import json
import threading
import schedule
import time
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from datetime import datetime, timedelta, timezone

from config import Config
from database_manager import init_db, save_message, get_recent_history
from cuncun_utils import (
    logger, upload_audio_v2, send_feishu, 
    match_voice_file, call_ai, 
    check_health, backup_database_task
)

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=3)
processed_ids = deque(maxlen=1000)

# --- Phase 1.3: 错误告警机制 ---
def send_error_alert(error_msg):
    """当系统逻辑崩溃时，第一时间给 likikyou 发送飞书提醒"""
    alert_text = f"⚠️ 【存存系统告警】\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n内容：{error_msg}"
    # 这里的 ADMIN_OPEN_ID 请在 .env 或 config.py 中配置为你自己的 open_id
    admin_id = getattr(Config, 'ADMIN_OPEN_ID', None)
    if admin_id:
        send_feishu(admin_id, "text", {"text": alert_text})
        logger.info("已发送错误告警至管理员")

# Prompt 提示词构建逻辑
def build_prompt(user_text):
    """构建带实时时间戳的提示词"""
    # 强制北京时间 (UTC+8)
    now = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(Config.PROMPT_PATH, "r", encoding="utf-8") as f:
            base = f.read().strip()
    except Exception as e:
        logger.warning(f"读取提示词失败: {e}")
        base = "我是存存，也可以叫我存宝。一个顶尖化妆师。"
        
    return f"{base}\n当前时间: {now}"

def core_logic(data):
    """核心处理逻辑，集成异常告警"""
    open_id = "未知"
    try:
        event = data.get("event", {})
        if event.get("message", {}).get("message_type") != "text": return
        
        user_text = json.loads(event["message"]["content"])["text"].strip()
        open_id = event["sender"]["sender_id"]["open_id"]
        
        # 使用结构化日志记录输入
        logger.info(f"📩 收到用户消息", extra={"user_text": user_text, "open_id": open_id})
        save_message(open_id, "user", user_text)
        
        prompt = build_prompt(user_text)
        history = get_recent_history(open_id, limit=6)
        
        # 记录调取历史的行为，取代 print
        logger.info(f"正在调取历史记忆", extra={"history_count": len(history)})
        
        reply = call_ai(prompt, user_text, history)
        
        # 长文本预热回复
        if len(user_text) > 50:
            notice = "喔唷，likikyou 今天写了这么多心里话呀，我正在认真读呢，稍微等我一下喔... ☕️"
            send_feishu(open_id, "text", {"text": notice})
        
        save_message(open_id, "assistant", reply)
        logger.info(f"💬 存存回复成功", extra={"reply_preview": reply[:30]})
        
        # 发送文本
        send_feishu(open_id, "text", {"text": reply})
        
        # 语音匹配与发送
        v_path = match_voice_file(reply)
        if v_path:
            f_key = upload_audio_v2(v_path)
            if f_key:
                send_feishu(open_id, "audio", {"file_key": f_key})

    except Exception as e:
        error_info = f"Core Logic Error: {str(e)}"
        logger.error(error_info, exc_info=True)
        # 触发告警，确保 likikyou 能收到推送
        send_error_alert(error_info)

@app.route("/", methods=["POST"])
def entry_point():
    # 1. 🛡️ 安全第一：先校验签名（Security）
    from cuncun_utils import verify_signature, AESCipher 
    if not verify_signature(request.headers, request.data):
        logger.warning("🚫 收到非法请求，签名校验失败")
        return jsonify({"code": 403, "msg": "invalid signature"}), 403

    # 获取原始 JSON 数据
    data = request.json
    
    # 2. 🔓 开启“拆箱”逻辑：如果消息被加密，则进行解密
    if data and "encrypt" in data:
        try:
            # 使用配置中的 ENCRYPT_KEY 进行解密
            cipher = AESCipher(Config.FEISHU_ENCRYPT_KEY)
            data = cipher.decrypt(data["encrypt"])
            # logger.info("🔓 消息解密成功")
        except Exception as e:
            logger.error(f"❌ 消息解密失败: {e}")
            return jsonify({"code": 500, "msg": "decryption failed"}), 500

    # 3. 处理业务逻辑 (此时 data 已经是明文 JSON)
    
    # 处理飞书的 URL 验证 (Challenge)
    if data and ("challenge" in data or data.get("type") == "url_verification"):
        return jsonify({"challenge": data.get("challenge")})
    
    # 消息排重 (使用解密后的 header)
    eid = data.get("header", {}).get("event_id")
    if not eid or eid in processed_ids: 
        return jsonify({})
    processed_ids.append(eid)
    
    
    # 4. 🚀 异步执行核心对话逻辑
    executor.submit(core_logic, data)
    
    # 注意：这里返回必须带 {}，代表成功接收
    return jsonify({})
# ------------------------------------------

@app.route("/health", methods=["GET"])
def health_check_endpoint():
    """健康检查接口"""
    status = check_health()
    code = 200 if status["status"] == "healthy" else 503
    return jsonify(status), code

# --- Phase 1.2: 定时任务执行器 ---
def run_scheduler():
    # 1. 每天凌晨 2 点备份
    schedule.every().day.at("02:00").do(backup_database_task)
    
    # 2. 每小时执行一次内部健康自检并记录日志
    schedule.every().hour.do(check_health)
    
    logger.info("⏰ 定时任务调度器已启动")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    init_db()
    
    # 启动后台调度线程
    threading.Thread(target=run_scheduler, daemon=True).start()
    
    port = getattr(Config, 'SERVER_PORT', getattr(Config, 'PORT', 8081))
    logger.info(f"🚀 存存 V2.2 启动成功: {port} (带告警与定时运维)")
    app.run(host='0.0.0.0', port=port, debug=False)

import json
import threading
import schedule
import time
import os
import lark_oapi as lark
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

# 引入飞书 SDK 的相关模块
from lark_oapi.client import Client
from lark_oapi.ws import Client as WSClient
from lark_oapi.service.im.v1 import P2pChatCreateEvent

from config import Config
from database_manager import init_db, save_message, get_recent_history
from cuncun_utils import (
    logger, upload_audio_v2, send_feishu, 
    match_voice_file, call_ai, 
    check_health, backup_database_task
)

# ----------------------------------------------------------------
# 全局配置与初始化
# ----------------------------------------------------------------
app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=3)

# ----------------------------------------------------------------
# 核心业务逻辑 (AI 大脑)
# ----------------------------------------------------------------

def send_error_alert(error_msg):
    """当系统逻辑崩溃时，第一时间给 likikyou 发送飞书提醒"""
    alert_text = f"⚠️ 【存存系统告警】\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n内容：{error_msg}"
    admin_id = getattr(Config, 'ADMIN_OPEN_ID', None)
    if admin_id:
        send_feishu(admin_id, "text", {"text": alert_text})
        logger.info("已发送错误告警至管理员")

def build_prompt(user_text):
    """构建带实时时间戳的提示词"""
    now = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(Config.PROMPT_PATH, "r", encoding="utf-8") as f:
            base = f.read().strip()
    except Exception as e:
        logger.warning(f"读取提示词失败: {e}")
        base = "我是存存，也可以叫我存宝。一个顶尖化妆师。"
    return f"{base}\n当前时间: {now}"

def process_message_task(open_id, user_text):
    """
    具体的任务执行函数，放入线程池运行
    """
    try:
        # 使用结构化日志记录输入
        logger.info(f"📩 收到用户消息 (长连接)", extra={"user_text": user_text, "open_id": open_id})
        save_message(open_id, "user", user_text)
        
        prompt = build_prompt(user_text)
        history = get_recent_history(open_id, limit=6)
        
        logger.info(f"正在调取历史记忆", extra={"history_count": len(history)})
        
        reply = call_ai(prompt, user_text, history)
        
        # 长文本预热回复
        if len(user_text) > 50:
            notice = "喔唷，今天写了这么多心里话呀，我正在认真读呢，稍微等我一下喔... ☕️"
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
        send_error_alert(error_info)

# ----------------------------------------------------------------
# 飞书 SDK 长连接处理器
# ----------------------------------------------------------------

def do_p2p_chat_create(data: P2pChatCreateEvent, option: lark.EventHandlerOption = None):
    """
    飞书 SDK 的回调函数。当收到私聊消息时，SDK 会自动调用这个函数。
    """
    # 1. 解析 SDK 对象中的数据
    try:
        event = data.event
        sender_id = event.sender.sender_id.open_id
        content_json = event.message.content
        msg_type = event.message.message_type
        
        # 2. 这里的 content 是一个 JSON 字符串，需要解析
        content_dict = json.loads(content_json)
        
        if msg_type != "text":
            logger.info("收到非文本消息，跳过处理")
            return
            
        user_text = content_dict.get("text", "").strip()
        
        # 3. 扔进线程池异步处理，不阻塞 SDK 的长连接心跳
        executor.submit(process_message_task, sender_id, user_text)
        
    except Exception as e:
        logger.error(f"SDK 数据解析失败: {e}", exc_info=True)

# ----------------------------------------------------------------
# 辅助服务 (健康检查 & 定时任务)
# ----------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health_check_endpoint():
    """保留健康检查接口，方便本地查看"""
    status = check_health()
    code = 200 if status["status"] == "healthy" else 503
    return jsonify(status), code

def run_scheduler():
    schedule.every().day.at("02:00").do(backup_database_task)
    schedule.every().hour.do(check_health)
    logger.info("⏰ 定时任务调度器已启动")
    while True:
        schedule.run_pending()
        time.sleep(60)

def run_flask_app():
    """在独立线程中运行 Flask，仅用于 Health Check"""
    port = getattr(Config, 'SERVER_PORT', getattr(Config, 'PORT', 8081))
    # use_reloader=False 防止在线程中二次启动
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ----------------------------------------------------------------
# 主程序入口
# ----------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    
    # 1. 启动定时任务 (后台线程)
    threading.Thread(target=run_scheduler, daemon=True).start()
    
    # 2. 启动 Flask 健康检查服务 (后台线程)
    # 这样你依然可以访问 http://localhost:8081/health
    threading.Thread(target=run_flask_app, daemon=True).start()
    
    # 3. 启动飞书长连接 (主进程阻塞运行)
    app_id = getattr(Config, 'FEISHU_APP_ID', os.getenv("FEISHU_APP_ID"))
    app_secret = getattr(Config, 'FEISHU_APP_SECRET', os.getenv("FEISHU_APP_SECRET"))
    
    if not app_id or not app_secret:
        logger.error("❌ 启动失败：未配置 FEISHU_APP_ID 或 FEISHU_APP_SECRET")
        exit(1)

    # 注册事件处理器
    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2p_chat_create_event(do_p2p_chat_create) \
        .build()

    # 创建并启动长连接客户端
    logger.info("🔗 正在建立飞书长连接 (WebSocket)...")
    ws_client = WSClient.builder(app_id, app_secret) \
        .event_handler(event_handler) \
        .build()

    try:
        # start() 是阻塞的，会一直运行直到按 Ctrl+C
        ws_client.start()
    except Exception as e:
        logger.error(f"❌ 长连接断开或启动失败: {e}")
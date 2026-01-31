import os
import json
import time
import requests
import logging
import hashlib
import hmac
import re
import base64
import shutil
import chromadb
from openai import OpenAI
from datetime import datetime, timedelta
from pythonjsonlogger import jsonlogger  #
from config import Config
from Crypto.Cipher import AES

# --- 1. 初始化结构化日志系统 ---

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, created, message):
        super().add_fields(log_record, created, message)
        log_record['timestamp'] = datetime.now().isoformat()
        # 修正：直接获取标准 levelname，如果不存在则默认为 INFO
        log_record['level'] = log_record.get('levelname', 'INFO')
        log_record['service'] = 'feishu-cuncun-pro'

def setup_logging():
    os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
    
    # 文件处理器 (持久化存储)
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    # 屏幕处理器 (用于 pm2 logs 查看)
    stream_handler = logging.StreamHandler()
    
    # 应用 JSON 格式化
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    _logger = logging.getLogger("feishu-utils")
    _logger.handlers = []  # 清空旧处理器，防止重复打印
    _logger.addHandler(file_handler)
    _logger.addHandler(stream_handler)
    _logger.setLevel(logging.INFO)
    return _logger

logger = setup_logging()

# --- 飞书签名校验：防止非法消耗 API 额度 ---
import hashlib
# import hmac  <-- 这一行可以删掉或注释掉

import hashlib

def verify_signature(request_headers, request_body):
    """
    🛡️ 飞书签名校验 (兼容模式)
    如果没有配置 FEISHU_ENCRYPT_KEY，则直接放行，方便调试。
    """
    # 1. 尝试获取 Key，如果没配或是被注释掉了，直接返回 True
    encrypt_key = getattr(Config, 'FEISHU_ENCRYPT_KEY', None)
    if not encrypt_key:
        return True 

    # 2. 获取飞书传来的安全头信息
    timestamp = request_headers.get("X-Lark-Request-Timestamp")
    nonce = request_headers.get("X-Lark-Request-Nonce")
    signature = request_headers.get("X-Lark-Signature")
    
    if not all([timestamp, nonce, signature]):
        return False

    # 3. 按照标准 SHA-256 算法比对
    try:
        content = (timestamp + nonce + encrypt_key).encode('utf-8') + request_body
        local_sig = hashlib.sha256(content).hexdigest()
        
        if local_sig == signature:
            return True
        else:
            logger.warning(f"签名不匹配! 远程:{signature[:8]}... 本地:{local_sig[:8]}...")
            return False
    except Exception as e:
        logger.error(f"签名校验异常: {e}")
        return False
    # ... 后续的加密比对逻辑 ...

# --- 2. 初始化客户端 ---
try:
    client = OpenAI(api_key=Config.DEEPSEEK_KEY, base_url="https://api.deepseek.com")
except Exception as e:
    logger.error(f"AI客户端初始化失败: {e}")
    client = None

# --- 3. 初始化向量库 ---
voice_collection = None
bio_collection = None
try:
    if os.path.exists(Config.ASSETS_PATH):
        client_assets = chromadb.PersistentClient(path=Config.ASSETS_PATH)
        voice_collection = client_assets.get_collection(name="cuncun_voice")
    if os.path.exists(Config.MEMORY_PATH):
        client_memory = chromadb.PersistentClient(path=Config.MEMORY_PATH)
        bio_collection = client_memory.get_or_create_collection(name="cuncun_bio")
except Exception as e:
    logger.warning(f"向量库加载警告: {e}")

# --- 核心功能函数 ---

_token_cache = {"token": None, "expires_at": 0}

def get_token():
    """获取 Token (带缓存)"""
    current_time = time.time()
    if _token_cache["token"] and current_time < _token_cache["expires_at"] - 300:
        return _token_cache["token"]
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        r = requests.post(url, json={
            "app_id": Config.FEISHU_APP_ID, 
            "app_secret": Config.FEISHU_APP_SECRET
        }, timeout=10)
        data = r.json()
        token = data.get("tenant_access_token")
        if token:
            _token_cache["token"] = token
            _token_cache["expires_at"] = current_time + data.get("expire", 7200)
            return token
    except Exception as e:
        logger.error(f"Token获取异常: {e}")
    return None

def upload_audio_v2(file_path):
    """协议逆向版：使用 'file' 字段名"""
    token = get_token()
    if not token or not os.path.exists(file_path): return None
    
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    filename = os.path.basename(file_path)
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'file_type': (None, 'opus'),
                'file_name': (None, filename),
                'file': (filename, f.read(), 'application/octet-stream')
            }
            r = requests.post(url, headers=headers, files=files, timeout=20)
            res = r.json()
            if res.get("code") == 0:
                logger.info(f"✅ 上传成功 Key: {res['data']['file_key']}")
                return res['data']['file_key']
            else:
                logger.error(f"❌ 上传失败: {res}")
                return None
    except Exception as e:
        logger.error(f"上传异常: {e}")
        return None

def send_feishu(receive_id, msg_type, content):
    """通用发送函数"""
    token = get_token()
    if not token: return False
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json={
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": json.dumps(content)
        }, timeout=10)
        return r.json().get("code") == 0
    except Exception as e:
        logger.error(f"发送飞书消息失败: {e}")
        return False

def get_embedding(text):
    if not Config.SILICONFLOW_API_KEY: return None
    try:
        url = "https://api.siliconflow.cn/v1/embeddings"
        headers = {"Authorization": f"Bearer {Config.SILICONFLOW_API_KEY}", "Content-Type": "application/json"}
        r = requests.post(url, json={"model": "BAAI/bge-large-zh-v1.5", "input": text}, headers=headers, timeout=10)
        return r.json()["data"][0]["embedding"] if r.status_code == 200 else None
    except Exception as e:
        logger.error(f"向量获取失败: {e}")
        return None
        
# --- 最终优化后的语音匹配逻辑 ---
def match_voice_file(text):
    if not voice_collection: 
        return None
    
    # 1. 彻底清洗文本：去掉所有形式的动作标签和旁白
    # 覆盖：[ ] , ( ) , （ ）, 【 】
    clean_text = re.sub(r"\[.*?\]|（.*?）|\(.*?\)|【.*?】", "", text).strip()
    
    # 2. 分句处理：增加对“...”和“..”这种口语化省略号的处理
    # 这样可以避免把“哈？你那些设计稿...” 这种长句直接送去匹配
    sentences = re.split(r'[。！？！?，,；; \n]|[.]{2,}', clean_text)
    # 过滤掉空格和长度小于 2 的片段（如“哈”、“嗯”），除非库里有很多这种短音
    sentences = [s.strip() for s in sentences if len(s.strip()) > 1] 
    
    if not sentences:
        logger.warning(f"⚠️ 清洗后无有效分句: {text[:20]}...")
        return None

    logger.info(f"🔍 开启分句检索，片段总数: {len(sentences)}")

    try:
        for sentence in sentences:
            # 这里的 get_embedding 建议使用你现有的 768 维模型
            vec = get_embedding(sentence)
            if not vec: continue
            
            # 3. 搜索最匹配的 1 条结果
            res = voice_collection.query(query_embeddings=[vec], n_results=1)
            
            if res["distances"] and len(res["distances"][0]) > 0:
                distance = res["distances"][0][0]
                
                # 4. 阈值设定为 0.48
                # 日志显示你的成功案例在 0.41 附近，0.4 能大幅提升“设计稿”这类句子的匹配可能
                if distance < 0.48: 
                    matched_filename = res["metadatas"][0][0]["filename"]
                    logger.info(f"✨ 匹配命中! [{sentence}] -> {matched_filename} (距离: {distance:.4f})")
                    return os.path.join(Config.VOICE_LIB, matched_filename)
                else:
                    logger.info(f"⏭️ 片段 [{sentence}] 最接近距离为 {distance:.4f}，未达标")
                
        logger.warning("❌ 所有分句均匹配失败")
        
    except Exception as e:
        logger.error(f"语音匹配过程发生异常: {e}", exc_info=True)
        
    return None

def call_ai(system_prompt, user_text, history=[]):
    if not client: return "AI 未连接"
    try:
        start_time = time.time()
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_text}],
            temperature=0.9,
            max_tokens=2048,
            presence_penalty=0.6,
            frequency_penalty=0.5
        )
        duration = time.time() - start_time
        logger.info(f"AI 响应成功", extra={"duration": round(duration, 2)}) #
        return res.choices[0].message.content
    except Exception as e:
        logger.error(f"AI 错误: {e}")
        return "我有点累了，稍等一下。"

# --- 运维功能 ---

def check_health():
    """健康检查"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "ai": client is not None,
            "voice_db": voice_collection is not None,
            "feishu_api": get_token() is not None
        }
    }
    logger.info("执行健康检查", extra={"health_data": health_data})
    return health_data

def backup_database_task():
    """数据库备份"""
    try:
        if not os.path.exists(Config.BACKUP_DIR):
            os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(Config.BACKUP_DIR, f"backup_{timestamp}.db")
        
        shutil.copy2(Config.DB_PATH, backup_path)
        logger.info(f"💾 数据库备份成功", extra={"backup_file": os.path.basename(backup_path)})
        
        # 清理旧备份 (保留7天)
        retention = time.time() - (7 * 86400)
        for f in os.listdir(Config.BACKUP_DIR):
            fp = os.path.join(Config.BACKUP_DIR, f)
            if os.path.getmtime(fp) < retention:
                os.remove(fp)
                logger.info(f"清理过期备份", extra={"removed_file": f})
    except Exception as e:
        logger.error(f"备份失败: {e}")

class AESCipher:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode('utf-8')).digest()

    def decrypt(self, encrypt_text):
        encrypt_bytes = base64.b64decode(encrypt_text)
        iv = encrypt_bytes[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_bytes = cipher.decrypt(encrypt_bytes[16:])
        # 移除 PKCS7 填充
        padding_len = decrypted_bytes[-1]
        decrypted_json = decrypted_bytes[:-padding_len].decode('utf-8')
        return json.loads(decrypted_json)
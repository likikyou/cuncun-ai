import os
from dotenv import load_dotenv

# 自动加载当前目录下的 .env 文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    # --- 1. 🔴 飞书平台配置 (必需) ---
    # 用于身份验证和 API 调用
    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
    
    # 用于回调安全校验 (Phase 1.1)
    FEISHU_VERIFY_TOKEN = os.getenv("FEISHU_VERIFY_TOKEN")
        # Encrypt Key加密策略开启后可解锁下方内容
    FEISHU_ENCRYPT_KEY = os.getenv("FEISHU_ENCRYPT_KEY")

    # --- 2. 🧠 AI 模型配置 ---
    # DeepSeek 大脑
    DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
    # 硅基流动 (用于 Embedding 向量化)
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")

    # --- 3. 🛣️ 路径配置 (分布式架构) ---
    BASE_DIR = BASE_DIR
    
    # 核心记忆数据库 (SQLite)
    DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "AI_banlu_cuncun_memory.db"))
    
    # 提示词与静态资产
    PROMPT_PATH = os.getenv("PROMPT_PATH", os.path.join(BASE_DIR, "prompt_template.txt"))
    ASSETS_PATH = os.getenv("ASSETS_PATH", os.path.join(BASE_DIR, "音频数据", "cuncun_assets_db"))
    VOICE_LIB = os.getenv("VOICE_LIB", os.path.join(BASE_DIR, "音频数据", "CunCun_Opus_Library"))
    MEMORY_PATH = os.getenv("MEMORY_PATH", os.path.join(BASE_DIR, "cuncun_memory_db"))

    # --- 4. 🛡️ 运维配置 (Phase 1 新增) ---
    # 结构化日志路径
    LOG_FILE = os.getenv("LOG_FILE", os.path.join(BASE_DIR, "logs", "feishu-cuncun.log"))
    
    # 数据库自动备份目录
    BACKUP_DIR = os.getenv("BACKUP_DIR", os.path.join(BASE_DIR, "backups"))
    
    # 管理员 Open ID (用于接收系统崩溃告警)
    ADMIN_OPEN_ID = os.getenv("ADMIN_OPEN_ID")
    
    # 服务端口
    SERVER_PORT = int(os.getenv("PORT", 8081))
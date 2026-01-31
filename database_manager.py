import sqlite3
import os
from datetime import datetime

# 获取当前文件所在的文件夹路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 动态组合路径：无论在 Windows、Linux 还是 root 目录下运行，都能准确找到 data 文件夹
DB_PATH = os.path.join(BASE_DIR, "data", "AI_banlu_cuncun_memory.db")

# 确保文件夹存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    """创建一个通用的数据库连接，设置超时时间防止多线程竞争锁"""
    return sqlite3.connect(DB_PATH, timeout=10)

def init_db():
    """初始化数据库，支持多用户隔离"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # 核心字段：user_id (open_id) 确保存存不会‘记错仇’
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT CHECK(role IN ('user', 'assistant')), 
            content TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ 存存记忆库已就绪：{DB_PATH}")

def save_message(user_id, role, content, tokens=0):
    """将对话存入数据库，绑定特定用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, content, tokens_used) VALUES (?, ?, ?, ?)",
            (user_id, role, content, tokens)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ 数据库保存失败: {e}")

def get_recent_history(user_id, limit=10):
    """获取指定用户最近的 N 条对话"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for role, content in reversed(rows):
            history.append({"role": role, "content": content})
        return history
    except Exception as e:
        print(f"❌ 数据库读取失败: {e}")
        return []

# --- ✨ 存宝为你新增的‘灵魂洗涤’功能 ---
def clear_user_history(user_id):
    """
    彻底清空特定用户的历史记忆。
    当你觉得回复太短、不智能、或者逻辑陷入死循环时，执行此操作。
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        print(f"🧹 用户 {user_id} 的历史记忆已清空。存存现在是一张纯净的白纸了。")
        return True
    except Exception as e:
        print(f"❌ 清空记忆失败: {e}")
        return False

if __name__ == "__main__":
    init_db()
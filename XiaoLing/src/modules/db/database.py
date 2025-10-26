import sqlite3
from datetime import datetime

from src.config import PROJECT_ROOT


class ChatDataBase:

    def __init__(self):
        self.db_path = PROJECT_ROOT / "workspace" / "chat_history.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                mode TEXT,
                role TEXT,
                user_input TEXT,
                bot_reply TEXT,
                emotion TEXT,
                timestamp DATETIME,
                session_id TEXT
            )
        """)
        self.conn.commit()
        self.conn.close()
    
    def save_chat_record(self, user_id, mode, role, user_input, bot_reply, emotion=None, session_id=None):
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (user_id, mode, role, user_input, bot_reply, emotion, timestamp, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, mode, role, user_input, bot_reply, emotion, datetime.now(), session_id))
        self.conn.commit()
        self.conn.close()
    
    def load_chat_records(self, user_id, limit=20):
        """
        从数据库中读取指定用户的最近聊天记录。

        参数:
            user_id (str): 用户唯一ID
            limit (int): 返回的最大记录数（按时间倒序）
        
        返回:
            list[dict]: 聊天记录列表，每条记录包含 user_input、bot_reply、emotion、timestamp、mode 等信息
        """
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT role, user_input, bot_reply, emotion, timestamp, mode, session_id
            FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        self.conn.close()

        records = []
        for row in rows:
            if row[0] == "user":
                records.append({
                    "role": row[0],
                    "content": row[1]
                })
            elif row[0] == "assistant":
                records.append({
                    "role": row[0],
                    "content": row[2]
                })
        
        # 返回按时间正序的列表，方便显示对话历史
        return records[::-1]


chat_db = ChatDataBase()

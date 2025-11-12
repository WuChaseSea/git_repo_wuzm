import sqlite3
from datetime import datetime

from src.config import PROJECT_ROOT


class ContentBase:

    def __init__(self):
        self.db_path = PROJECT_ROOT / "workspace" / "content.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                mode TEXT,
                role TEXT,
                emotion TEXT,
                content TEXT,
                timestamp DATETIME,
                session_id TEXT
            )
        """)
        self.conn.commit()
        self.conn.close()
    
    def save_content_record(self, user_id, mode, role, content, emotion=None, session_id=None):
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO contents (user_id, mode, role, content, emotion, timestamp, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, mode, role, content, emotion, datetime.now(), session_id))
        self.conn.commit()
        self.conn.close()
    
    def load_content_records(self, user_id, limit=20):
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
            SELECT role, content, emotion, timestamp, mode, session_id
            FROM contents
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


content_db = ContentBase()

import sqlite3
from datetime import datetime

from src.config import PROJECT_ROOT


class EmotionBase:

    def __init__(self):
        self.db_path = PROJECT_ROOT / "workspace" / "emotion.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS emotion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                score REAL,              -- 数值情绪值，范围建议 -1 ~ +1
                emotion_label TEXT,      -- 情绪类型，如 sad, stress, calm, happy
                text TEXT,               -- 该条用户文本内容
                timestamp DATETIME       -- 记录时间
            )
        """)
        self.conn.commit()
        self.conn.close()
    
    def save_emotion_record(self, user_id, text, score, emotion_label):
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO emotion_history (user_id, text, score, emotion_label, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, text, score, emotion_label, datetime.now()))
        self.conn.commit()
        self.conn.close()
    
    def get_last_week_emotion(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, score FROM emotion_history
            WHERE user_id = ?
            AND timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp ASC
        """, (user_id,))
        data = cur.fetchall()
        conn.close()
        return data  # [(timestamp, score), ...]


emotion_db = EmotionBase()

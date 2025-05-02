# database/models.py - 数据库模型定义

import sqlite3
from utils.logger import logger

def init_database(db_path):
    """初始化SQLite数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        first_seen TIMESTAMP,
        last_interaction TIMESTAMP
    )
    ''')
    
    # 创建交互记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP,
        bot_id TEXT,
        user_message TEXT,
        bot_response TEXT,
        processing_time REAL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # 创建分析统计表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date DATE,
        total_messages INTEGER,
        total_characters INTEGER,
        avg_response_time REAL,
        most_used_bot TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")

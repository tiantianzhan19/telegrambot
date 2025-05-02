# database/operations.py - 数据库操作函数

import sqlite3
from datetime import datetime
from config import DB_PATH
from utils.logger import logger

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def record_user(user_id, username, first_name, last_name):
    """记录或更新用户信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查用户是否已存在
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if result is None:
        # 新用户，添加记录
        cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_name, first_seen, last_interaction)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, current_time, current_time))
        logger.info(f"新用户记录: {user_id}, {username}")
    else:
        # 更新现有用户的最后交互时间
        cursor.execute('''
        UPDATE users SET username = ?, first_name = ?, last_name = ?, last_interaction = ?
        WHERE user_id = ?
        ''', (username, first_name, last_name, current_time, user_id))
    
    conn.commit()
    conn.close()

def record_interaction(user_id, bot_id, user_message, bot_response, processing_time):
    """记录用户与机器人的交互"""
    conn = get_connection()
    cursor = conn.cursor()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
    INSERT INTO interactions (user_id, timestamp, bot_id, user_message, bot_response, processing_time)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, current_time, bot_id, user_message, bot_response, processing_time))
    
    conn.commit()
    conn.close()

def update_analytics(user_id, bot_id, processing_time):
    """更新用户分析数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 检查今天的记录是否存在
    cursor.execute("SELECT * FROM analytics WHERE user_id = ? AND date = ?", (user_id, current_date))
    result = cursor.fetchone()
    
    if result is None:
        # 今天没有记录，创建新记录
        cursor.execute('''
        INSERT INTO analytics (user_id, date, total_messages, total_characters, avg_response_time, most_used_bot)
        VALUES (?, ?, 1, 0, ?, ?)
        ''', (user_id, current_date, processing_time, bot_id))
    else:
        # 更新现有记录
        analytics_id, _, _, total_messages, total_chars, avg_time, most_used = result
        
        # 获取今天该用户使用的所有机器人
        cursor.execute('''
        SELECT bot_id, COUNT(*) as count FROM interactions 
        WHERE user_id = ? AND date(timestamp) = ? 
        GROUP BY bot_id ORDER BY count DESC LIMIT 1
        ''', (user_id, current_date))
        bot_result = cursor.fetchone()
        
        most_used_bot = bot_result[0] if bot_result else most_used
        
        # 计算新的平均响应时间
        new_avg_time = ((avg_time * total_messages) + processing_time) / (total_messages + 1)
        
        cursor.execute('''
        UPDATE analytics SET 
        total_messages = total_messages + 1,
        avg_response_time = ?,
        most_used_bot = ?
        WHERE id = ?
        ''', (new_avg_time, most_used_bot, analytics_id))
    
    conn.commit()
    conn.close()

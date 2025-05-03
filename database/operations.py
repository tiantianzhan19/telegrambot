import sqlite3
from datetime import datetime
from config import DB_PATH
from utils.logger import logger

def get_connection():
    """
    返回 SQLite 数据库连接对象。
    """
    return sqlite3.connect(DB_PATH)


def record_user(user_id, username, first_name, last_name):
    """
    插入或更新用户信息：
      - 首次见：创建记录并设置首次/最后交互时间
      - 再次见：更新用户名、姓名和最后交互时间
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
    )
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, last_name, first_seen, last_interaction)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, first_name, last_name, now, now)
        )
        logger.info(f"Registered new user: {user_id} ({username})")
    else:
        cursor.execute(
            "UPDATE users SET username = ?, first_name = ?, last_name = ?, last_interaction = ?"
            " WHERE user_id = ?",
            (username, first_name, last_name, now, user_id)
        )

    conn.commit()
    conn.close()


def record_interaction(user_id, bot_id, user_message, bot_response, processing_time):
    """
    插入用户-机器人交互记录：
      - 字段涵盖用户、时间戳、机器人ID、消息内容与处理时长
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO interactions (user_id, timestamp, bot_id, user_message, bot_response, processing_time)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, now, bot_id, user_message, bot_response, processing_time)
    )
    conn.commit()
    conn.close()


def update_analytics(user_id, bot_id, processing_time):
    """
    累积更新分析表：
      - 若当天无记录：初始化消息计数与平均响应时间
      - 已有记录：累加消息数，重算平均响应，更新最常使用机器人
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT id, total_messages, avg_response_time, most_used_bot FROM analytics"
        " WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO analytics (user_id, date, total_messages, avg_response_time, most_used_bot)"
            " VALUES (?, ?, 1, ?, ?)",
            (user_id, today, processing_time, bot_id)
        )
    else:
        analytics_id, total_msgs, avg_time, prev_bot = row
        # 统计今日最频繁机器人
        cursor.execute(
            "SELECT bot_id, COUNT(*) FROM interactions"
            " WHERE user_id = ? AND date(timestamp) = ?"
            " GROUP BY bot_id ORDER BY COUNT(*) DESC LIMIT 1",
            (user_id, today)
        )
        most_used = cursor.fetchone()
        top_bot = most_used[0] if most_used else prev_bot
        # 更新平均响应时间
        new_avg = ((avg_time * total_msgs) + processing_time) / (total_msgs + 1)
        cursor.execute(
            "UPDATE analytics SET total_messages = ?, avg_response_time = ?, most_used_bot = ?"
            " WHERE id = ?",
            (total_msgs + 1, new_avg, top_bot, analytics_id)
        )

    conn.commit()
    conn.close()

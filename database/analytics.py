import os
import pandas as pd
from datetime import datetime
from database.operations import get_connection
from utils.logger import logger

def get_stats_summary():
    """
    查询并汇总关键统计指标：
      - total_users: 注册用户总数
      - active_users_today: 当日活跃用户数
      - total_interactions: 累计交互次数
      - bot_usage: 各机器人使用频次排行
      - avg_response_time: 平均处理时长（秒）
    返回包含上述指标的字典。
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 注册用户总数
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # 当日活跃用户数
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT COUNT(DISTINCT user_id) FROM interactions WHERE date(timestamp) = ?",
        (today,)
    )
    active_users_today = cursor.fetchone()[0]

    # 累计交互次数
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]

    # 各机器人使用频次排行
    cursor.execute(
        "SELECT bot_id, COUNT(*) AS count FROM interactions GROUP BY bot_id ORDER BY count DESC"
    )
    bot_usage = cursor.fetchall()

    # 平均处理时长
    cursor.execute("SELECT AVG(processing_time) FROM interactions")
    avg_response_time = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_users": total_users,
        "active_users_today": active_users_today,
        "total_interactions": total_interactions,
        "bot_usage": bot_usage,
        "avg_response_time": avg_response_time
    }


def export_interactions_to_csv():
    """
    导出所有交互记录至 CSV：
      - 字段：user_id, username, first_name, timestamp, bot_id, user_message, bot_response, processing_time
      - 文件名：interactions_export_YYYYMMDD_HHMMSS.csv
    成功返回文件名，失败返回 None。
    """
    try:
        conn = get_connection()
        query = (
            "SELECT i.user_id, u.username, u.first_name, i.timestamp, i.bot_id, "
            "i.user_message, i.bot_response, i.processing_time "
            "FROM interactions i "
            "JOIN users u ON i.user_id = u.user_id "
            "ORDER BY i.timestamp DESC"
        )
        interactions_df = pd.read_sql_query(query, conn)

        filename = f"interactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        interactions_df.to_csv(filename, index=False)
        conn.close()
        return filename
    except Exception as e:
        logger.error(f"导出 CSV 失败: {e}")
        return None
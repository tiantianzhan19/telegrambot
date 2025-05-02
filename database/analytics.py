# database/analytics.py - 数据分析和导出功能

import os
import pandas as pd
from datetime import datetime
from database.operations import get_connection
from utils.logger import logger

def get_stats_summary():
    """获取统计摘要数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 总用户数
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # 今日活跃用户数
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
    SELECT COUNT(DISTINCT user_id) FROM interactions 
    WHERE date(timestamp) = ?
    ''', (today,))
    active_users_today = cursor.fetchone()[0]
    
    # 总交互次数
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]
    
    # 每个机器人的使用次数
    cursor.execute('''
    SELECT bot_id, COUNT(*) as count FROM interactions 
    GROUP BY bot_id ORDER BY count DESC
    ''')
    bot_usage = cursor.fetchall()
    
    # 平均响应时间
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
    """导出交互数据为CSV文件"""
    try:
        conn = get_connection()
        
        # 导出交互记录
        interactions_df = pd.read_sql_query('''
        SELECT i.user_id, u.username, u.first_name, i.timestamp, i.bot_id, 
               i.user_message, i.bot_response, i.processing_time
        FROM interactions i
        JOIN users u ON i.user_id = u.user_id
        ORDER BY i.timestamp DESC
        ''', conn)
        
        # 保存到CSV
        csv_filename = f"interactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        interactions_df.to_csv(csv_filename, index=False)
        
        conn.close()
        return csv_filename
    except Exception as e:
        logger.error(f"导出数据失败: {e}")
        return None

# config.py - 配置文件
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")


# 数据库设置
DB_PATH = "bot_interactions.db"

# 管理员设置
ADMIN_IDS = [8079573322]  # 替换为您的 Telegram 用户 ID

# OpenAI 设置
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7

# 机器人设置
MAX_HISTORY_LENGTH = 10  # 存储的最大对话历史条数

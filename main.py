# main.py

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.commands import start, help_command, clear_command     # ← 加入 clear_command
from bot.handlers import handle_message
from database.models import init_database
from config import TELEGRAM_TOKEN, DB_PATH

def main() -> None:
    init_database(DB_PATH)
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help",  help_command))
    application.add_handler(CommandHandler("clear", clear_command))  # ← 注册 /clear
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("机器人已启动……")
    application.run_polling()

if __name__ == "__main__":
    main()

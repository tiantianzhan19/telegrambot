# bot/commands.py
"""
只保留 /start 和 /help 命令
"""
from telegram import Update
from telegram.ext import ContextTypes
from database.operations import record_user
from bot.personalities import BOT_PERSONALITY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令"""
    user = update.message.from_user
    record_user(user.id, user.username, user.first_name, user.last_name)
    context.user_data['history'] = []
    await update.message.reply_text(
        f"👋 你好 {user.first_name}！我是{BOT_PERSONALITY['emoji']} {BOT_PERSONALITY['name']}，很高兴和你聊天！"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /help 命令"""
    user = update.message.from_user
    record_user(user.id, user.username, user.first_name, user.last_name)

    help_text = (
        "📖 <b>使用指南</b>\n\n"
        "可用命令:\n"
        "/start  - 开始对话\n"
        "/help   - 查看帮助\n"
        "/clear  - 清除对话历史\n\n"
        f"当前人格: {BOT_PERSONALITY['emoji']} {BOT_PERSONALITY['name']}"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

    
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /clear 命令：清除当前对话上下文（history、stage、task），
    但后端数据库的所有记录依然保留。
    """
    user = update.message.from_user
    # 记录命令使用日志
    record_user(user.id, user.username, user.first_name, user.last_name)

    # 清空对话状态
    context.user_data.pop("history", None)
    context.user_data.pop("stage",    None)
    context.user_data.pop("task",     None)
    # 如果你还存了别的，比如 asked_name 或 user_name，也一并清掉：
    context.user_data.pop("asked_name", None)
    context.user_data.pop("user_name",  None)

    await update.message.reply_text("🔄 对话已清除，已重置为初始状态。我们重新开始吧！")   
# bot/commands.py

from telegram import Update
from telegram.ext import ContextTypes
from database.operations import record_user
from bot.personalities import BOT_PERSONALITY
from utils.openai_client import openai_client
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE

async def detect_user_name(text: str) -> str:
    """
    调用 GPT 从任意中文表达中提取用户姓名，未识别时返回空字符串。
    """
    response = await openai_client.chat_completion(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个简洁的助手，仅需从用户的中文表达中提取姓名，"
                    "如果无法识别合理的姓名，则返回空字符串。"
                )
            },
            {"role": "user", "content": f"请从这句话中提取用户的姓名：{text}"}
        ],
        temperature=DEFAULT_TEMPERATURE,
    )
    return response.strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start：记录用户，初始化会话，并智能欢迎。
    如果用户在 /start 附带文本中自报姓名，则优先使用该姓名。
    """
    user = update.message.from_user
    record_user(user.id, user.username, user.first_name, user.last_name)

    # 初始化对话历史
    context.user_data['history'] = []

    # 尝试从启动命令中的附加文本识别姓名
    raw_text = update.message.text or ""
    name = await detect_user_name(raw_text)
    if name:
        context.user_data['user_name'] = name
        welcome = f"👋 你好，{name}！"
    else:
        welcome = f"👋 你好，{user.first_name}！"

    await update.message.reply_text(
        f"{welcome} 我是 {BOT_PERSONALITY['emoji']} {BOT_PERSONALITY['name']}，很高兴和你聊天！"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /help：展示可用命令及当前人格。
    """
    user = update.message.from_user
    record_user(user.id, user.username, user.first_name, user.last_name)

    help_text = (
        "📖 <b>使用指南</b>\n\n"
        "/start  - 启动并欢迎\n"
        "/help   - 查看帮助\n"
        "/clear  - 重置对话\n\n"
        f"当前人格：{BOT_PERSONALITY['emoji']} {BOT_PERSONALITY['name']}"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /clear：清除上下文状态，保留后端记录。
    """
    user = update.message.from_user
    record_user(user.id, user.username, user.first_name, user.last_name)

    # 重置对话上下文
    for key in ("history", "stage", "task", "asked_name", "user_name"):
        context.user_data.pop(key, None)

    await update.message.reply_text("🔄 对话已重置到初始状态！")

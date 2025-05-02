# bot/keyboards.py - 内联键盘和按钮

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.personalities import BOT_PERSONALITIES

def get_bot_selection_keyboard():
    """创建机器人选择菜单的内联键盘"""
    keyboard = []
    
    # 添加机器人选择按钮
    for bot_id, bot_info in BOT_PERSONALITIES.items():
        keyboard.append([InlineKeyboardButton(
            f"{bot_info['emoji']} {bot_info['name']} ({bot_id})", 
            callback_data=f'select_{bot_id}'
        )])
    
    # 添加功能按钮
    keyboard.append([
        InlineKeyboardButton("🔄 重置对话", callback_data='reset_history'),
        InlineKeyboardButton("❓ 帮助", callback_data='help')
    ])
    
    return InlineKeyboardMarkup(keyboard)

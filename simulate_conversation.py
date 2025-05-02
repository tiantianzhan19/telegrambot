# simulate_conversation.py
"""
按 Excel 驱动对话模拟脚本
"""
import pandas as pd
from bot.personalities import BOT_PERSONALITY
from utils.openai_client import get_ai_response


def simulate():
    df = pd.read_excel('procrastination_conversations.xlsx')
    history = []
    for _, row in df[df['sender'] == 'User'].iterrows():
        user_text = row['content']
        # 构建消息
        messages = [{"role": "system", "content": BOT_PERSONALITY['personality'] }]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})
        # 调用 GPT
        response = get_ai_response(messages)
        # 输出
        print(f"User: {user_text}")
        print(f"{BOT_PERSONALITY['emoji']} {BOT_PERSONALITY['name']}: {response}\n")
        # 更新历史
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    simulate()

# utils/openai_client.py - OpenAI API交互

import openai
from config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE

# 初始化OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(messages, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE):
    """
    获取AI响应
    
    Args:
        messages: 消息列表
        model: 使用的模型名称
        temperature: 温度参数
        
    Returns:
        AI生成的回复文本
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    
    return response.choices[0].message.content

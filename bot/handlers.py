import re
import json
import time
from telegram import Update
from telegram.ext import ContextTypes
from bot.personalities import BOT_PERSONALITY
from database.operations import record_user, record_interaction, update_analytics
from utils.openai_client import get_ai_response
from utils.logger import logger
from config import MAX_HISTORY_LENGTH

# 多阶段对话逻辑描述，用于构建系统提示
STAGE_DESCRIPTIONS = {
    "1": "问候 & 任务确认：收集任务描述",
    "2": "任务拆解 & 计划制定：分解并设定时间",
    "3": "执行监控：追踪进度与困难",
    "4": "智能辅导 & 鼓励：提供策略或鼓励",
    "5": "完成 & 新任务：庆祝完成并询问"
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    核心消息处理：
      1. 引导并识别用户姓名
      2. 构建多阶段对话 Prompt
      3. 调用 GPT 返回下一阶段及回复
      4. 记录交互并更新状态与统计
    """
    user = update.message.from_user
    text = update.message.text.strip()

    # 更新用户基本信息
    record_user(user.id, user.username, user.first_name, user.last_name)

    # 第一步：询问姓名
    if not context.user_data.get("asked_name"):
        await update.message.reply_text("你好，我是小天，请告诉我你的名字。")
        context.user_data["asked_name"] = True
        return

    # 第二步：提取姓名并初始化会话状态
    if "user_name" not in context.user_data:
        match = re.search(r'(?:我叫|叫)(?P<name>\w+)', text)
        name = match.group('name') if match else text
        context.user_data.update({
            "user_name": name,
            "stage": "1",
            "task": "",
            "history": []
        })
        await update.message.reply_text(f"很高兴认识你，{name}！我们开始吧。")
        return

    # 会话核心：生成系统提示
    start = time.time()
    name = context.user_data["user_name"]
    stage = context.user_data["stage"]
    task = context.user_data["task"]
    history = context.user_data["history"]

    if stage == "1" and not task:
        context.user_data["task"] = text
        task = text

    system_prompt = (
        f"{BOT_PERSONALITY['personality']}\n"
        f"用户：{name}\n"
        f"阶段：{STAGE_DESCRIPTIONS[stage]}\n"
        f"任务：{task or '未定义'}\n\n"
        "请根据以下对话历史和新输入，返回 JSON：{ 'next_stage': <阶段>, 'reply': <机器人回复> }。\n"
        "历史对话：\n"
    )
    for msg in history:
        role = '用户' if msg['role']=='user' else '机器人'
        system_prompt += f"- {role}: {msg['content']}\n"
    system_prompt += f"- 用户: {text}\n"

    # GPT 调用与解析
    try:
        raw = get_ai_response([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ])
        result = json.loads(raw)
        next_stage = result.get("next_stage", stage)
        reply = result.get("reply", f"{name}，抱歉未能理解，请再说一遍。")
    except Exception as e:
        logger.error(f"处理失败: {e} | 原始: {raw}")
        next_stage, reply = stage, f"{name}，系统繁忙，请稍后再试。"

    # 记录与统计
    elapsed = time.time() - start
    record_interaction(user.id, BOT_PERSONALITY['name'], text, reply, elapsed)
    update_analytics(user.id, BOT_PERSONALITY['name'], elapsed)

    # 更新历史与阶段
    history.extend([{'role':'user','content':text},{'role':'assistant','content':reply}])
    context.user_data['history'] = history[-MAX_HISTORY_LENGTH:]
    context.user_data['stage'] = next_stage

    # 发送回复
    await update.message.reply_text(reply)

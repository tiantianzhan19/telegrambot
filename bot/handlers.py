# bot/handlers.py

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

# 各阶段中文描述，用于 System Prompt
STAGE_DESCRIPTIONS = {
    "1": "阶段1：问候 & 任务确认。目标：让用户说明今天要完成的任务。",
    "2": "阶段2：任务拆解 & 计划制定。目标：帮助用户把任务拆成小步骤并设定时间。",
    "3": "阶段3：执行监控。目标：检查进度、发现困难或进展。",
    "4": "阶段4：智能辅导 & 鼓励反馈。目标：针对困难给策略，针对进展给鼓励。",
    "5": "阶段5：完成 & 新任务。目标：庆祝完成并询问是否开始新任务。"
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理所有用户消息：
      1. 首次问候并索要姓名
      2. 提取“我叫XXX”或“叫XXX”中的姓名
      3. 动态多阶段对话：用 JSON 协议交给 GPT 决定 next_stage 和 reply
    """
    user      = update.message.from_user
    user_text = update.message.text.strip()

    # 记录/更新用户基础信息
    record_user(user.id, user.username, user.first_name, user.last_name)

    # —— 第一步：问候并索要姓名 ——
    if not context.user_data.get("asked_name"):
        await update.message.reply_text("你好，我是小天～很高兴认识你，你叫什么名字呀？")
        context.user_data["asked_name"] = True
        return

    # —— 第二步：接收并提取姓名 ——
    if "user_name" not in context.user_data:
        # 正则匹配 “我叫XXX” 或 “叫XXX”
        m = re.search(r'(?:我叫|叫)\s*(?P<name>[\u4e00-\u9fa5A-Za-z0-9_]+)', user_text)
        name = m.group('name') if m else user_text.replace('我叫', '').replace('叫', '').strip()
        context.user_data["user_name"] = name
        # 初始化对话状态
        context.user_data["stage"]   = "1"
        context.user_data["task"]    = ""
        context.user_data["history"] = []
        await update.message.reply_text(f"嗯，{name}，很高兴认识你！我们开始吧。")
        return

    # —— 后续多阶段对话 —— 
    start_time = time.time()
    name       = context.user_data["user_name"]
    stage      = context.user_data.get("stage", "1")
    task       = context.user_data.get("task", "")
    history    = context.user_data.get("history", [])

    # 阶段1：把第一条用户输入当作任务描述
    if stage == "1" and not task:
        context.user_data["task"] = user_text
        task = user_text

    # 构建 System Prompt（中文）
    system_prompt = (
        f"{BOT_PERSONALITY['personality']}\n\n"
        f"用户姓名：{name}\n"
        f"当前阶段：{STAGE_DESCRIPTIONS[stage]}\n"
        f"任务描述：{task or '未设置'}\n\n"
        "请你根据以下历史对话和用户新话，用 JSON 格式返回：\n"
        "{\n"
        '  "next_stage": "<下一个阶段编号 1-5>",\n'
        '  "reply": "<机器人本轮要说的话（请至少称呼用户一次）>"\n'
        "}\n"
        "历史对话：\n"
    )
    for msg in history:
        role = "用户" if msg["role"] == "user" else "机器人"
        system_prompt += f"- {role}: {msg['content']}\n"
    system_prompt += f"- 用户: {user_text}\n\n"

    # 调用 OpenAI 接口
    try:
        raw = get_ai_response([
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_text}
        ])
        result = json.loads(raw)
        next_stage = result.get("next_stage", stage)
        reply_text = result.get("reply", f"{name}，抱歉，我没理解清楚，请再说一遍。")
    except Exception as e:
        logger.error(f"GPT JSON 解析失败或请求出错: {e}\nRaw: {raw}")
        next_stage = stage
        reply_text = f"{name}，抱歉，处理时出错，请稍后再试。"

    # 记录交互 & 更新统计
    processing_time = time.time() - start_time
    record_interaction(user.id, BOT_PERSONALITY['name'], user_text, reply_text, processing_time)
    update_analytics(user.id, BOT_PERSONALITY['name'], processing_time)

    # 更新对话历史与阶段
    history.append({"role": "user",      "content": user_text})
    history.append({"role": "assistant", "content": reply_text})
    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]
    context.user_data["history"] = history
    context.user_data["stage"]   = next_stage

    # 发送回复
    await update.message.reply_text(reply_text)

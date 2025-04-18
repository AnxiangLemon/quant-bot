import asyncio
from telegram import Bot
from modules.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message_async(message: str):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"[Telegram] ❌ 异步发送失败：{e}")

# 保持一个全局复用的 event loop
def send_telegram_message(message: str):
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(send_telegram_message_async(message))
        print(f"[Telegram] ✅ 已异步发送消息：{message}")

    except Exception as e:
        print(f"[Telegram] ❌ 异步运行错误：{e}")

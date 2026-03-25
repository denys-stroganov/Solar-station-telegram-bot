from aiogram import Router, F, Dispatcher
from aiogram.types import Message
from core.telegram_formatter import TelegramFormatter
from core.data_analyzer import DataAnalyzer
import asyncio

router = Router()

def register_general_handlers(dp):
    dp.include_router(router)

@router.message(F.text == "🔋 General")
async def general_handler(message: Message, dispatcher: Dispatcher):
    client = dispatcher["client"]
    cache = dispatcher["cache"]

    cached = cache.get("raw_full_data")
    if cached:
        data = cached
    else:
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, client.get_full_data)
        cache.set("raw_full_data", data)

    analyzed = DataAnalyzer(data)
    text = TelegramFormatter(analyzed).general_info()
    await message.answer(text)
from aiogram import Router, F, Dispatcher
from aiogram.types import Message
from core.telegram_formatter import TelegramFormatter
from core.data_analyzer import DataAnalyzer

router = Router()

def register_refresh_handlers(dp):
    dp.include_router(router)

@router.message(F.text == "🔄 Refresh")
async def status_handler(message: Message, dispatcher: Dispatcher):
    client = dispatcher["client"]
    cache = dispatcher["cache"]

    cache.storage.clear()

    # --- TODAY ---
    data = client.get_full_data()
    analyzed = DataAnalyzer(data)
    fmt = TelegramFormatter(analyzed)

    text = (
        "<b>🔄 Refresh (new data)</b>\n\n"
        f"{fmt.today_info()}\n\n"
        f"{fmt.general_info()}\n\n"
        f"{fmt.runtime_info()}"
        # f"{fmt.total_info()}"
    )

    await message.answer(text)
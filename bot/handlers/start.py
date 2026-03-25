from aiogram import Router, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.reply_menu import reply_menu_keyboard
from core.subscribers import save_subscriber

router = Router()

def register_start_handlers(dp):
    dp.include_router(router)

@router.message(CommandStart())
async def start_handler(message: Message, dispatcher: Dispatcher):
    save_subscriber(message.chat.id)

    await message.answer(
        "<b>Вітаю! Оберіть потрібний розділ:</b>",
        reply_markup=reply_menu_keyboard(),
    )
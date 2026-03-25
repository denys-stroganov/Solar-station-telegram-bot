from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def reply_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="📅 Today"), KeyboardButton(text="🔋 General")],
        [KeyboardButton(text="⚡ Runtime"), KeyboardButton(text="📊 Total")],
        [KeyboardButton(text="🔄 Refresh"), KeyboardButton(text="📈 Status")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
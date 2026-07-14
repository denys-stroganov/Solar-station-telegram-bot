import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def reply_menu_keyboard():
    web_app_url = os.getenv("WEBHOOK_BASE_URL")
    
    keyboard = [
        [KeyboardButton(text="📅 Today"), KeyboardButton(text="🔋 General")],
        [KeyboardButton(text="⚡ Runtime"), KeyboardButton(text="📊 Total")],
        [KeyboardButton(text="🔄 Refresh"), KeyboardButton(text="📈 Status")],
    ]
    
    if web_app_url:
        keyboard.append([
            KeyboardButton(
                text="📊 Statistics",
                web_app=WebAppInfo(url=f"{web_app_url}/app/")
            )
        ])
        
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
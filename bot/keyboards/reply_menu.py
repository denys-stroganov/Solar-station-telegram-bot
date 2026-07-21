import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def reply_menu_keyboard():
    web_app_url = os.getenv("WEBHOOK_BASE_URL")
    
    keyboard = []
    
    if web_app_url:
        keyboard.append([
            KeyboardButton(
                text="📊 Statistics",
                web_app=WebAppInfo(url=f"{web_app_url}/app/")
            )
        ])
    
    keyboard.extend([
        [KeyboardButton(text="🔋 General"), KeyboardButton(text="⚡ Runtime")],
        [KeyboardButton(text="🔄 Refresh"), KeyboardButton(text="📈 Status")],
    ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
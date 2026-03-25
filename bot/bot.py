import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from bot.handlers.refresh import register_refresh_handlers
from bot.handlers.status import register_status_handlers
from core.auth_session import AuthSession
from core.data_client import DataClient
from core.const import URLS

from bot.handlers.start import register_start_handlers
from bot.handlers.today import register_today_handlers
from bot.handlers.general import register_general_handlers
from bot.handlers.runtime import register_runtime_handlers
from bot.handlers.total import register_total_handlers

from bot.monitors.power_monitor import power_monitor
from bot.monitors.soc_monitor import soc_monitor
from bot.monitors.battery_temp_monitor import battery_temp_monitor

from core.cache import Cache

async def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    cache = Cache(ttl = 30)
    dp["cache"] = cache
    dp["state"] = cache
    dp["power_state"] = {"isOffGrid": None}
    dp["soc_state"] = {
        "last_soc": None,
        "low_sent": False,
        "high_sent": False,
    }
    dp["battery_temp_state"] = {
        "last_temp": None,
        "low_sent": False,
        "high_sent": False,
    }

    #-----------------------------------
    # 1. Ініціалізація core-модулів
    #-----------------------------------
    auth = AuthSession(login_url=URLS["login"])
    auth.login()

    client = DataClient(auth)

    # Передаємо client у хендлери через dp["client"]
    dp["client"] = client
    dp["auth"] = auth

    #-----------------------------------
    # 2. Реєстрація хендлерів
    #-----------------------------------

    register_start_handlers(dp)
    register_today_handlers(dp)
    register_general_handlers(dp)
    register_runtime_handlers(dp)
    register_total_handlers(dp)
    register_status_handlers(dp)
    register_refresh_handlers(dp)

    #-----------------------------------
    # 3. Запуск бота
    #-----------------------------------

    print("Bot is running ... ")
    asyncio.create_task(power_monitor(bot, dp))
    asyncio.create_task(soc_monitor(bot, dp))
    asyncio.create_task(battery_temp_monitor(bot, dp))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
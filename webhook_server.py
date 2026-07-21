from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import logging
import os
import asyncio
from datetime import date
from core.auth_session import AuthSession
from core.data_client import DataClient
from core.cache import Cache

from bot.handlers.start import register_start_handlers
from bot.handlers.today import register_today_handlers
from bot.handlers.general import register_general_handlers
from bot.handlers.runtime import register_runtime_handlers
from bot.handlers.total import register_total_handlers
from bot.handlers.status import register_status_handlers
from bot.handlers.refresh import register_refresh_handlers

from bot.monitors.battery_temp_monitor import battery_temp_monitor
from bot.monitors.power_monitor import power_monitor
from bot.monitors.soc_monitor import soc_monitor

from core.subscribers import load_subscribers

class InjectDispatcherMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        data["dispatcher"] = dp
        return await handler(event, data)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ACCOUNT = os.getenv("ACCOUNT")
PASSWORD = os.getenv("PASSWORD")

WEBHOOK_PATH = "/webhook"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

dp.update.middleware(InjectDispatcherMiddleware())

register_start_handlers(dp)
register_today_handlers(dp)
register_general_handlers(dp)
register_runtime_handlers(dp)
register_total_handlers(dp)
register_status_handlers(dp)
register_refresh_handlers(dp)

# -----------------------------
# ІНІЦІАЛІЗАЦІЯ КЛІЄНТА ТА КЕШУ
# -----------------------------
LOGIN_URL = "https://server.luxpowertek.com/WManage/web/login"
auth = AuthSession(LOGIN_URL)
auth.login()

shared_cache = Cache(ttl=30)

dp["client"] = DataClient(auth)
dp["cache"] = shared_cache
dp["state"] = shared_cache
dp["auth"] = auth

async def handle(request: web.Request):
    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(
            bot,
            update,
            data={"dispatcher": dp, "bot": bot}
        )
    except Exception as e:
        logging.exception("Error while handling update")
    return web.Response()

async def on_startup(app):
    try:
        print(">>> on_startup begin")

        # Notify all subscribers that bot has restarted
        subscribers = load_subscribers()
        for chat_id in subscribers:
            try:
                await bot.send_message(
                    chat_id,
                    "🔄 Bot restarted! Please press /start to restore the menu."
                )
            except Exception as e:
                print(f"Failed to notify {chat_id}: {e}")

        asyncio.create_task(power_monitor(bot, dp))
        asyncio.create_task(soc_monitor(bot, dp))
        asyncio.create_task(battery_temp_monitor(bot, dp))

        base_url = os.getenv("WEBHOOK_BASE_URL")
        if base_url:
            webhook_url = f"{base_url}{WEBHOOK_PATH}"
            print(f"Setting webhook to: {webhook_url}")
            await bot.set_webhook(webhook_url)
        else:
            print("WEBHOOK_BASE_URL not set - skipping webhook registration")
        print(">>> on_startup OK")
    except Exception as e:
        print("❌ on_startup ERROR:", e)
        raise

async def on_shutdown(app):
    try:
        print(">>> on_shutdown begin")

        base_url = os.getenv("WEBHOOK_BASE_URL")
        if base_url:
            await bot.delete_webhook()
        await bot.session.close()
        print(">>> on_shutdown OK")
    except Exception as e:
        print("❌ on_shutdown ERROR:", e)


# -----------------------------
# API HANDLERS FOR MINI APP
# -----------------------------
def cors_json_response(data, status=200):
    return web.json_response(data, status=status, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })

async def handle_options(request: web.Request):
    return web.Response(headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })

async def handle_year_stats(request: web.Request):
    try:
        year_param = request.query.get("year")
        data = dp["cache"].get_or_fetch_year_stats(dp["client"], year_param=year_param)
        return cors_json_response(data)
    except Exception as e:
        return cors_json_response({"success": False, "error": str(e)}, status=500)

async def handle_month_stats(request: web.Request):
    try:
        year_param = request.query.get("year")
        month_param = request.query.get("month")
        data = dp["cache"].get_or_fetch_month_stats(dp["client"], year_param=year_param, month_param=month_param)
        return cors_json_response(data)
    except Exception as e:
        return cors_json_response({"success": False, "error": str(e)}, status=500)


def main():
    print(">>> Starting aiohttp server...")
    app = web.Application()

    async def health(request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    # API routes
    app.router.add_get("/api/stats/year", handle_year_stats)
    app.router.add_get("/api/stats/month", handle_month_stats)
    app.router.add_options("/api/stats/year", handle_options)
    app.router.add_options("/api/stats/month", handle_options)

    # Serve Static TMA Files
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(BASE_DIR, "frontend/dist")
    os.makedirs(dist_dir, exist_ok=True)
    app.router.add_static("/app", path=dist_dir, show_index=True)

    app.router.add_post(WEBHOOK_PATH, handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=8080)

    print(">>> aiohttp server stopped!")

if __name__ == "__main__":
    main()

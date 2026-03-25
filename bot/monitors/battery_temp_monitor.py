import asyncio
import logging
from core.subscribers import load_subscribers

LOW_TEMP = 5
HIGH_TEMP = 45

async def battery_temp_monitor(bot, dp):
    print("🌡 battery_temp_monitor started")

    client = dp["client"]
    auth = dp["auth"]

    state = {"low_sent": False, "high_sent": False}

    while True:
        try:
            loop = asyncio.get_running_loop()
            data = await asyncio.wait_for(
                loop.run_in_executor(None, client.get_full_data),
                timeout=10
            )

            temp = data["batteryInfo"]["tBat"]
            # logging.info(f"[Temp Monitor] Current temp: {temp} type={type(temp)} | low_sent: {state['low_sent']} | high_sent: {state['high_sent']}")
            if temp is None or not isinstance(temp, (int, float)):
                await asyncio.sleep(30)
                continue

            subscribers = load_subscribers()
            if not subscribers:
                await asyncio.sleep(30)
                continue

            # Low temperature
            if temp <= LOW_TEMP and not state["low_sent"]:
                state["low_sent"] = True
                state["high_sent"] = False

                for chat_id in subscribers:
                    await bot.send_message(chat_id, f"❄️ Низька температура акумуляторів: {temp}°C")

            # High temperature
            elif temp >= HIGH_TEMP and not state["high_sent"]:
                state["high_sent"] = True
                state["low_sent"] = False

                for chat_id in subscribers:
                    await bot.send_message(chat_id, f"🔥 Висока температура акумуляторів: {temp}°C")

        except PermissionError:
            print("[Temp Monitor] Session expired → re-login")
            auth.login()

        except asyncio.TimeoutError:
            print(f"[Temp Monitor] Timeout while fetching data")

        except Exception as e:
            print(f"[Temp Monitor] Error: {e}")

        await asyncio.sleep(30)
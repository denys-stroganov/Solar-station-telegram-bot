import asyncio
import logging

from core.subscribers import load_subscribers

async def soc_monitor(bot, dp):
    client = dp["client"]
    auth = dp["auth"]
    state_cache = dp["state"]

    state = {"low_sent": False, "high_sent": False}

    LOW_THRESHOLD = 20
    HIGH_THRESHOLD = 95

    logging.info("🔋 SOC Monitor started")

    while True:
        try:
            subscribers = load_subscribers()
            if not subscribers:
                logging.info("[SOC Monitor] No chat_id found, waiting ... ")
                await asyncio.sleep(30)
                continue

            loop = asyncio.get_running_loop()
            data = await asyncio.wait_for(
                loop.run_in_executor(None, client.get_full_data),
                timeout=10
            )

            if not data:
                logging.info("[SOC Monitor] Fail to fetch data, waiting ... ")
                await asyncio.sleep(30)
                continue

            # Зберігаємо тільки потрібні підсекції, НЕ весь data
            # raw_full_data видалено — це було головне джерело витоку пам'яті
            state_cache.set("raw_runtime", data.get("runtime"))
            state_cache.set("raw_energy", data.get("energy"))
            state_cache.set("raw_batteryInfo", data.get("batteryInfo"))

            battery_info = data.get("batteryInfo") or {}
            soc = battery_info.get("soc")

            # Явно звільняємо великий об'єкт
            del data

            if soc is None:
                await asyncio.sleep(10)
                continue

            if isinstance(soc, str):
                soc = int(soc.replace("%", ""))

            # Низький SOC
            if soc <= LOW_THRESHOLD and not state["low_sent"]:
                state["low_sent"] = True
                state["high_sent"] = False
                for chat_id in subscribers:
                    await bot.send_message(chat_id, f"⚠️ Низький рівень заряду: {soc}%")

            # Високий SOC
            elif soc >= HIGH_THRESHOLD and not state["high_sent"]:
                state["high_sent"] = True
                state["low_sent"] = False
                for chat_id in subscribers:
                    await bot.send_message(chat_id, f"🔋 Рівень заряду: {soc}%")

        except PermissionError:
            print("[SOC Monitor] Session expired → re-login")
            auth.login()

        except asyncio.TimeoutError:
            print("[SOC Monitor] Timeout while fetching data")

        except Exception as e:
            print(f"[SOC Monitor] Error: {e}")

        await asyncio.sleep(30)
import asyncio
from core.subscribers import load_subscribers

async def power_monitor(bot, dp):
    client = dp["client"]
    auth = dp["auth"]

    state = {"last_is_off_grid": None}

    print("⚡ power_monitor started")

    while True:
        try:
            loop = asyncio.get_running_loop()
            runtime = await asyncio.wait_for(
                loop.run_in_executor(None, client.get_runtime_info),
                timeout=10
            )

            if not runtime or "isOffGrid" not in runtime:
                await asyncio.sleep(15)
                continue

            is_off_grid = runtime["isOffGrid"]
            del runtime  # звільняємо об'єкт одразу після використання

            # Якщо значення не змінилося — нічого не робимо
            if state["last_is_off_grid"] == is_off_grid:
                await asyncio.sleep(15)
                continue

            state["last_is_off_grid"] = is_off_grid

            subscribers = load_subscribers()
            if subscribers:
                msg = "⚡ Мережа зникла" if is_off_grid else "⚡ Мережа з'явилась"
                for chat_id in subscribers:
                    await bot.send_message(chat_id, msg)

        except PermissionError:
            print("[Power Monitor] Session expired → re-login")
            auth.login()

        except asyncio.TimeoutError:
            print("[Power Monitor] Timeout while fetching data")

        except Exception as e:
            print(f"[Power Monitor] Error: {e}")

        await asyncio.sleep(15)
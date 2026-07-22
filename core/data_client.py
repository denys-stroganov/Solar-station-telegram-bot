from datetime import date
from core.const import SERIALS, URLS

class DataClient:
    def __init__(self, auth):
        self.auth = auth
        self.session = auth.session

    # ----------------------------
    # HELPERS
    # ----------------------------

    def _safe_post(self, url, payload=None, params=None, expect_json=True):
        resp = self.session.post(url, data=payload, params=params, timeout=5)

        if resp.status_code == 401:
            print("Сесія протухла - повторний логін")
            self.auth.login()
            resp = self.session.post(url, data=payload, params=params, timeout=5)

        try:
            return resp.json()
        except ValueError:
            print("Сесія протухла (HTML instead of JSON) - повторний логін")
            self.auth.login()
            resp = self.session.post(url, data=payload, params=params, timeout=5)
            return resp.json()

    # ----------------------------
    # DATE HELPER
    # ----------------------------
    @property
    def get_daily_date(self):
        return date.today().strftime("%Y-%m-%d")

    # ----------------------------
    # API CALLS
    # ----------------------------
    def get_energy_info(self):
        payload = {"serialNum": SERIALS[1]}
        return self._safe_post(URLS["energy"], payload)

    def get_runtime_info(self):
        payload = {"serialNum": SERIALS[1]}
        return self._safe_post(URLS["runtime"], payload)

    def get_details_info(self):
        payload = {"serialNum": SERIALS[1]}
        return self._safe_post(URLS["details"], payload)

    # ----------------------------
    # API CALLS
    # ----------------------------
    def get_battery_info(self):
        url = f'{URLS["batteryInfo"]}{self.get_daily_date}'
        params = {"serialNum": SERIALS[1]}
        payload = {"page": 1, "rows": 1}
        resp = self._safe_post(url, payload=payload, params=params, expect_json=True)

        rows = resp.get("rows", [])
        if not rows:
            print(f"[battery] Немає даних за {self.get_daily_date}")
            return None

        return rows[0]

    # ----------------------------
    # NORMALIZATION
    # ----------------------------

    # Поля, які приходять з бекенду постачальника помноженими на 10
    SCALED_FIELDS = ("ePvDay", "eExportDay", "eImportDay", "eConsumptionDay")

    @staticmethod
    def _normalize_row(row: dict, fields=SCALED_FIELDS, divisor: int = 10) -> dict:
        """Ділить вказані поля на divisor, зберігаючи структуру рядка."""
        for field in fields:
            if field in row and row[field] is not None:
                row[field] = round(row[field] / divisor, 1)
        return row

    @classmethod
    def _normalize_rows(cls, rows: list[dict]) -> list[dict]:
        return [cls._normalize_row(row) for row in rows]

    # ----------------------------
    # API CALLS
    # ----------------------------
    def get_month_column_info(self, year=None, month=None):
        today = date.today()
        payload = {
            "serialNum": SERIALS[1],
            "year": int(year) if year is not None else today.year,
            "month": int(month) if month is not None else today.month
        }
        resp = self._safe_post(URLS["monthColumnParallel"], payload)

        if resp and resp.get("success") and isinstance(resp.get("data"), list):
            resp["data"] = self._normalize_rows(resp["data"])

        return resp

    def get_year_column_info(self, year=None):
        today = date.today()
        payload = {
            "serialNum": SERIALS[1],
            "year": int(year) if year is not None else today.year
        }
        resp = self._safe_post(URLS["yearColumnParallel"], payload)

        if resp and resp.get("success") and isinstance(resp.get("data"), list):
            resp["data"] = self._normalize_rows(resp["data"])

        return resp

    # ----------------------------
    # API CALLS
    # ----------------------------
    def get_full_data(self):
        energy = self.get_energy_info()
        runtime = self.get_runtime_info()
        details = self.get_details_info()
        battery = self.get_battery_info()

        if battery is None:
            raise ValueError("Дані батареї недоступні за сьогодні")
            # або: return None — якщо хочеш м'яко обробити в хендлері

        return {
            "energy": energy,
            "runtime": runtime,
            "details": details,
            "batteryInfo": battery
        }
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
        """ LuxPower batteryInfo endpoint is NOT API.
        It requires:
        - serialNum
        - date (YYYY-MM-DD)
        - page, rows
        """
        url = f'{URLS["batteryInfo"]}{self.get_daily_date}'
        params = {"serialNum": SERIALS[1]}
        payload = {"page": 1, "rows": 1}
        resp = self._safe_post(url, payload=payload, params=params, expect_json=True)

        return resp["rows"][0]

    # ----------------------------
    # API CALLS
    # ----------------------------
    def get_full_data(self):
        """
        Returns a unified dict ready for DataAnalyzer.
        """
        energy = self.get_energy_info()
        runtime = self.get_runtime_info()
        details = self.get_details_info()
        battery = self.get_battery_info()
        return {
            "energy": energy,
            "runtime": runtime,
            "details": details,
            "batteryInfo": battery
        }
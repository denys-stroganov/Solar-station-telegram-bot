import os
import requests
import pickle
from dotenv import load_dotenv

class AuthSession:

    def __init__(self, login_url, cookies_file="cookies.pkl"):
        load_dotenv()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.cookies_file = os.path.join(BASE_DIR, cookies_file)

        self.username = os.getenv("ACCOUNT")
        self.password = os.getenv("PASSWORD")
        self.login_url = login_url
        self.session = requests.Session()
        self.is_logged_in = False

        if not self.username or not self.password:
            raise ValueError("ACCOUNT or PASSWORD aren't found in .env or variable environments")

        # Якщо є збережені cookies — пробуємо їх завантажити
        self._load_cookies()

    def _save_cookies(self):
        with open(self.cookies_file, "wb") as f:
            pickle.dump(self.session.cookies, f)

    def _load_cookies(self):
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, "rb") as f:
                cookies = pickle.load(f)
                self.session.cookies.update(cookies)
            print("Cookies loaded")

            # Тестовий запит для перевірки валідності cookies
            test_url = "https://server.luxpowertek.com/WManage/web/overview"
            resp = self.session.post(test_url)

            if resp.ok:
                self.is_logged_in = True
                print("Cookies are valid")
            else:
                print("Cookies expired, login required")
                self.is_logged_in = False

    def login(self):
        payload = {"account": self.username, "password": self.password}
        resp = self.session.post(self.login_url, data=payload)

        if resp.ok:
            self.is_logged_in = True
            self._save_cookies()
            print("Success auth, cookies saved")
        else:
            self.is_logged_in = False
            print(f"Auth ERROR: {resp.status_code}")
        return self.is_logged_in
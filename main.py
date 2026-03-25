from core.data_analyzer import DataAnalyzer
from core.auth_session import AuthSession
from core.data_client import DataClient
from core.const import URLS
from core.console_formatter import ConsoleFormatter

if __name__ == "__main__":
    try:
        auth = AuthSession(URLS["login"])
        auth.login()

        client = DataClient(auth.session)
        data = client.get_full_data()

        analyzer = DataAnalyzer(data)
        fmt = ConsoleFormatter(analyzer)

        print()
        print(fmt.general_info())
        print()
        print(fmt.electricity_info())
        print()
        print(fmt.today_info())
        print()
        print(fmt.total_info())
        print()

    except ValueError as e:
        print(e)
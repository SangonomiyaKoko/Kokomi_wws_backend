import os
database_file_path = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))

LATESTSEASON = 1013  # 排位最赛季代码
CVC_SEASON = 21
API_HOST = '0.0.0.0'  # api接口host
API_PORT = 443  # api接口port
PLATFORM = 'api'
BACK_END_PATH = os.path.join(database_file_path, 'kokomi_wws_backend')
DB_PATH = os.path.join(database_file_path, 'kokomi_wws_backend', 'database')
SERVER_DB_PATH = os.path.join(
    database_file_path, 'kokomi_game_server', 'data', 'server.json')
WG_API_TOKEN = ''
TOKEN = [
    'kokomi'
]
REQUEST_TIMEOUT = 5
REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.3162 SLBChan/103'
}

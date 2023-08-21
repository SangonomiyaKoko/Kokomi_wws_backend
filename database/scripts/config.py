import os
file_path = os.path.dirname(os.path.dirname(__file__))
USER_NUM = 10
UPDATE_NUM = 1
PLATFORM = 'backend'
BACK_END_PATH = file_path
DB_PATH = os.path.join(file_path, 'database')  # 默认数据库位置
UPDATE_TIME = [0, 10, 22, 23]  # 表示会在一下时间内进行一次更新，请根据结合需求
REQUEST_TIMEOUT = 5
REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.3162 SLBChan/103'
}
UPDATE_SLEEP = False  # 为True时会更新一个一次数据休眠一段时间，可以减少带宽压力
SLEEP_TIME = 0  # 上面配置为True时生效，单位为秒

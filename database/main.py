'''
recent数据更新逻辑

user.py: 从数据库中获取所有用户数据，依次判断是否需要更新
    ⇓
user_queue.py: 把需要更新的数据存储到队列中
    ⇓
update.py: 从队列中依次读取用户数据，更新数据库数据


ac.py
config.py
data_source.py
'''
import threading
import datetime
import gc
import time
from scripts.config import (
    UPDATE_TIME
)
import asyncio
from scripts import update
from scripts import user
# 定义线程处理函数


def process_data(thread_id):
    if thread_id == 0:
        asyncio.run(user.main())
    else:
        asyncio.run(update.main())


while True:
    # 创建两个线程
    threads = []
    for i in range(2):
        thread = threading.Thread(target=process_data, args=(i,))
        threads.append(thread)

    # 启动线程
    for thread in threads:
        thread.start()

    # 等待所有线程执行完成
    for thread in threads:
        thread.join()

    print("当前更新轮次已完成")
    if datetime.datetime.now().hour in UPDATE_TIME:
        pass
    else:
        print('未到达更新时间，线程休眠1800s')
        time.sleep(1800)
        continue
    gc.collect()

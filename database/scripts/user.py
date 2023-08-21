import os
import httpx
import asyncio
import time
import logging
import sqlite3
import traceback
from .user_queue import user_queue
from .ac import ac_list
from .config import (
    DB_PATH,
    REQUEST_HEADER,
    REQUEST_TIMEOUT,
    USER_NUM
)
from .data_source import (
    server_list
)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


def read_db():
    conn = sqlite3.connect(os.path.join(
        parent_file_path, 'database', 'user.db'))
    c = conn.cursor()
    cursor = c.execute("SELECT * from user_db")
    user_list = []
    for index in list(cursor):
        if str(index[0]) in ac_list:
            user_list.append(
                [index[0], index[1], True, ac_list[str(index[0])], index[3]])
        else:
            user_list.append(
                [index[0], index[1], False, None, index[3]])
    user_list = user_list[:20]
    conn.close()
    return user_list


async def fetch_data(
    user: list,
    sem
):
    async with sem:
        aid = user[0]
        server = user[1]
        use_ac = user[2]
        ac = user[3]
        battle_count = user[4]
        if check_today_data(
            aid=aid,
            server=server
        ):
            user_queue.put([aid, server, use_ac, ac, 1])
            print(f'[ INFO ] [Threading-1] | {server}_{aid} 加入更新队列')
            info_list[1] += 1
            return None
        url = f'{server_list[server]}/api/accounts/{aid}/' + \
            (f'?ac={ac}' if use_ac else '')
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url, headers=REQUEST_HEADER, timeout=REQUEST_TIMEOUT)
                requset_code = res.status_code
                requset_result = res.json()
                if requset_code == 200:
                    if 'hidden_profile' in requset_result['data'][str(aid)]:
                        print(
                            f'[ INFO ] [Threading-1] | {server}_{aid} 隐藏战绩,跳过更新')
                        info_list[3] += 1
                        return
                    if requset_result['data'][str(aid)]['statistics'] == {}:
                        now_battle_count = 0
                    else:
                        now_battle_count = requset_result['data'][str(aid)]['statistics']['pvp'].get(
                            'battles_count', 0) + requset_result['data'][str(aid)]['statistics']['rank_solo'].get('battles_count', 0)
                    if now_battle_count == battle_count:
                        print(
                            f'[ INFO ] [Threading-1] | {server}_{aid} 未有战斗数据,跳过更新')
                        info_list[2] += 1
                        return
                    else:
                        user_queue.put([aid, server, use_ac, ac, 1])
                        print(
                            f'[ INFO ] [Threading-1] | {server}_{aid} 加入更新队列')
                        info_list[1] += 1
                        return None
                elif requset_code == 404:
                    print(f'[ INFO ] [Threading-1] | {server}_{aid} 未有数据,跳过更新')
                    info_list[2] += 1
                    return
                else:
                    user_queue.put([aid, server, use_ac, ac, 1])
                    print(
                        f'[ERROR] [Threading-1] | {server}_{aid} 网络 {requset_code} 错误,加入更新队列')
                    info_list[4] += 1
                    return None
            except Exception as e:
                traceback.print_exc()
                user_queue.put([aid, server, use_ac, ac, 1])
                print(
                    f'[ERROR] [Threading-1] | {server}_{aid} 发生 {type(e).__name__} 错误,加入更新队列')
                info_list[4] += 1
                return None


def check_today_data(
    aid: str,
    server: str
):
    user_db_path = os.path.join(DB_PATH, server, f'{aid}.db')
    if os.path.exists(user_db_path):
        conn = sqlite3.connect(user_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM recent_data WHERE date = ?",
                       (time.strftime("%Y-%m-%d", time.localtime(time.time())),))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return False
        else:
            return True
    else:
        return True


def int_to_str(num: int):
    str_num = str(num)
    if len(str_num) > 3:
        return str_num[:len(str_num)-3] + ' ' + str_num[len(str_num)-3:]
    else:
        return str_num


async def main():
    print(f'[ INFO ] [Threading-1] | 更新开始')
    start_time = time.time()
    user_list = read_db()
    tasks = []
    sem = asyncio.Semaphore(USER_NUM)
    tasks = []
    global info_list
    info_list = [0, 0, 0, 0, 0]
    info_list[0] = len(user_list)
    # [总数，本次更新，跳过更新，隐藏战绩，错误]

    async def run_task(user):
        await fetch_data(user, sem)
    for user in user_list:
        tasks.append(run_task(user))
    await asyncio.gather(*tasks)
    print(f'[ INFO ] [Threading-1] | 更新完成')
    user_queue.put([None, None, None, None, 1])  # 停止信号
    start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    used_time = round(time.time()-start_time, 1)
    with open(os.path.join(parent_file_path, 'log', 'info.txt'), "a", encoding="utf-8") as f:
        f.write('-------------------------------------------------------------------------------------------------------------\n')
        f.write(f"{start}  更新开始\n")
        f.write(
            f"{now} [Threading-1] | 运行完成，遍历 {len(user_list)} 人数据，耗时 {used_time} s\n")
        f.write(
            f"{now} [Threading-1] | 更新数据：[\n    用户总数：{info_list[0]}\n    本次更新：{info_list[1]}\n    跳过更新：{info_list[2]}\n    隐藏战绩：{info_list[3]}\n    错误数量：{info_list[4]}\n]\n")
    f.close()

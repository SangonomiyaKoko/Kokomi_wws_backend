import time
import os
import logging
import asyncio
from .user_queue import user_queue
from .database_update import update_today_day
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


async def main():
    time.sleep(0.1)
    print(f'[ INFO ] [Threading-2] | 更新开始')
    user_num = 0
    error_list = []
    start_time = time.time()
    while True:
        if not user_queue.empty():
            user = user_queue.get()
            if user == [None, None, None, None, 1]:
                user_queue.put([None, None, None, None, 2])
                continue
            elif user == [None, None, None, None, 2]:
                # 运行结束
                break
            user_num += 1
            update_result = await update_today_day(
                aid=user[0],
                server=user[1],
                use_ac=user[2],
                ac=user[3]
            )
            if update_result['status'] == 'ok':
                print(
                    f'[ INFO ] [Threading-2] | {user[1]}_{user[0]} 更新成功,第 {user[4]} 次')
            elif user[4] == 1:
                print(
                    f'[ ERROR ] [Threading-2] | {user[1]}_{user[0]} 更新失败,稍后将再次尝试')
                user_queue.put([user[0], user[1], user[2], user[3], 2])
            else:
                print(
                    f'[ ERROR ] [Threading-2] | {user[1]}_{user[0]} 再次更新失败,错误已写入日志')
                update_error = update_result['error']
                error_list.append(f'Error:{update_error} | {user}')
        else:
            # 等待一段时间再检测队列
            time.sleep(1)
    print(f'[ INFO ] [Threading-2] | 更新完成')
    now = time.strftime("%Y-%m-%d %H:%M:%S",
                        time.localtime(time.time()))
    used_time = round(time.time()-start_time, 1)
    end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    with open(os.path.join(parent_file_path, 'log', 'info.txt'), "a", encoding="utf-8") as f:
        f.write(
            f"{now} [Threading-2] | 运行完成，更新 {user_num} 人数据，耗时 {used_time} s\n")
        f.write(f"{end} [Threading-2] | 更新完成,报错ID: [\n")
        for error in error_list:
            f.write(f'   {error}\n')
        f.write(
            ']\n-------------------------------------------------------------------------------------------------------------\n')
    f.close()

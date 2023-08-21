import sqlite3
import os
import time
import logging
import gc
from .ac import ac_list

parent_file_path = os.path.dirname(os.path.dirname(__file__))


async def main(
    user_id: str,
    platform: str
):
    parameter = [user_id, platform]
    try:
        # 从数据库获取绑定信息
        bind_db_path = os.path.join(
            parent_file_path, 'db', 'bind', f'user_{platform}.db')
        conn = sqlite3.connect(bind_db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS bind_db
                (
                    ID str PRIMARY KEY, 
                    UID str,
                    SERVER str,
                    USEPR bool,
                    USEAC bool,
                    AC str
                )'''
                     )
        cursor = conn.cursor()
        query = f"SELECT * FROM bind_db WHERE ID = '{user_id}'"
        cursor.execute(query)
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        if data == None:
            return {'status': 'info', 'message': '请先绑定游戏账号后查询'}
        else:
            if (
                str(data[0]) in ac_list and
                ac_list[str(data[0])][0] == platform and
                ac_list[str(data[0])][1] == data[2] and
                ac_list[str(data[0])][2] == str(data[1])
            ):
                data = list(data)
                data[3] = False if data[3] == 0 else True
                data[4] = True
                data[5] = ac_list[str(data[0])][3]
            else:
                data = list(data)
                data[3] = False if data[3] == 0 else True
                data[4] = False
                data[5] = None
            return {'status': 'ok', 'message': 'SUCCESS', 'data': data}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '程序内部错误,请联系麻麻解决', 'error': str(type(e).__name__)}
    finally:
        gc.collect()

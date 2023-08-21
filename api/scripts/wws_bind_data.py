import os
import time
import logging
import gc
import sqlite3
from .config import BACK_END_PATH, DB_PATH

parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


def creat_db(
    new_db_path
):
    con = sqlite3.connect(new_db_path)
    cursorObj = con.cursor()
    cursorObj.execute('''CREATE TABLE user_db
    (
        UID str PRIMARY KEY, 
        SERVER str,
        TIME int,
        USEAC bool,
        AC str
    )''')
    con.commit()
    con.close()


async def main(
    user_id: str,
    account_id: str,
    server: str,
    platform: str
):
    parameter = [user_id, account_id, server, platform]
    try:
        user_bind_db = os.path.join(
            parent_file_path, 'db', 'bind', f'user_{platform}.db')
        # if os.path.exists(user_bind_db) != True:
        #     creat_db(user_bind_db)
        conn = sqlite3.connect(user_bind_db)
        c = conn.cursor()
        cursor = c.execute(
            "SELECT ID,UID,SERVER,USEPR,USEAC,AC  from bind_db")
        for row in cursor:
            if str(row[0]) == str(user_id):
                statements = "UPDATE bind_db set UID = " + \
                    str(account_id)+" where ID="+str(user_id)
                c.execute(statements)
                statements = "UPDATE bind_db set SERVER = '" + \
                    str(server)+"' where ID="+str(user_id)
                c.execute(statements)
                res = await add_user_id(
                    uid=account_id,
                    server=server
                )
                if res['status'] == 'ok':
                    pass
                else:
                    return res

                break
        if conn.total_changes == 2:
            conn.commit()
            conn.close()
            if os.path.exists(os.path.join(DB_PATH, f'{server}/{account_id}.db')) == False:
                return {'status': 'info', 'message': '改绑成功!\n绑定后才会开始记录recent数据,无法查询之前的记录'}
            return {'status': 'info', 'message': '改绑成功!'}
        else:
            c.execute("INSERT OR REPLACE INTO bind_db (ID, UID, SERVER, USEPR, USEAC, AC) VALUES (?, ?, ?, ?, ?, ?)",
                      (str(user_id), account_id, server, 1, 0, None))
            conn.commit()
            conn.close()
            res = await add_user_id(
                uid=account_id,
                server=server
            )
            if res['status'] == 'ok':
                pass
            else:
                return res
            if os.path.exists(os.path.join(DB_PATH, f'{server}/{account_id}.db')) == False:
                return {'status': 'info', 'message': '绑定成功!\n绑定后才会开始记录recent数据,无法查询之前的记录'}
            return {'status': 'info', 'message': '绑定成功!'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '程序内部错误,请联系麻麻解决', 'error': str(type(e).__name__)}
    finally:
        gc.collect()


async def add_user_id(
    uid: str,
    server: str
):
    db_path = os.path.join(BACK_END_PATH, 'database', 'user.db')
    if os.path.exists(db_path) != True:
        creat_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT aid FROM user_db WHERE aid = ?", (uid,))
    result = cursor.fetchone()
    if result:
        result = {'status': 'ok', 'message': 'SUCCESS'}
    else:
        cursor.execute(
            "INSERT INTO user_db (aid,server,last_query_time,battle_count,use_ac,ac) VALUES (?, ?, ?, ?, ?, ?)", (uid, server, int(time.time()), 0, 0, None))
        result = {'status': 'ok', 'message': 'SUCCESS'}
    conn.commit()
    cursor.close()
    conn.close()
    return result

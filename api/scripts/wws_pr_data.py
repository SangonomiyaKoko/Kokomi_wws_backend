import os
import time
import logging
import gc
import sqlite3

parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


async def main(
    user_id: str,
    use_pr: bool,
    platform: str
):
    parameter = [user_id, use_pr, platform]
    try:
        user_bind_db = os.path.join(
            parent_file_path, 'db', 'bind', f'user_{platform}.db')
        conn = sqlite3.connect(user_bind_db)
        cursor = conn.cursor()
        sql_stmt = "UPDATE bind_db SET USEPR = ? WHERE ID = ?"
        cursor.execute(sql_stmt, (use_pr, user_id))
        conn.commit()
        conn.close()
        if use_pr:
            return {'status': 'info', 'message': '已启用PR评分'}
        else:
            return {'status': 'info', 'message': '已关闭PR评分'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '程序内部错误,请联系麻麻解决', 'error': str(type(e).__name__)}
    finally:
        gc.collect()

import sqlite3
import os
import time
import gc
import logging
from .config import BACK_END_PATH
from .personal_rating import get_personal_rating
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


async def main(
    user_list: dict,
    ship_id: str
):
    try:
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'data': {}
        }
        user_dict = {}
        # 读取用户数据
        platform = 'qq'
        bind_db_path = os.path.join(
            parent_file_path, 'db', 'bind', f'user_{platform}.db')
        conn = sqlite3.connect(bind_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bind_db")
        rows = cursor.fetchall()
        for row in rows:
            if str(row[0]) in user_list:
                user_dict[row[1]] = {
                    'nickname': user_list[str(row[0])],
                    'user_id': str(row[0])
                }
        aid_list = list(user_dict.keys())
        conn = sqlite3.connect(os.path.join(
            BACK_END_PATH, 'cache', 'cache.db'))
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE aid IN ({})".format(
            ', '.join('?' * len(aid_list)))
        cursor.execute(query, aid_list)
        cache_data = cursor.fetchall()
        data_dict = {}
        for row in cache_data:
            data_dict[row[0]] = {
                'name': row[1],
                'data': row[2]
            }
        conn.close()
        conn.close()
        for aid in aid_list:
            if aid not in data_dict:
                continue
            user_cache_data = eval(data_dict[aid]['data'])
            if ship_id in user_cache_data:
                result['data'][aid] = {
                    'user_name': user_dict[aid]['nickname'],
                    'user_id': user_dict[aid]['user_id'],
                    'game_id': data_dict[aid]['name'],
                    'data': format_index(
                        ship_id=ship_id,
                        json_data=user_cache_data[ship_id],
                        battle_type='pvp'
                    )
                }
        res = result
        del result
        return res
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
        return {'status': 'error', 'message': '程序内部错误,请联系麻麻解决', 'error': str(type(e).__name__)}
    finally:
        gc.collect()


def format_index(
    ship_id: str,
    json_data: dict,
    battle_type: str
) -> dict:
    '''
    数据处理并写入
    '''
    if json_data == {} or json_data['battles_count'] < 10:
        return None
    temp_res_data = {}
    cache_list = [
        'battles_count',
        'wins',
        'damage_dealt',
        'frags'
    ]
    for index in cache_list:
        temp_res_data[index] = json_data[index]

    pr_data = get_personal_rating(
        ship_id=ship_id,
        ship_data=[
            json_data['battles_count'],
            json_data['wins'],
            json_data['damage_dealt'],
            json_data['frags'],
        ],
        battle_type=battle_type
    )
    # select_ship 数据处理
    for index in [
        'value_battles_count',
        'personal_rating',
        'n_damage_dealt',
        'n_frags'
    ]:
        temp_res_data[index] = pr_data[index]

    return temp_res_data

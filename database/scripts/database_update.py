import httpx
import json
import os
import logging
import asyncio
import gc
import gzip
from datetime import date, timedelta
import time
import sqlite3
from .data_source import (
    server_list,
    recent_json_index,
    ach_json_index,
    ach_index_dict
)
from .config import(
    DB_PATH,
    BACK_END_PATH,
    REQUEST_TIMEOUT,
    REQUEST_HEADER,
    PLATFORM
)
file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))


'''
gzip压缩
gzip.compress(bytes(str(res['data']), encoding='utf-8'))
gzip解压缩
eval(str(gzip.decompress(open('temp.txt', 'rb').read()), encoding="utf-8"))
'''


async def fetch_data(
    url: str,
    aid: str
) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, headers=REQUEST_HEADER, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                return {'status': 'ok', 'message': 'SUCCESS', 'data': result['data'][str(aid)]}
            return {'status': 'error', 'message': '网络请求错误', 'error': f'Request code:{res.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': '网路请求错误', 'error': str(type(e).__name__)}


def write_cache(
    aid: str,
    nickname: str,
    base_data: dict
):
    '''更新缓存数据'''
    if base_data == {}:
        return
    cache_data = {}
    cache_list = [
        'battles_count',
        'wins',
        'damage_dealt',
        'frags',
        'original_exp',
        'planes_killed',
        'max_frags_by_planes',
        'max_planes_killed',
        'max_damage_dealt',
        'max_frags'
    ]
    for ship_id, ship_data in base_data.items():
        if ship_data['pvp'] == {}:
            continue
        cache_data[ship_id] = {}
        for index in cache_list:
            cache_data[ship_id][index] = ship_data['pvp'][index]

    conn = sqlite3.connect(os.path.join(BACK_END_PATH, 'cache', 'cache.db'))
    cursor = conn.cursor()
    table_create_query = '''
    CREATE TABLE IF NOT EXISTS users (
        aid str PRIMARY KEY,
        nickname str,
        data str
    );
    '''
    cursor.execute(table_create_query)
    user_data = (aid, nickname, str(cache_data))
    insert_or_replace_query = 'INSERT OR REPLACE INTO users (aid, nickname, data) VALUES (?, ?, ?)'
    cursor.execute(insert_or_replace_query, user_data)
    conn.commit()
    conn.close()


def ach_index(
    json_data: dict
) -> dict:
    '''
    处理成就数据
    '''
    if json_data == {}:
        return json_data
    temp_res_data = {}
    for ach_id, ach_name in ach_index_dict.items():
        ach_id = str(ach_id)
        if ach_id in json_data:
            for index in ach_json_index:
                if index.keywords == ach_name:
                    temp_res_data[index.index] = json_data[ach_id]['count']
                else:
                    continue
        else:
            continue
    return temp_res_data


def del_useless_index(
    json_data: dict
) -> dict:
    '''
    删除无用数据条目
    '''
    if json_data == {}:
        return json_data
    temp_res_data = {}
    for index in recent_json_index:
        temp_res_data[index.index] = json_data[index.keywords]
    return temp_res_data


async def get_data(
    aid: str,
    server: str,
    use_ac: bool = False,
    ac: str = None
):
    urls = [
        f'{server_list[server]}/api/accounts/{aid}/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/pvp/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/pvp_solo/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/pvp_div2/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/pvp_div3/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/rank_solo/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/achievements/' +
        (f'?ac={ac}' if use_ac else '')
    ]
    tasks = []
    responses = []
    async with asyncio.Semaphore(len(urls)):
        for url in urls:
            tasks.append(fetch_data(url, aid))
        responses = await asyncio.gather(*tasks)
        return responses


async def update_user_data(
    aid: str,
    server: str,
    use_ac: bool = False,
    ac: str = None
) -> dict:
    '''
    采用多线程并发的方式请求数据
    '''
    parameter = [aid, server, use_ac, ac]
    try:
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'error': None,
            'hidden': False,
            'nickname': None,
            'update_time': 0,
            'data': {
                'user': {
                    'last_battle_time': 0,
                    'leveling_points': 0,
                    'karma': 0
                },
                'ships': {},
                'achievements': {}
            }
        }
        request_responses = await get_data(
            aid=aid,
            server=server,
            use_ac=use_ac,
            ac=ac
        )
        # 判断是否成功获取数据
        for response in request_responses:
            if response['status'] == 'error':
                result['status'] = 'error'
                result['message'] = response['message']
                result['error'] = response['error']
                return result
        # 用户基本信息及状态
        basic_data = request_responses[0]['data']
        result['nickname'] = basic_data['name']
        result['update_time'] = int(time.time())
        if 'hidden_profile' in basic_data:
            result['hidden'] = True
            del result['error']
            return result
        else:
            if basic_data['statistics'] == {}:
                del result['error']
                return result
            result['data']['user'] = basic_data['statistics']['basic']
        now_battle_count = basic_data['statistics']['pvp'].get(
            'battles_count', 0) + basic_data['statistics']['rank_solo'].get('battles_count', 0)
        # 用户详细信息
        for index in [1, 2, 3, 4, 5]:
            type_index_list = ['pvp', 'pvp_solo',
                               'pvp_div2', 'pvp_div3', 'rank_solo']
            if index == 1:
                write_cache(
                    aid, request_responses[index]['data']['name'], request_responses[index]['data']['statistics'])
            for ship_id, ship_data in request_responses[index]['data']['statistics'].items():
                if ship_id not in result['data']['ships']:
                    result['data']['ships'][ship_id] = {
                        'pvp': {}, 'pvp_solo': {}, 'pvp_div2': {}, 'pvp_div3': {}, 'rank_solo': {}}
                result['data']['ships'][ship_id][type_index_list[index-1]] = del_useless_index(
                    ship_data[type_index_list[index-1]])
        result['data']['achievements'] = ach_index(
            request_responses[6]['data']['statistics']['achievements'])
        update_battle_count(aid=aid, battle_count=now_battle_count)
        gc.collect()
        return result
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '程序内部错误', 'error': str(type(e).__name__)}


def insert_sql(
    temp_json: json
) -> str:
    '''
    sql插入语句及数据
    '''
    sql = '''INSERT INTO recent_data(
    date,
    hidden,
    update_time,
    last_battle_time,
    leveling_points,
    karma,
    achievements,
    ships
    ) VALUES(?, ?, ?,?, ?, ?, ?, ?)'''
    data = (
        date.today().strftime("%Y-%m-%d"),
        temp_json['hidden'],
        temp_json['update_time'],
        None if temp_json['hidden'] else temp_json['data']['user']['last_battle_time'],
        None if temp_json['hidden'] else temp_json['data']['user']['leveling_points'],
        None if temp_json['hidden'] else temp_json['data']['user']['karma'],
        gzip.compress(
            bytes(str(temp_json['data']['achievements']), encoding='utf-8')),
        gzip.compress(bytes(str(temp_json['data']['ships']), encoding='utf-8')))
    return (sql, data)


def new_insert_sql(
    temp_json: json
) -> str:
    '''
    sql插入语句及数据
    '''
    sql = '''INSERT INTO recent_data(
    date,
    hidden,
    update_time,
    last_battle_time,
    leveling_points,
    karma,
    achievements,
    ships
    ) VALUES(?, ?, ?,?, ?, ?, ?, ?)'''
    data = (
        (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d"),
        temp_json['hidden'],
        temp_json['update_time'],
        temp_json['data']['user']['last_battle_time'],
        temp_json['data']['user']['leveling_points'],
        temp_json['data']['user']['karma'],
        gzip.compress(
            bytes(str(temp_json['data']['achievements']), encoding='utf-8')),
        gzip.compress(bytes(str(temp_json['data']['ships']), encoding='utf-8')))
    return (sql, data)


def user_db_path(
    aid: str,
    server: str
) -> str:
    '''
    返回用户db文件的路径
    '''
    return os.path.join(DB_PATH, f'{server}/{aid}.db')


def creat_db(
    new_db_path
):
    con = sqlite3.connect(new_db_path)
    cursorObj = con.cursor()
    cursorObj.execute("""
    CREATE TABLE recent_data(
        date str PRIMARY KEY,
        hidden bool,
        update_time int,
        last_battle_time int,
        leveling_points int,
        karma int,
        achievements bytes,
        ships bytes
    )""")
    con.commit()
    con.close()


def insert_data(
    aid: str,
    server: str,
    temp_json: json
):
    '''
    将数据插入数据库
    '''
    if os.path.exists(user_db_path(aid=aid, server=server)):
        con = sqlite3.connect(user_db_path(aid=aid, server=server))
        cursorObj = con.cursor()
        sql_tuple = insert_sql(temp_json=temp_json)
        try:
            cursorObj.execute(sql_tuple[0], sql_tuple[1])
        except:
            today = date.today().strftime("%Y-%m-%d")
            cursorObj.execute(
                f"DELETE from recent_data where date = '{today}'")
            cursorObj.execute(sql_tuple[0], sql_tuple[1])
        con.commit()
        con.close()
    else:
        creat_db(user_db_path(aid=aid, server=server))
        con = sqlite3.connect(user_db_path(aid=aid, server=server))
        cursorObj = con.cursor()
        sql_tuple = insert_sql(temp_json=temp_json)
        new_sql_tuple = new_insert_sql(temp_json=temp_json)
        cursorObj.execute(new_sql_tuple[0], new_sql_tuple[1])
        cursorObj.execute(sql_tuple[0], sql_tuple[1])
        con.commit()
        con.close()


async def update_today_day(
    aid: str,
    server: str,
    use_ac: bool = False,
    ac: str = None
) -> dict:
    '''
    更新今天的数据
    '''
    try:
        res = await update_user_data(
            aid=aid,
            server=server,
            use_ac=use_ac,
            ac=ac
        )
        if res['status'] == 'error':
            return res
        insert_data(
            aid=aid,
            server=server,
            temp_json=res
        )
        if PLATFORM == 'api':
            update_query_time(aid=aid)
        return {'status': 'ok', 'message': 'SUCCESS'}
    except Exception as e:
        return {'status': 'error', 'message': '更新数据库发生错误', 'error': f'{type(e).__name__}'}


def update_query_time(aid: str):
    '''
    更新用户查询数据的时间,api端使用
    '''
    conn = sqlite3.connect(os.path.join(BACK_END_PATH, 'database', 'user.db'))
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_db SET last_query_time = ? WHERE aid = ?", (int(time.time()), aid))
    conn.commit()
    cursor.close()
    conn.close()


def update_battle_count(aid: str, battle_count: int):
    '''
    更新用户查询数据的时间,api端使用
    '''
    conn = sqlite3.connect(os.path.join(BACK_END_PATH, 'database', 'user.db'))
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_db SET battle_count = ? WHERE aid = ?", (battle_count, aid))
    conn.commit()
    cursor.close()
    conn.close()


def ach_decoed(
    ach_data: dict
) -> dict:
    '''
    解压缩成就数据
    '''
    temp_json = {}
    for index in ach_json_index:
        if index.index in ach_data:
            temp_json[index.keywords] = ach_data[index.index]
    return temp_json


def ships_decoed(
    ships_data: dict
) -> dict:
    '''
    解压缩船只数据
    '''
    temp_json = {}
    for ship_id, ship_data in ships_data.items():
        temp_json[ship_id] = {'pvp': {}, 'pvp_solo': {},
                              'pvp_div2': {}, 'pvp_div3': {}, 'rank_solo': {}}
        type_list = ['pvp', 'pvp_solo', 'pvp_div2', 'pvp_div3', 'rank_solo']
        for type_index in type_list:
            if ship_data == {} or ship_data[type_index] == {}:
                continue
            else:
                for index in recent_json_index:
                    temp_json[ship_id][type_index][index.keywords] = ship_data[type_index][index.index]
    return temp_json


def construct_and_decoed_data(
    row: tuple
) -> dict:
    temp = {
        'date': row[0],
        'hidden': row[1],
        'update_time': row[2],
        'last_battle_time': row[3],
        'leveling_points': row[4],
        'karma': row[5],
        'achievements': ach_decoed(eval(str(gzip.decompress(row[6]), encoding="utf-8"))),
        'ships': ships_decoed(eval(str(gzip.decompress(row[7]), encoding="utf-8")))
    }
    return temp


def read_db_data(
    aid: str,
    server: str,
    date: str,
    today: str,
    use_ac: bool = False,
    ac: str = None
):
    update_date = update_today_day(
        aid=aid,
        server=server,
        use_ac=use_ac,
        ac=ac
    )
    if update_date['status'] == 'error':
        return update_date
    con = sqlite3.connect(user_db_path(aid=aid, server=server))
    cursorObj = con.cursor()
    cursorObj.execute("SELECT * FROM recent_data")
    rows = cursorObj.fetchall()
    recent_db_data = {}
    for row in rows:
        if row[0] == today:
            recent_db_data[today] = construct_and_decoed_data(row=row)
        if row[0] == date:
            recent_db_data[date] = construct_and_decoed_data(row=row)
    if date not in recent_db_data:
        return {'status': 'info', 'message': f'无当前日期数据,当前可查询{len(rows)-1}天'}
    cursorObj.close()
    con.close()
    return {'status': 'ok', 'message': 'SUCCESS', 'data': recent_db_data}

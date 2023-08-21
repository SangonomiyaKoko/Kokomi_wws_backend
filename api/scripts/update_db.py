import httpx
import json
import sqlite3
import os
import asyncio
parent_file_path = os.path.dirname(os.path.dirname(__file__))


async def update_ship_data():
    async with httpx.AsyncClient() as client:
        try:
            url = 'https://api.wows-numbers.com/personal/rating/expected/json/'
            res = await client.get(url, timeout=5)
            if res.status_code != 200:
                return {'status': 'error', 'message': '网络错误，请稍后重试', 'error': f'Request code:{res.status_code}'}
            result = res.json()
            update_ship_data_db(result['data'])
            return {'status': 'ok', 'message': 'SUCCESS'}
        except Exception as e:
            return {'status': 'error', 'message': '更新数据失败', 'error': type(e).__name__}


async def update_ship_info():
    async with httpx.AsyncClient() as client:
        try:
            url = 'https://vortex.worldofwarships.asia/api/encyclopedia/en/vehicles/'
            res = await client.get(url, timeout=5)
            if res.status_code != 200:
                return {'status': 'error', 'message': '网络错误，请稍后重试', 'error': f'Request code:{res.status_code}'}
            result = res.json()
            update_ship_info_db(result['data'])
            return {'status': 'ok', 'message': 'SUCCESS'}
        except Exception as e:
            return {'status': 'error', 'message': '更新数据失败', 'error': type(e).__name__}


def update_ship_data_db(
    json_data: dict
):
    db_path = os.path.join(parent_file_path, 'db', 'data', 'ship_data.db')
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS ship_data
                (
                    ship_id str PRIMARY KEY, 
                    win_rate float,
                    average_damage_dealt float, 
                    average_frags float
                )'''
                 )
    conn.execute('DELETE FROM ship_data')
    for ship_id, ship_data in json_data.items():
        if ship_data == []:
            continue
        dmg = ship_data['average_damage_dealt']
        win = ship_data['win_rate']
        frag = ship_data['average_frags']
        conn.execute(
            f"INSERT INTO ship_data VALUES ('{ship_id}', {win}, {dmg}, {frag})")
    conn.commit()
    conn.close()


def update_ship_info_db(
    json_data: dict
):
    db_path = os.path.join(parent_file_path, 'db', 'data', 'ship_info.db')
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS ship_info
                (
                    ship_id str PRIMARY KEY, 
                    ship_tier int,
                    ship_type str, 
                    ship_nation str
                )''')
    conn.execute('DELETE FROM ship_info')
    for ship_id, ship_data in json_data.items():
        if ship_data == []:
            continue
        ship_tier = ship_data['level']
        ship_type = ship_data['tags'][0]
        ship_nation = ship_data['nation']
        conn.execute(
            f"INSERT INTO ship_info VALUES ('{ship_id}', {ship_tier}, '{ship_type}', '{ship_nation}')")
    conn.commit()
    conn.close()


def test_db():
    con = sqlite3.connect(os.path.join(
        parent_file_path, 'db', 'data', 'ship_info.db'))
    cursorObj = con.cursor()
    cursorObj.execute("SELECT * FROM ship_info")
    rows = cursorObj.fetchall()
    for row in rows:
        print(row)
    con.close()


def get_ship_data(ship_id):
    conn = sqlite3.connect(os.path.join(
        parent_file_path, 'db', 'data', 'ship_data.db'))
    cursor = conn.cursor()
    query = f"SELECT * FROM ship_data WHERE ship_id = '{ship_id}'"
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data


def get_ship_info(ship_id):
    conn = sqlite3.connect(os.path.join(
        parent_file_path, 'db', 'data', 'ship_info.db'))
    cursor = conn.cursor()
    query = f"SELECT * FROM ship_info WHERE ship_id = '{ship_id}'"
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data


def get_all_ship_info():
    conn = sqlite3.connect(os.path.join(
        parent_file_path, 'db', 'data', 'ship_info.db'))
    cursor = conn.cursor()
    query = f"SELECT * FROM ship_info"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def get_all_ship_data():
    conn = sqlite3.connect(os.path.join(
        parent_file_path, 'db', 'data', 'ship_data.db'))
    cursor = conn.cursor()
    query = f"SELECT * FROM ship_data"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


# print(asyncio.run(update_ship_info()))
# print(asyncio.run(update_ship_data()))

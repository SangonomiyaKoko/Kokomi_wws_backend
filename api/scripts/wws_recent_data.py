import httpx
import os
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
import logging
import asyncio
import threading
import time
import gc
import sqlite3
from .data_source import server_list
from .database_update import read_db_data
from .personal_rating import get_personal_rating
from .config import (
    REQUEST_HEADER,
    REQUEST_TIMEOUT,
    BACK_END_PATH
)

parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, headers=REQUEST_HEADER, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            requset_result = res.json()
            if requset_code == 200:
                if 'vortex' in url:
                    return {'status': 'ok', 'message': 'SUCCESS', 'data': requset_result['data']}
                else:
                    return {'status': 'ok', 'message': 'SUCCESS', 'data': requset_result}
            if (
                # 特殊情况处理，如用户没有添加过工会请求会返回404
                '/clans/' in url
                and requset_code == 404
            ):
                return {'status': 'ok', 'message': 'SUCCESS', 'data': {"role": None, "clan": {}, "joined_at": None, "clan_id": None}}
            elif requset_code == 404:
                return {'status': 'info', 'message': '该用户数据不存在'}

            return {'status': 'error', 'message': '网络请求错误,请稍后重试', 'error': f'Request code:{res.status_code}'}
        except (TimeoutException, ConnectTimeout, ReadTimeout):
            return {'status': 'error', 'message': '网络请求超时,请稍后重试', 'error': 'Request Timeout'}
        except Exception as e:
            return {'status': 'error', 'message': '网路请求错误,请稍后重试', 'error': str(type(e).__name__)}


async def get_basic_data(
    aid: str,
    server: str,
    use_ac: bool = False,
    ac: str = None
):
    urls = [
        f'{server_list[server]}/api/accounts/{aid}/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/clans/'
    ]
    tasks = []
    responses = []
    async with asyncio.Semaphore(len(urls)):
        for url in urls:
            tasks.append(fetch_data(url))
        responses = await asyncio.gather(*tasks)
        return responses


async def get_database_data(
    result,
    aid,
    server,
    date: str,
    today: str,
    use_ac: bool = False,
    ac: str = None
):
    db_result = await read_db_data(
        aid=aid,
        server=server,
        date=date,
        today=today,
        use_ac=use_ac,
        ac=ac
    )
    if db_result['status'] != 'ok':
        return db_result
    if db_result['data'][today]['hidden'] == 1 or db_result['data'][date]['hidden'] == 1:
        result['hidden'] = True
        return {'status': 'ok', 'message': 'SUCCESS'}
    ship_data_calculated(
        result,
        db_result['data'][today]['ships'],
        db_result['data'][date]['ships']
    )
    ach_data_calculated(
        result,
        db_result['data'][today]['achievements'],
        db_result['data'][date]['achievements']
    )
    result['data']['time']['now_time'] = db_result['data'][today]['update_time']
    result['data']['time']['last_update_time'] = db_result['data'][date]['update_time']
    return {'status': 'ok', 'message': 'SUCCESS'}


def ship_data_calculated(
    result: dict,
    new_dict: dict,
    old_dict: dict
):
    #
    for ship_id, ship_data in new_dict.items():
        if ship_id in old_dict and ship_data == old_dict[ship_id]:
            continue
        if (
            ship_id not in old_dict or
            (ship_data['pvp'] != {} and old_dict[ship_id]['pvp'] == {}) or
            (ship_data['rank_solo'] != {} and old_dict[ship_id]['rank_solo'] == {}) or
            (ship_data['pvp'] != {} and ship_data['pvp']['battles_count'] > old_dict[ship_id]['pvp']['battles_count']) or
            (ship_data['rank_solo'] != {} and ship_data['rank_solo']
             ['battles_count'] > old_dict[ship_id]['rank_solo']['battles_count'])
        ):
            result['data']['ships'][ship_id] = {
                'pvp': {},
                'pvp_solo': {},
                'pvp_div2': {},
                'pvp_div3': {},
                'rank_solo': {}
            }
            for battle_type in ['pvp', 'pvp_solo', 'pvp_div2', 'pvp_div3', 'rank_solo']:
                if ship_id not in old_dict and ship_data[battle_type] != {}:
                    temp_res = {}
                    for battle_index, battle_num in ship_data[battle_type].items():
                        temp_res[battle_index] = ship_data[battle_type][battle_index]
                elif ((ship_data[battle_type] != {} and old_dict[ship_id][battle_type] != {}) and
                      ship_data[battle_type]['battles_count'] > old_dict[ship_id][battle_type]['battles_count']
                      ):
                    temp_res = {}
                    for battle_index, battle_num in ship_data[battle_type].items():
                        temp_res[battle_index] = ship_data[battle_type][battle_index] - \
                            old_dict[ship_id][battle_type][battle_index]
                elif ship_data[battle_type] != {} and old_dict[ship_id][battle_type] == {}:
                    temp_res = {}
                    for battle_index, battle_num in ship_data[battle_type].items():
                        temp_res[battle_index] = ship_data[battle_type][battle_index]
                else:
                    continue
                pr_data = get_personal_rating(
                    ship_id=ship_id,
                    ship_data=[
                        temp_res['battles_count'],
                        temp_res['wins'],
                        temp_res['damage_dealt'],
                        temp_res['frags'],
                    ],
                    battle_type=battle_type
                )
                for index in [
                    'value_battles_count',
                    'personal_rating',
                    'n_damage_dealt',
                    'n_frags'
                ]:
                    temp_res[index] = pr_data[index]
                result['data']['ships'][ship_id][battle_type] = temp_res

                if result['data']['pr']['battle_type'][battle_type] == {}:
                    result['data']['pr']['battle_type'][battle_type] = {
                        'battles_count': 0,
                        'wins': 0,
                        'damage_dealt': 0,
                        'frags': 0,
                        'original_exp': 0,
                        'value_battles_count': 0,
                        'personal_rating': 0,
                        'n_damage_dealt': 0,
                        'n_frags': 0
                    }
                for index in [
                    'battles_count',
                    'wins',
                    'damage_dealt',
                    'frags',
                    'original_exp'
                ]:
                    result['data']['pr']['battle_type'][battle_type][index] += temp_res[index]
                if pr_data['value_battles_count'] != 0:
                    for index in [
                        'value_battles_count',
                        'personal_rating',
                        'n_damage_dealt',
                        'n_frags'
                    ]:
                        result['data']['pr']['battle_type'][battle_type][index] += pr_data[index]
    return None


def ach_data_calculated(
    result: dict,
    new_dict: dict,
    old_dict: dict
):
    temp_res = {}
    for ach_id, ach_num in new_dict.items():
        if ach_id not in old_dict:
            temp_res[ach_id] = ach_num
        elif ach_num > old_dict[ach_id]:
            temp_res[ach_id] = ach_num - old_dict[ach_id]
        else:
            continue
    result['data']['achievements'] = temp_res
    return None


async def main(
    aid,
    server,
    date: str,
    today: str,
    use_ac: bool = False,
    ac: str = None
) -> dict:
    '''
    采用多线程并发的方式请求数据
    '''
    parameter = [aid, server, date, today, use_ac, ac]
    try:
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'error': None,
            'hidden': False,
            'nickname': None,
            'dog_tag': {},
            'data': {
                'user': {},
                'pr': {
                    'battle_type': {
                        'pvp': {},
                        'pvp_solo': {},
                        'pvp_div2': {},
                        'pvp_div3': {},
                        'rank_solo': {},
                    }
                },
                'ships': {},
                'achievements': {},
                'clans': {},
                'time': {
                    'last_update_time': 0,
                    'now_time': 0
                }
            }
        }
        # 获取用户信息
        basic_data = await get_basic_data(
            aid=aid,
            server=server,
            use_ac=use_ac,
            ac=ac
        )
        for response in basic_data:
            if response['status'] != 'ok':
                return response
        # 处理数据
        result['nickname'] = basic_data[0]['data'][aid]['name']
        if 'hidden_profile' in basic_data[0]['data'][aid]:
            result['hidden'] = True
            return result
        else:
            if basic_data[0]['data'][aid]['statistics'] == {}:
                return {'status': 'info', 'message': '该账号没有战斗数据'}
            result['data']['user'] = basic_data[0]['data'][aid]['statistics']['basic']
            result['dog_tag'] = basic_data[0]['data'][aid]['dog_tag']
        result['data']['clans'] = basic_data[1]['data']
        # 获取recent数据
        read_db_data = await get_database_data(
            result=result,
            aid=aid,
            server=server,
            date=date,
            today=today,
            use_ac=use_ac,
            ac=ac
        )
        if read_db_data['status'] != 'ok':
            return read_db_data
        # 处理最终结果
        res = result
        if res['status'] != 'error':
            del res['error']
        if res['status'] != 'ok':
            res['data'] = {}
        return res
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '程序内部错误,请联系麻麻解决', 'error': str(type(e).__name__)}
    finally:
        gc.collect()

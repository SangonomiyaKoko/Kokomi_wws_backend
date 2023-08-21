import httpx
import time
import os
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
import logging
import asyncio
import threading
import gc
from .config import (
    REQUEST_TIMEOUT,
    REQUEST_HEADER,
    LATESTSEASON
)
from .data_source import server_list
from .personal_rating import get_personal_rating
from .update_db import get_ship_info

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


async def get_other_data(
    aid: str,
    server: str,
    use_ac: bool = False,
    ac: str = None
):
    urls = [
        f'{server_list[server]}/api/accounts/{aid}/ships/rank_solo/' +
        (f'?ac={ac}' if use_ac else ''),
    ]
    tasks = []
    responses = []
    async with asyncio.Semaphore(len(urls)):
        for url in urls:
            tasks.append(fetch_data(url))
        responses = await asyncio.gather(*tasks)
        return responses


def other_data_processing(
    aid: str,
    responses: dict
) -> None:
    index = 0
    for response in responses:
        type_index_list = ['pvp', 'pvp_solo',
                           'pvp_div2', 'pvp_div3', 'rank_solo']
        for ship_id, ship_data in response['data'][aid]['statistics'].items():
            format_index(
                ship_data[type_index_list[index]],
                ship_id,
                type_index_list[index]
            )
        index += 1


def other_data_processing(
    aid: str,
    responses: dict
) -> None:
    index = 0
    for response in responses:
        type_index_list = ['rank_solo']
        for ship_id, ship_data in response['data'][aid]['statistics'].items():
            format_index(
                ship_data[type_index_list[index]],
                ship_id,
                type_index_list[index]
            )
        index += 1


def season_data(
    season_data: dict,
    rank_data: dict
) -> dict:
    '''
    排位赛季数据处理
    '''
    season_list = []
    i = LATESTSEASON
    while i >= 1001:
        season_list.append(i)
        i -= 1

    res_data = {}
    for season_index in season_list:
        res_data[str(season_index)] = {'battles_count': 0, 'wins': 0, 'damage_dealt': 0,
                                       'frags': 0, 'original_exp': 0, 'best_season_rank': 3, 'best_rank': 10}
    for season_index in season_list:
        if str(season_index) not in season_data:
            continue
        for index in ['battles_count', 'wins', 'damage_dealt', 'frags', 'original_exp']:
            if season_index <= 1003:
                res_data[str(season_index)][index] = season_data[str(
                    season_index)]['-1']['rank_solo'][index]
            else:
                res_data[str(season_index)][index] = season_data[str(
                    season_index)]['0']['rank_solo'][index]
        for season_stage, season_stage_data in rank_data[str(season_index)].items():
            for num in [1, 2, 3]:
                if str(num) in season_stage_data:
                    if res_data[str(season_index)]['best_season_rank'] > num:
                        res_data[str(season_index)]['best_season_rank'] = num
                        res_data[str(season_index)]['best_rank'] = season_stage_data[str(
                            num)]['rank_best']
                        continue
                    elif (
                        res_data[str(season_index)]['best_season_rank'] == num
                        and res_data[str(season_index)]['best_rank'] > season_stage_data[str(num)]['rank_best']
                    ):
                        res_data[str(season_index)]['best_rank'] = season_stage_data[str(
                            num)]['rank_best']
                        continue
                    continue
                else:
                    continue
    return res_data


def format_index(
    json_data: dict,
    ship_id: str,
    battle_type: str
) -> None:
    '''
    数据处理并写入
    '''
    if json_data == {}:
        return None
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
    # battle_type 数据处理
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
        result['data']['pr']['battle_type'][battle_type][index] += json_data[index]
    if pr_data['value_battles_count'] != 0:
        for index in [
            'value_battles_count',
            'personal_rating',
            'n_damage_dealt',
            'n_frags'
        ]:
            result['data']['pr']['battle_type'][battle_type][index] += pr_data[index]
    # ship_type 数据处理
    ship_info = get_ship_info(ship_id=ship_id)
    if ship_info == None:
        return None
    if battle_type != 'rank_solo':
        return None

    if result['data']['pr']['ship_type'][ship_info[2]] == {}:
        result['data']['pr']['ship_type'][ship_info[2]] = {
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
    for index in ['battles_count', 'wins', 'damage_dealt', 'frags', 'original_exp']:
        result['data']['pr']['ship_type'][ship_info[2]
                                          ][index] += json_data[index]
    if pr_data['value_battles_count'] != 0:
        for index in [
            'value_battles_count',
            'personal_rating',
            'n_damage_dealt',
            'n_frags'
        ]:
            result['data']['pr']['ship_type'][ship_info[2]
                                              ][index] += pr_data[index]


async def main(
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
        global result
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
                        'rank_solo': {},
                    },
                    'ship_type': {
                        'AirCarrier': {},
                        'Battleship': {},
                        'Cruiser': {},
                        'Destroyer': {},
                        'Submarine': {},
                    }
                },
                'season': {},
                'clans': {}
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
            result['data']['season'] = season_data(
                season_data=basic_data[0]['data'][aid]['statistics']['seasons'],
                rank_data=basic_data[0]['data'][aid]['statistics']['rank_info']
            )
        result['data']['clans'] = basic_data[1]['data']
        # 获取其他信息
        other_data = await get_other_data(
            aid=aid,
            server=server,
            use_ac=use_ac,
            ac=ac
        )
        for response in other_data:
            if response['status'] != 'ok':
                return response
        other_data_processing(
            aid=aid,
            responses=other_data
        )
        # 处理最终结果
        res = result
        del result
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

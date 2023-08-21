import httpx
import time
import os
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
import logging
import asyncio
import threading
import gc
from .data_source import (
    server_list,
    useful_index_list
)
from .config import (
    REQUEST_TIMEOUT,
    REQUEST_HEADER
)
from .personal_rating import get_personal_rating_info

file_path = os.path.dirname(__file__)
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
    ship_id: str,
    use_ac: bool = False,
    ac: str = None
):
    urls = [
        f'{server_list[server]}/api/accounts/{aid}/ships/{ship_id}/pvp/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/{ship_id}/pvp_solo/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/{ship_id}/pvp_div2/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/{ship_id}/pvp_div3/' +
        (f'?ac={ac}' if use_ac else ''),
        f'{server_list[server]}/api/accounts/{aid}/ships/{ship_id}/rank_solo/' +
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
            if ship_id not in result['data']['ships']:
                result['data']['ships'][ship_id] = {
                    'pvp': {},
                    'pvp_solo': {},
                    'pvp_div2': {},
                    'pvp_div3': {},
                    'rank_solo': {}
                }
            format_index(
                ship_id,
                ship_data[type_index_list[index]],
                type_index_list[index]
            )
        index += 1


def format_index(
    ship_id: str,
    json_data: dict,
    battle_type: str
) -> dict:
    '''
    数据处理并写入
    '''
    if json_data == {}:
        return None
    temp_res_data = {}
    for index in useful_index_list:
        temp_res_data[index] = json_data[index]

    pr_data = get_personal_rating_info(
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
    result['data']['ships'][ship_id][battle_type] = temp_res_data
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
            'n_frags': 0,
            'nwin': 0,
            'ndmg': 0,
            'nfrag': 0,
            'swin': 0,
            'sdmg': 0,
            'sfrag': 0,
            'uwin': 0,
            'udmg': 0,
            'ufrag': 0
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
            'n_frags',
            'nwin',
            'ndmg',
            'nfrag',
            'swin',
            'sdmg',
            'sfrag',
            'uwin',
            'udmg',
            'ufrag'
        ]:
            result['data']['pr']['battle_type'][battle_type][index] += pr_data[index]
    return None


async def main(
    aid: str,
    server: str,
    ship_id: list,
    use_ac: bool = False,
    ac: str = None
) -> dict:
    '''
    采用多线程并发的方式请求数据
    '''
    parameter = [aid, server, ship_id, use_ac, ac]
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
                        'pvp': {},
                        'pvp_solo': {},
                        'pvp_div2': {},
                        'pvp_div3': {},
                        'rank_solo': {},
                    }
                },
                'ships': {},
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
        result['data']['clans'] = basic_data[1]['data']
        # 获取其他信息
        other_data = await get_other_data(
            aid=aid,
            server=server,
            ship_id=ship_id,
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

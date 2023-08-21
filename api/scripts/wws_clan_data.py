import httpx
import time
import os
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
import logging
import asyncio
import gc
from .config import (
    REQUEST_TIMEOUT,
    REQUEST_HEADER
)
from .data_source import (
    clan_server_list,
    cw_achievement
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
            elif (
                '/clans.' in url
                and requset_code == 503
            ):
                return {'status': 'info', 'message': '该工会数据不存在'}
            elif requset_code == 404:
                return {'status': 'info', 'message': '该用户数据不存在'}

            return {'status': 'error', 'message': '网络请求错误,请稍后重试', 'error': f'Request code:{res.status_code}'}
        except (TimeoutException, ConnectTimeout, ReadTimeout):
            return {'status': 'error', 'message': '网络请求超时,请稍后重试', 'error': 'Request Timeout'}
        except Exception as e:
            return {'status': 'error', 'message': '网路请求错误,请稍后重试', 'error': str(type(e).__name__)}


async def get_other_data(
    clan_id: str,
    server: str
):
    urls = [
        f'{clan_server_list[server]}/api/clanbase/{clan_id}/claninfo/',
        f'{clan_server_list[server]}/api/members/{clan_id}/?battle_type=pvp'
    ]
    tasks = []
    responses = []
    async with asyncio.Semaphore(len(urls)):
        for url in urls:
            tasks.append(fetch_data(url))
        responses = await asyncio.gather(*tasks)
        return responses


def other_data_processing(responses: list):
    # clan_info数据处理
    clan_info_data_processing(responses[0]['data'])
    # clan_members数据处理
    clan_member_data_processing(responses[1]['data'])


def clan_info_data_processing(response: dict):
    # 工会成就
    for index in response['clanview']['achievements']:
        for ach_num, ach_list in cw_achievement.items():
            if index['cd'] in ach_list:
                result['data']['clans']['achievements'][ach_num] += index['count']
    # 工会基本信息
    basic_index = [
        'members_count',
        'max_members_count',
        'tag',
        'name',
        'created_at'
    ]
    for index in basic_index:
        result['data']['clans']['info'][index] = response['clanview']['clan'][index]
    # 军团建筑
    buildings_dict = {
        'headquarters': {'level': 0, 'max_level': 4},
        'dry_dock': {'level': 0, 'max_level': 6},
        'shipbuilding_factory': {'level': 0, 'max_level': 6},
        'university': {'level': 0, 'max_level': 6},
        'design_department': {'level': 0, 'max_level': 6},
        'coal_yard': {'level': 0, 'max_level': 3},
        'steel_yard': {'level': 0, 'max_level': 3},
        'academy': {'level': 0, 'max_level': 5},
        'paragon_yard': {'level': 0, 'max_level': 3},
        'superships_home': {'level': 0, 'max_level': 3}
    }
    for index, value in buildings_dict.items():
        if index not in response['clanview']['buildings']:
            continue
        buildings_dict[index]['level'] = response['clanview']['buildings'][index]['level']
    result['data']['clans']['buildings'] = buildings_dict
    # 本赛季cw是否参加
    if response['clanview']['wows_ladder']['battles_count'] > 0:
        result['data']['clans']['info']['cyc_active'] = True
    else:
        result['data']['clans']['info']['cyc_active'] = False
    # cw赛季数据
    cyc_index = [
        'division',
        'league',
        'division_rating',
        'season_number'
    ]
    for index in cyc_index:
        result['data']['clans']['info'][index] = response['clanview']['wows_ladder'][index]


def clan_member_data_processing(response: dict):
    member_index = [
        'name',
        'battles_count',
        'wins_percentage',
        'damage_per_battle',
        'frags_per_battle',
        'exp_per_battle',
        'battles_per_day',
        'days_in_clan',
        'last_battle_time'
    ]
    for member_data in response['items']:
        temp_dict = {}
        for index in member_index:
            temp_dict[index] = member_data[index]
        temp_dict['role'] = member_data['role']['name']
        result['data']['clans']['members'].append(temp_dict)
    result['data']['clans']['statistics'] = response['clan_statistics']


async def main(
    clan_id: str,
    server: str
):
    '''
    获取用户所属工会的信息
    '''
    parameter = [clan_id, server]
    try:
        global result
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'error': None,
            'data': {
                'clans': {
                    'info': {},
                    'statistics': {},
                    'achievements': {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0},
                    'buildings': {},
                    'members': []
                },
            }
        }
        clan_data = await get_other_data(
            clan_id=clan_id,
            server=server
        )
        for response in clan_data:
            if response['status'] != 'ok':
                return response
        other_data_processing(clan_data)
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

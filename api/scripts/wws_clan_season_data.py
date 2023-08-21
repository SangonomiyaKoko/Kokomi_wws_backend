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
    server_list,
    clan_server_list
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
    cvc_season: str,
    server: str
):
    urls = [
        f'{clan_server_list[server]}/api/clanbase/{clan_id}/claninfo/',
        f'{clan_server_list[server]}/api/members/{clan_id}/?battle_type=cvc&season={cvc_season}'
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
    # clan_season数据处理
    clan_season_data_processing(responses[1]['data'])


def clan_info_data_processing(response: dict):
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


def clan_season_data_processing(
    response: dict
):
    # 本赛季cw是否参加
    if response['clan_statistics']['battles_count'] > 0:
        result['data']['clans']['info']['cyc_active'] = True
    else:
        result['data']['clans']['info']['cyc_active'] = False
    # cw赛季数据
    cyc_index = [
        'division',
        'league',
        'division_rating'
    ]
    for index in cyc_index:
        result['data']['clans']['info'][index] = response['clan_statistics'][index]

    season_dict = {}
    code = 99
    while code >= 1:
        season_dict[str(code)] = {'1': {}, '2': {}}
        code -= 1
    for season_data in response['clan_statistics']['ratings']:
        if season_data['season_number'] > 99:
            continue
        season_dict[str(season_data['season_number'])][str(season_data['team_number'])] = {
            'battles_count': season_data['battles_count'],
            'wins_count': season_data['wins_count'],
            'longest_winning_streak': season_data['longest_winning_streak'],
            'league': season_data['max_position']['league'],
            'division': season_data['max_position']['division'],
            'division_rating': season_data['max_position']['division_rating']
        }
    del_list = []
    for number, data in season_dict.items():
        if data == {'1': {}, '2': {}}:
            del_list.append(number)
    for del_index in del_list:
        del season_dict[del_index]

    result['data']['clans']['season'] = season_dict
    for member_data in response['items']:
        member_dict = {
            'name': member_data['name'],
            'battles_count': member_data['battles_count'],
            'wins_percentage': member_data['wins_percentage'],
            'days_in_clan': member_data['days_in_clan'],
            'last_battle_time': member_data['last_battle_time'],
            'role': member_data['role']['name']
        }
        result['data']['clans']['members'].append(member_dict)


async def main(
    clan_id: str,
    cvc_season: str,
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
                    'season': {
                    },
                    'members': []
                },
            }
        }
        # 获取工会信息
        clan_data = await get_other_data(
            cvc_season=cvc_season,
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

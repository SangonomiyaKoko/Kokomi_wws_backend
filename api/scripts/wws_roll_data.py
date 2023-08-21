import httpx
import time
import os
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
import logging
import asyncio
import gc
from .data_source import (
    server_list
)
from .config import (
    REQUEST_TIMEOUT,
    REQUEST_HEADER
)
from .update_db import get_ship_info

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
    use_ac: bool = False,
    ac: str = None
):
    urls = [
        f'{server_list[server]}/api/accounts/{aid}/ships/pvp/' +
        (f'?ac={ac}' if use_ac else '')
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
    select: list,
    responses: dict
) -> None:
    for response in responses:
        for ship_id, ship_data in response['data'][aid]['statistics'].items():
            ship_info = get_ship_info(ship_id=ship_id)
            if ship_info == None:
                continue
            if (
                (select[0] == [] or ship_info[1] in select[0]) and
                (select[1] == [] or ship_info[2] in select[1]) and
                (select[2] == [] or ship_info[3] in select[2])
            ):
                result['data']['ships'].append(ship_id)


async def main(
    aid: str,
    server: str,
    select: list,
    use_ac: bool = False,
    ac: str = None
) -> dict:
    '''
    采用多线程并发的方式请求数据
    '''
    parameter = [aid, server, select, use_ac, ac]
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
                'ships': [],
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
            use_ac=use_ac,
            ac=ac
        )
        for response in other_data:
            if response['status'] != 'ok':
                return response
        other_data_processing(
            aid=aid,
            select=select,
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

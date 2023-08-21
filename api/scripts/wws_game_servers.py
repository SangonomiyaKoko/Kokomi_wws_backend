import json
import time
import httpx
import asyncio
import logging
import gc
import os
from .config import SERVER_DB_PATH


file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10)
        requset_code = res.status_code
        if requset_code == 200:
            requset_result = res.json()
            return requset_result
        else:
            return None


async def get_data():
    urls = [
        'https://api.worldoftanks.asia/wgn/servers/info/?application_id=aaaa630bfc681dfdbc13c3327eac2e85&game=wows',
        'https://api.worldoftanks.com/wgn/servers/info/?application_id=aaaa630bfc681dfdbc13c3327eac2e85&game=wows',
        'https://api.worldoftanks.eu/wgn/servers/info/?application_id=aaaa630bfc681dfdbc13c3327eac2e85&game=wows'
    ]
    tasks = []
    responses = []
    async with asyncio.Semaphore(len(urls)):
        for url in urls:
            tasks.append(fetch_data(url))
        responses = await asyncio.gather(*tasks)
        return responses


async def main() -> dict:
    '''
    采用多线程并发的方式请求数据
    '''
    parameter = []
    try:
        global result
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'error': None,
            'data': {
                'now': {'asia': None, 'eu': None, 'na': None, 'ru': None, 'cn': None},
                'max': {'asia': None, 'eu': None, 'na': None, 'ru': None, 'cn': None},
                'min': {'asia': None, 'eu': None, 'na': None, 'ru': None, 'cn': None},
                'hour': {'asia': {}, 'eu': {}, 'na': {}, 'ru': {}, 'cn': {}},
                'day': {'asia': {}, 'eu': {}, 'na': {}, 'ru': {}, 'cn': {}}
            }
        }
        now_data = await get_data()
        for index in now_data:
            if index == None or 'wows' not in index['data']:
                continue
            result['data']['now'][index['data']['wows'][0]['server'].lower(
            )] = index['data']['wows'][0]['players_online']
        with open(SERVER_DB_PATH) as f:
            json_data = json.load(f)
        f.close()
        begin_time = int(time.time()) - 24*60*60
        i = 0
        temp_dict = {'asia': {}, 'eu': {}, 'na': {}, 'ru': {}, 'cn': {}}
        for record_time, server_data in json_data.items():
            if int(record_time) < begin_time:
                pass
            else:
                for index in ['asia', 'eu', 'na', 'ru', 'cn']:
                    if index.upper() not in server_data:
                        continue
                    if result['data']['max'][index] == None or server_data[index.upper()] > result['data']['max'][index]:
                        result['data']['max'][index] = server_data[index.upper()]
                    if result['data']['min'][index] == None or server_data[index.upper()] < result['data']['min'][index]:
                        result['data']['min'][index] = server_data[index.upper()]
                    result['data']['hour'][index][record_time] = server_data[index.upper()]
                i += 1
            date_str = time.strftime(
                "%Y-%m-%d", time.localtime(int(record_time)))
            for index in ['asia', 'eu', 'na', 'ru', 'cn']:
                if index.upper() not in server_data:
                    continue
                if date_str not in temp_dict[index]:
                    temp_dict[index][date_str] = {
                        'num': 0,
                        'user': 0
                    }
                temp_dict[index][date_str]['num'] += 1
                temp_dict[index][date_str]['user'] += server_data[index.upper()]
        for index in ['asia', 'eu', 'na', 'ru', 'cn']:
            server_data = temp_dict[index]
            if server_data == {}:
                continue
            for date_str, date_data in server_data.items():
                if date_data['num'] <= 120:
                    continue
                result['data']['day'][index][date_str] = int(
                    date_data['user']/date_data['num'])

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

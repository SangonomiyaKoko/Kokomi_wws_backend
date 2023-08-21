import httpx
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
from .data_source import server_list
import logging
import os
import time
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


def aid_to_server(aid: str):
    if len(aid) == 10 and (aid[0] == '2' or aid[0] == '3'):
        return 'asia'
    elif len(aid) == 9 and (aid[0] == '5' or aid[0] == '6'):
        return 'eu'
    elif len(aid) == 10 and aid[0] == '1':
        return 'na'
    elif len(aid) == 10 and aid[0] == '7':
        return 'cn'
    elif len(aid) <= 8 or (len(aid) == 9 and aid[0] == '1'):
        return 'ru'
    else:
        return None


async def main(
    uid: str
):
    parameter = [uid]
    try:
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'error': None,
            'data': {},

        }
        server = aid_to_server(uid)
        if server == None:
            return {'status': 'info', 'message': 'uid格式错误'}
        async with httpx.AsyncClient() as client:
            url = f'{server_list[server]}/api/accounts/{uid}/'
            res = await client.get(url, timeout=5)
            if res.status_code == 404:
                return {'status': 'info', 'message': '该用户数据不存在'}
            if res.status_code != 200:
                return {'status': 'error', 'message': '网络错误，请稍后重试', 'error': 'Status Code:'+str(res.status_code)}
            response = res.json()
            if response['data'][str(uid)]['statistics'] == {}:
                return {'status': 'info', 'message': '该账号无游戏数据，请检查uid是否有误'}
            result['data'] = {
                'aid': uid,
                'server': server
            }
        if result['status'] != 'error':
            del result['error']
        return result
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'error', 'message': '网络请求超时,请稍后重试', 'error': 'Request Timeout'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '网路请求错误,请稍后重试', 'error': str(type(e).__name__)}

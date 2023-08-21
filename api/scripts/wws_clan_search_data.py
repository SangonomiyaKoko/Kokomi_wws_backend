import httpx
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
from .data_source import clan_server_list
import logging
import time
import os
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


async def main(
    clan_name: str,
    server: str
):
    parameter = [clan_name, server]
    try:
        async with httpx.AsyncClient() as client:
            url = clan_server_list[server] + \
                '/api/search/autocomplete/?search={}&type=clans'.format(
                    clan_name.upper())
            res = await client.get(url, timeout=5)
            print(url)
            if res.status_code != 200:
                return {'status': 'error', 'message': '网络错误，请稍后重试', 'error': f'Request code:{res.status_code}'}
            result = res.json()
        if result['search_autocomplete_result'] == []:
            return {'status': 'info', 'message': '无查询结果，请检查id拼写'}
        if result['search_autocomplete_result'][0]['tag'].upper() != clan_name.upper():
            return {'status': 'info', 'message': '无查询结果，请检查id拼写'}
        else:
            clan_id = result['search_autocomplete_result'][0]['id']
            return {'status': 'ok', 'message': 'SUCCESS', 'data': clan_id}
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'error', 'message': '网络请求超时,请稍后重试', 'error': 'Request Timeout'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '网路请求错误,请稍后重试', 'error': str(type(e).__name__)}

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


async def main(
    game_id: str,
    server: str
):
    parameter = [game_id, server]
    try:
        async with httpx.AsyncClient() as client:
            url = server_list[server] + \
                '/api/accounts/search/{}/?limit=10'.format(game_id.lower())
            res = await client.get(url, timeout=5)
            if res.status_code != 200:
                return {'status': 'error', 'message': '网络错误，请稍后重试', 'error': 'Status Code:'+str(res.status_code)}
            result = res.json()
        if result['data'] == []:
            return {'status': 'info', 'message': '无查询结果，请检查id拼写'}
        if result['data'][0]['name'].lower() != game_id.lower():
            return {'status': 'info', 'message': '无查询结果，请检查id拼写'}
        else:
            accountid = result['data'][0]['spa_id']
            return {'status': 'ok', 'message': 'SUCCESS', 'data': accountid}
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'error', 'message': '网络请求超时,请稍后重试', 'error': 'Request Timeout'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': '网路请求错误,请稍后重试', 'error': str(type(e).__name__)}

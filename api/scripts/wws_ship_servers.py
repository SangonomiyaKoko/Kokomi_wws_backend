import logging
import gc
import os
import time
from .update_db import (
    get_all_ship_data,
    get_all_ship_info
)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


async def main(select: list
               ) -> dict:
    '''
    采用多线程并发的方式请求数据
    '''
    parameter = [select]
    try:
        global result
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'error': None,
            'data': {
                'ships': {}
            }
        }
        ship_info_data = get_all_ship_info()
        select_list = []
        for ship_info in ship_info_data:
            if (
                (select[0] == [] or ship_info[1] in select[0]) and
                (select[1] == [] or ship_info[2] in select[1]) and
                (select[2] == [] or ship_info[3] in select[2])
            ):
                select_list.append(ship_info[0])
        ship_server_data = get_all_ship_data()
        for ship_server in ship_server_data:
            if ship_server[0] in select_list:
                result['data']['ships'][ship_server[0]] = {
                    'win_rate': round(ship_server[1], 2),
                    'average_damage_dealt': int(ship_server[2]),
                    'average_frags': round(ship_server[3], 2)
                }
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

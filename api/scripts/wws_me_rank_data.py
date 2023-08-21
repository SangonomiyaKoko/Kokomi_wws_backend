import httpx
import json
import os
from httpx import TimeoutException, ConnectTimeout, ReadTimeout
import asyncio
import threading
import logging
import time
import gc
from .data_source import server_list
import random
import requests
from lxml import etree
from .config import (
    REQUEST_TIMEOUT,
    REQUEST_HEADER
)
file_path = os.path.dirname(os.path.dirname(__file__))

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


def get_number_rank_data(
    nickname: str,
    ship_id: str,
    server: str
):
    headers = [{
        'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.0.3161 SLBChan/103',
        'Cookie': '_ga=GA1.2.480224465.1649926104; __gads=ID=5935751846d15bb3-22c09abbf2d10077:T=1649926104:RT=1649926104:S=ALNI_MboywqIoUq0vRNgqGeIHwWiVlBKhw; apiConsent=1; translationsProposals=1; _gid=GA1.2.1757806025.1654338079; __gpi=UID=000005256cfefcdd:T=1651587555:RT=1654607225:S=ALNI_MZPYlwmzfkg1commeVvI-mqNsu9bQ; PHPSESSID=cd0ohm1otc5i4a7i5ivi1eu3bf'
    },
        {
        'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'Cookie': 'PHPSESSID=pcg2f40e6p6kst6sd7rmidfo69; _ga=GA1.2.326175025.1654609818; _gid=GA1.2.1379565250.1654609818; __gads=ID=9399a2e08062cbe9-22887de9d0d300ce:T=1654609818:RT=1654609818:S=ALNI_MZxWIxXFKpvodhmhJ7iNXKJJdPS4Q; __gpi=UID=00000670fc196d90:T=1654609818:RT=1654609818:S=ALNI_Maf9M6LWO0W0OIIVqILbhc8dVxfcQ; apiConsent=1'
    },
        {
        'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
        'Cookie': 'PHPSESSID=a7j0i0mv3sl3pq9efes0g21sk9; _ga=GA1.2.339136817.1654610361; _gid=GA1.2.365516903.1654610361; _gat=1; __gads=ID=2f1a8b3664cebb54-2297a738d7d300d9:T=1654610361:RT=1654610361:S=ALNI_Man_AQVwYcLIst2iLCkRYPx1ggp3w; __gpi=UID=0000067106b6968b:T=1654610361:RT=1654610361:S=ALNI_MYdeqwp47qetFhBtLOs3Z48M-Nb8w; apiConsent=1'
    }
    ]
    ran_num = random.randint(0, 2)
    url = f'https://{server}.wows-numbers.com/ship/ranking/position.ajax?nickname={nickname}&ship={ship_id}'
    try:
        page = requests.get(url=url, headers=headers[ran_num], timeout=10).text
    except:
        result['status'] = 'info'
        result['message'] = '请求数据失败，请稍后尝试'
        return None
    page.encode('utf-8')
    if page == '':
        result['status'] = 'info'
        result['message'] = '没有您的排名数据,具体原因请前往wows-numbers网站查询'
        return None
    page_path = json.loads(page)
    page_url = page_path["url"]
    nickname = page_path["nickname"]
    number_url = 'https://server.wows-numbers.com'
    new_url = number_url.replace('server', server) + page_url
    ran_num = random.randint(0, 2)
    try:
        page = requests.get(
            url=new_url, headers=headers[ran_num], timeout=10).text
    except:
        result['status'] = 'info'
        result['message'] = '请求数据失败，请稍后尝试'
        return None
    page.encode('utf-8')
    html = etree.HTML(page)
    i = 1
    temp_json = {
        'user': {},
        'other': []
    }
    index_num = 1
    temp_dict = []
    pag_len = len(html.xpath('/html/body/div[3]/div[14]/table/tbody/tr'))
    while i <= pag_len:
        name = html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/@data-nickname')[0]
        if nickname == name:
            num = html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[1]/text()')[0]
            index_num = i
            battles = str(html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[3]/span/text()')[0])
            PR = str(html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[4]/span/text()')[0])
            PR_color = html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[4]/span/@style')[0]
            win_rate = str(html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[5]/span/text()')[0])
            win_rate_color = html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[5]/span/@style')[0]
            frag = str(html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[6]/span/text()')[0])
            frag_color = html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[6]/span/@style')[0]
            damage = str(html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[8]/span/text()')[0])
            damage_color = html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[8]/span/@style')[0]
            exp = str(html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[10]/span/text()')[0])

            tr_len = len(html.xpath('/html/body/div[3]/nav/ul/li'))
            if tr_len == 0:
                all_num = pag_len/100
            else:
                all_num = html.xpath(
                    '/html/body/div[3]/nav/ul/li['+str(tr_len-1)+']/a/text()')[0]
            if len(html.xpath('/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[2]/a')) != 2:
                nick_name = name
            else:
                nick_name = str(html.xpath(
                    '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[2]/a[1]/text()')[0]) + name
            temp_json['user'] = {
                'nickname': nick_name,
                'rank_num': num,
                'battles_count': battles,
                'personal_rating': PR,
                'win_rate': win_rate,
                'frag': frag,
                'damage_dealt': damage,
                'exp': exp,
                'win_rate_color': win_rate_color.split(';')[0],
                'frag_color': frag_color.split(';')[0],
                'damage_dealt_color': damage_color.split(';')[0],
                'personal_rating_color': PR_color.split(';')[0],
                'all_rank_num': all_num
            }
        name = html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/@data-nickname')[0]
        if len(html.xpath('/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[2]/a')) != 2:
            nick_name = name
        else:
            nick_name = str(html.xpath(
                '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[2]/a[1]/text()')[0]) + name
        num = html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[1]/text()')[0]
        battles = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[3]/span/text()')[0])
        PR = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[4]/span/text()')[0])
        PR_color = html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[4]/span/@style')[0]
        win_rate = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[5]/span/text()')[0])
        win_rate_color = html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[5]/span/@style')[0]
        frag = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[6]/span/text()')[0])
        frag_color = html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[6]/span/@style')[0]
        damage = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[8]/span/text()')[0])
        damage_color = html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[8]/span/@style')[0]
        max_frag = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[7]/span/text()')[0])
        max_damage = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[9]/span/text()')[0])
        exp = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[10]/span/text()')[0])
        max_exp = str(html.xpath(
            '/html/body/div[3]/div[14]/table/tbody/tr[' + str(i) + ']/td[11]/span/text()')[0])
        temp_dict.append([nick_name, num, battles, PR, win_rate, frag, damage, exp, max_damage,
                         max_frag, max_exp, win_rate_color.split(';')[0], frag_color.split(';')[0], damage_color.split(';')[0], PR_color.split(';')[0]])
        i += 1
    # temp_dict处理
    if pag_len > 10:
        if index_num < 6:
            temp_dict = temp_dict[0:10]
        elif pag_len - index_num < 4:
            temp_dict = temp_dict[pag_len-11:pag_len-1]
        else:
            temp_dict = temp_dict[index_num-6:index_num+4]
    for index in temp_dict:
        temp_json['other'].append({
            'nickname': index[0],
            'rank_num': index[1],
            'battles_count': index[2],
            'personal_rating': index[3],
            'win_rate': index[4],
            'frag': index[5],
            'damage_dealt': index[6],
            'exp': index[7],
            'max_damage': index[8],
            'max_frag': index[9],
            'max_exp': index[10],
            'win_rate_color': index[11],
            'frag_color': index[12],
            'damage_dealt_color': index[13],
            'personal_rating_color': index[14]
        })
    result['data']['rank'] = temp_json


async def main(
    aid: str,
    server: str,
    ship_id: str,
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
                'rank': {},
                'clans': {}
            }
        }
        if server in ['cn', 'ru']:
            return {
                'status': 'info',
                'message': 'wows numbers网站不支持国服与俄服数据的查询'
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
        # 获取排名数据
        get_number_rank_data(
            result['nickname'],
            ship_id,
            server
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

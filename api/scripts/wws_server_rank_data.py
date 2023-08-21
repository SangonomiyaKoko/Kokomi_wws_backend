import os
import logging
import gc
import time
import random
import requests
from lxml import etree
file_path = os.path.dirname(os.path.dirname(__file__))
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    parent_file_path, 'log', 'error.log'), level=logging.ERROR)


def get_number_rank_data(
    server: str,
    ship_id: str
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

    page_url = f'/ship/{ship_id},/?p=1'
    number_url = 'https://server.wows-numbers.com'
    new_url = number_url.replace('server', server) + page_url
    ran_num = random.randint(0, 2)
    try:
        page = requests.get(
            url=new_url, headers=headers[ran_num], timeout=10).text
    except:
        result['status'] = 'info'
        result['message'] = '请求数据失败，请稍后尝试'
        return result
    page.encode('utf-8')
    html = etree.HTML(page)
    i = 1
    temp_json = []
    temp_dict = []
    pag_len = len(html.xpath('/html/body/div[3]/div[14]/table/tbody/tr'))
    if pag_len == 0:
        result['status'] = 'info'
        result['message'] = '无当前船只的数据'
        return result
    while i <= pag_len:
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
    if pag_len > 50:
        temp_dict = temp_dict[0:50]
    for index in temp_dict:
        temp_json.append({
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
    return result


async def main(
    server: str,
    ship_id: str
) -> dict:
    parameter = [server, ship_id]
    try:
        if server in ['cn', 'ru']:
            return {
                'status': 'info',
                'message': 'wows numbers网站不支持国服与俄服数据的查询'
            }
        global result
        result = {
            'status': 'ok',
            'message': 'SUCCESS',
            'error': None,
            'data': {
                'rank': {}
            }
        }
        # 获取排名数据
        result = get_number_rank_data(
            server=server,
            ship_id=ship_id
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

'''
https://api.worldoftanks.asia/wgn/servers/info/?application_id=aaaa630bfc681dfdbc13c3327eac2e85&game=wows
https://api.worldoftanks.com/wgn/servers/info/?application_id=aaaa630bfc681dfdbc13c3327eac2e85&game=wows
https://api.worldoftanks.eu/wgn/servers/info/?application_id=aaaa630bfc681dfdbc13c3327eac2e85&game=wows
'''
import asyncio
import httpx
import time
import json
import os
import json
file_path = os.path.dirname(__file__)


async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10)
        requset_code = res.status_code
        if requset_code == 200:
            result = res.json()
            return result
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

while True:
    try:
        json_path = os.path.join(file_path, 'data', 'server.json')

        with open(json_path) as f:
            server_data = json.load(f)
        f.close()
        time_str = str(int(time.time()))
        server_data[time_str] = {
            'ASIA': None,
            'NA': None,
            'EU': None
        }
        res = asyncio.run(get_data())
        for index in res:
            if index == None:
                continue
            server_data[time_str][index['data']['wows'][0]['server']
                                  ] = index['data']['wows'][0]['players_online']

        with open(json_path, 'w') as f:
            json.dump(server_data, f, indent=4)
        f.close()
        print('INFO： {} |  as:{} na:{} eu:{} '.format(
            time_str, server_data[time_str]['ASIA'], server_data[time_str]['NA'], server_data[time_str]['EU']))
    except:
        print('error')
    time.sleep(600)

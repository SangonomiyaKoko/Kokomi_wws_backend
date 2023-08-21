from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import os
import scripts.config as config
import sqlite3
import time
from scripts import (
    wws_basic_data,
    wws_rank_data,
    wws_bind_data,
    wws_recent_data,
    wws_user_search_data,
    wws_platform_bind_data,
    wws_me_rank_data,
    wws_server_rank_data,
    wws_select_ship_data,
    wws_single_ship_data,
    wws_roll_data,
    wws_clan_data,
    wws_clan_season_data,
    wws_clan_search_data,
    wws_user_clan_search,
    wws_group_rank_data,
    wws_game_servers,
    wws_sx_data,
    wws_user_check_data,
    wws_ship_servers,
    wws_pr_data,
    wws_rank_season_data,
    wws_rank_ship_data

)
from data_source import (
    user_basic_parameters,
    user_bind_parameters,
    user_platform_parameters,
    user_recent_parameters,
    user_search_parameters,
    user_me_rank_parameter,
    user_server_rank_parameter,
    user_select_ship_parameter,
    user_single_ship_parameter,
    user_clan_parameter,
    clan_parameter,
    clan_season_parameter,
    clan_search_parameter,
    token_parameter,
    uid_parameter,
    ship_server_parameter,
    user_pr_parameters,
    user_rank_season_parameter,
    user_rank_ship_parameter

)
app = FastAPI()
description = '''
KokomiBot官方数据接口，Token请联系作者获取
--

1.QQ群聊：164933984

2.邮箱：3197206779@qq.com

3.加入 Discord 或 KOOK 的官方频道

- Discord:https://discord.gg/GjgmvQ2BHX

- KOOK:https://kook.top/N8Ymq2

---
'''
token_msg = '当前token不可用，请联系作者申请接口token'
app = FastAPI(title='Kokomi API', version='1.1.0',
              description=description)
file_path = os.path.dirname(__file__)


def log_db(
    function_index: int,
    status: str,
    commons: dict
):

    log_db_path = os.path.join(
        file_path, 'log', 'day', f'{time.strftime("%Y-%m-%d", time.localtime(time.time()))}.db')
    conn = sqlite3.connect(log_db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS api_log
        (
            TIME int, 
            FUNCTION int, 
            STATUS str,
            COMMONS str
        )''')
    conn.execute("INSERT INTO api_log (TIME,FUNCTION,STATUS,COMMONS) VALUES (?,?,?,?)", (int(
        time.time()), function_index, status, str(commons)))
    conn.commit()
    conn.close()


@app.get("/test/", summary='测试', tags=['Test Interface'])
async def test():
    """
    创建一个新项目。

    - **item** (请求体): 项目信息
        - **name** (str): 项目名称
        - **description** (str): 项目描述

    返回：
    - **id** (int): 项目的唯一标识符
    - **item** (Item): 创建的项目信息
        - **name** (str): 项目名称
        - **description** (str): 项目描述

    """
    return 'ok'


@app.get("/user/basic/", summary='用户基础数据', description='No description here', tags=['用户基本数据接口'])
async def user_basic(commons: dict = Depends(user_basic_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_basic_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        use_ac=commons['use_ac'],
        ac=commons['ac']
    )
    log_db(1, result['status'], commons)
    return result


@app.get("/user/rank/", summary='用户排位数据', description='No description here', tags=['用户基本数据接口'])
async def user_rank(commons: dict = Depends(user_basic_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_rank_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        use_ac=commons['use_ac'],
        ac=commons['ac']
    )
    log_db(2, result['status'], commons)
    return result


@app.get("/user/search/", summary='查找用户', description='No description here', tags=['数据查询接口'])
async def user_rank(commons: dict = Depends(user_search_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_user_search_data.main(
        game_id=commons['name'],
        server=commons['server']
    )
    log_db(3, result['status'], commons)
    return result


@app.get("/user/platform/", summary='查找用户id', description='No description here', tags=['数据查询接口'])
async def user_rank(commons: dict = Depends(user_platform_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_platform_bind_data.main(
        user_id=commons['user_id'],
        platform=commons['platform'],
    )
    log_db(4, result['status'], commons)
    return result


@app.get("/user/ships/", summary='查找用户指定范围内船只的数据', description='No description here', tags=['用户基本数据接口'])
async def user_rank(commons: dict = Depends(user_select_ship_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_select_ship_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        select=eval(commons['select']),
        use_ac=commons['use_ac'],
        ac=commons['ac']
    )
    log_db(5, result['status'], commons)
    return result


@app.get("/user/roll/", summary='查找用户指定范围内的船只', description='No description here', tags=['用户基本数据接口'])
async def user_rank(commons: dict = Depends(user_select_ship_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_roll_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        select=eval(commons['select']),
        use_ac=commons['use_ac'],
        ac=commons['ac']
    )
    log_db(6, result['status'], commons)
    return result


@app.get("/user/ship/", summary='查找用户指定船只的数据', description='No description here', tags=['用户基本数据接口'])
async def user_rank(commons: dict = Depends(user_single_ship_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_single_ship_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        ship_id=commons['ship_id'],
        use_ac=commons['use_ac'],
        ac=commons['ac']
    )
    log_db(7, result['status'], commons)
    return result


@app.get("/database/recent/", summary='recent数据查询', description='No description here', tags=['数据库接口'])
async def user_bind(commons: dict = Depends(user_recent_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_recent_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        date=commons['date'],
        today=commons['today'],
        use_ac=commons['use_ac'],
        ac=commons['ac']
    )
    log_db(8, result['status'], commons)
    return result


@app.get("/database/bind/", summary='用户绑定', description='No description here', tags=['数据库接口'])
async def user_bind(commons: dict = Depends(user_bind_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_bind_data.main(
        user_id=commons['user_id'],
        account_id=commons['aid'],
        server=commons['server'],
        platform=commons['platform']
    )
    log_db(9, result['status'], commons)
    return result


@app.get("/leaderboard/search/", summary='查询用户在number的排行榜', description='No description here', tags=['Number数据接口'])
async def user_bind(commons: dict = Depends(user_me_rank_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_me_rank_data.main(
        aid=commons['aid'],
        server=commons['server'],
        ship_id=commons['ship_id']
    )
    log_db(10, result['status'], commons)
    return result


@app.get("/leaderboard/server/", summary='查询船只在number的排行', description='No description here', tags=['Number数据接口'])
async def user_bind(commons: dict = Depends(user_server_rank_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_server_rank_data.main(
        server=commons['server'],
        ship_id=commons['ship_id']
    )
    log_db(11, result['status'], commons)
    return result


@app.get("/user/clan/", summary='用户所属工会', description='No description here', tags=['数据查询接口'])
async def user_basic(commons: dict = Depends(user_clan_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_user_clan_search.main(
        aid=str(commons['aid']),
        server=commons['server']
    )
    log_db(12, result['status'], commons)
    return result


@app.get("/clan/search/", summary='查找工会', description='No description here', tags=['数据查询接口'])
async def user_basic(commons: dict = Depends(clan_search_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_clan_search_data.main(
        clan_name=commons['clan_name'],
        server=commons['server']
    )
    log_db(13, result['status'], commons)
    return result


@app.get("/clan/info/", summary='工会基本数据', description='No description here', tags=['工会数据接口'])
async def user_basic(commons: dict = Depends(clan_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_clan_data.main(
        clan_id=commons['clan_id'],
        server=commons['server']
    )
    log_db(14, result['status'], commons)
    return result


@app.get("/clan/cvc/", summary='工会cw数据', description='No description here', tags=['工会数据接口'])
async def user_basic(commons: dict = Depends(clan_season_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_clan_season_data.main(
        clan_id=commons['clan_id'],
        cvc_season=commons['cvc_season'],
        server=commons['server']
    )
    log_db(15, result['status'], commons)
    return result


class Item(BaseModel):
    token: str
    ship_id: str
    data: dict


@app.post("/group/rank/", summary='批量获取数据库数据', description='No description here', tags=['数据库接口'])
async def user_basic(items: Item):
    if items.token not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_group_rank_data.main(
        user_list=items.data,
        ship_id=items.ship_id
    )
    log_db(16, result['status'], None)
    return result


@app.get("/server/active/", summary='获取服务器在线人数数据', description='No description here', tags=['服务器统计接口'])
async def user_rank(commons: dict = Depends(token_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_game_servers.main()
    log_db(17, result['status'], None)
    return result


@app.get("/user/sx/", summary='扫雪', description='No description here', tags=['用户基本数据接口'])
async def user_rank(commons: dict = Depends(user_basic_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_sx_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        use_ac=commons['use_ac'],
        ac=commons['ac']
    )
    log_db(18, result['status'], commons)
    return result


@app.get("/user/uid/", summary='查找uid', description='No description here', tags=['数据查询接口'])
async def user_rank(commons: dict = Depends(uid_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_user_check_data.main(
        uid=commons['uid']
    )
    log_db(19, result['status'], commons)
    return result


@app.get("/server/ships/", summary='获取船只服务器数据', description='No description here', tags=['服务器统计接口'])
async def user_rank(commons: dict = Depends(ship_server_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_ship_servers.main(
        select=eval(commons['select'])
    )
    log_db(20, result['status'], commons)
    return result


@app.get("/database/pr/", summary='更改use_pr', description='No description here', tags=['数据库接口'])
async def user_bind(commons: dict = Depends(user_pr_parameters)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_pr_data.main(
        user_id=commons['user_id'],
        use_pr=commons['use_pr'],
        platform=commons['platform']
    )
    log_db(21, result['status'], commons)
    return result


@app.get("/rank/season/", summary='用户排位数据', description='No description here', tags=['用户基本数据接口'])
async def user_rank(commons: dict = Depends(user_rank_season_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_rank_season_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        season=commons['season']
    )
    log_db(22, result['status'], commons)
    return result


@app.get("/rank/ship/", summary='用户排位数据', description='No description here', tags=['用户基本数据接口'])
async def user_rank(commons: dict = Depends(user_rank_ship_parameter)):
    if commons['token'] not in config.TOKEN:
        return {'status': 'info', 'message': token_msg}
    result = await wws_rank_ship_data.main(
        aid=str(commons['aid']),
        server=commons['server'],
        ship_id=commons['ship_id']
    )
    log_db(22, result['status'], commons)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)

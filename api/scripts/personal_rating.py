from .update_db import get_ship_data


def get_personal_rating(
    ship_id: str,
    ship_data: list,
    battle_type: str
):
    '''
    计算pr数据
    ship_data [battles,wins,damage,frag]
    '''
    battles_count = ship_data[0]
    avg_damage = ship_data[2]/battles_count
    avg_wins = ship_data[1]/battles_count*100
    avg_frag = ship_data[3]/battles_count
    server_data = get_ship_data(ship_id=ship_id)
    if server_data == None:
        return {
            'value_battles_count': 0,
            'personal_rating': -1,
            'n_damage_dealt': -1,
            'n_frags': -1
        }
    if avg_damage > server_data[2]*0.4:
        n_damage = (avg_damage-server_data[2] * 0.4) / \
            (server_data[2]*0.6)
    else:
        n_damage = 0
    if avg_wins > server_data[1]*0.7:
        n_win_rate = (avg_wins-server_data[1]*0.7) / (server_data[1]*0.3)
    else:
        n_win_rate = 0
    if avg_frag > server_data[3]*0.1:
        n_kd = (avg_frag-server_data[3]*0.1)/(server_data[3]*0.9)
    else:
        n_kd = 0
    if battle_type == 'rank_solo':
        pr = 600*n_damage+350*n_kd+400*n_win_rate
    else:
        pr = 700*n_damage+300*n_kd+150*n_win_rate
    return {
        'value_battles_count': battles_count,
        'personal_rating': round(pr*battles_count, 6),
        'n_damage_dealt': round((avg_damage/server_data[2])*battles_count, 6),
        'n_frags': round((avg_frag/server_data[3])*battles_count, 6)
    }


def get_personal_rating_info(
    ship_id: str,
    ship_data: list,
    battle_type: str
):
    '''
    计算pr数据
    ship_data [battles,wins,damage,frag]
    '''
    battles_count = ship_data[0]
    avg_damage = ship_data[2]/battles_count
    avg_wins = ship_data[1]/battles_count*100
    avg_frag = ship_data[3]/battles_count
    server_data = get_ship_data(ship_id=ship_id)
    if server_data == None:
        return {
            'value_battles_count': 0,
            'personal_rating': -1,
            'n_damage_dealt': -1,
            'n_frags': -1,
            'nwin': 0,
            'ndmg': 0,
            'nfrag': 0,
            'swin': 0,
            'sdmg': 0,
            'sfrag': 0,
            'uwin': 0,
            'udmg': 0,
            'ufrag': 0
        }
    if avg_damage > server_data[2]*0.4:
        n_damage = (avg_damage-server_data[2] * 0.4) / \
            (server_data[2]*0.6)
    else:
        n_damage = 0
    if avg_wins > server_data[1]*0.7:
        n_win_rate = (avg_wins-server_data[1]*0.7) / (server_data[1]*0.3)
    else:
        n_win_rate = 0
    if avg_frag > server_data[3]*0.1:
        n_kd = (avg_frag-server_data[3]*0.1)/(server_data[3]*0.9)
    else:
        n_kd = 0
    if battle_type == 'rank_solo':
        pr = 600*n_damage+350*n_kd+400*n_win_rate
    else:
        pr = 700*n_damage+300*n_kd+150*n_win_rate
    return {
        'value_battles_count': battles_count,
        'personal_rating': round(pr*battles_count, 6),
        'n_damage_dealt': round((avg_damage/server_data[2])*battles_count, 6),
        'n_frags': round((avg_frag/server_data[3])*battles_count, 6),
        'nwin': int(150*n_win_rate),
        'ndmg': int(700*n_damage),
        'nfrag': int(300*n_kd),
        'swin': round(server_data[1], 2),
        'sdmg': round(server_data[2], 2),
        'sfrag': round(server_data[3], 2),
        'uwin': round(avg_wins, 2),
        'udmg': round(avg_damage, 2),
        'ufrag': round(avg_frag, 2),

    }

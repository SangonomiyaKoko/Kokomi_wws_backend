from dataclasses import dataclass


@dataclass
class json_index:
    keywords: str
    index: int


recent_json_index = [
    json_index('battles_count',                  0),
    json_index('wins',                           1),
    json_index('losses',                         2),
    json_index('damage_dealt',                   3),
    json_index('ships_spotted',                  4),
    json_index('frags',                          5),
    json_index('survived',                       6),
    json_index('scouting_damage',                7),
    json_index('original_exp',                   8),
    json_index('exp',                            9),
    json_index('art_agro',                      10),
    json_index('tpd_agro',                      11),
    json_index('win_and_survived',              12),
    json_index('control_dropped_points',        13),
    json_index('control_captured_points',       14),
    json_index('team_control_captured_points',  15),
    json_index('team_control_dropped_points',   16),
    json_index('planes_killed',                 17),
    json_index('frags_by_ram',                  18),
    json_index('frags_by_tpd',                  19),
    json_index('frags_by_planes',               20),
    json_index('frags_by_dbomb',                21),
    json_index('frags_by_atba',                 22),
    json_index('frags_by_main',                 23),
    json_index('hits_by_main',                  24),
    json_index('shots_by_main',                 25),
    json_index('hits_by_skip',                  26),
    json_index('shots_by_skip',                 27),
    json_index('hits_by_atba',                  28),
    json_index('shots_by_atba',                 29),
    json_index('hits_by_rocket',                30),
    json_index('shots_by_rocket',               31),
    json_index('hits_by_bomb',                  32),
    json_index('shots_by_bomb',                 33),
    json_index('hits_by_tpd',                   34),
    json_index('shots_by_tpd',                  35),
    json_index('hits_by_tbomb',                 36),
    json_index('shots_by_tbomb',                37),
]

ach_json_index = [
    json_index('PCH016_FirstBlood',              0),
    json_index('PCH004_Dreadnought',             1),
    json_index('PCH011_InstantKill',             2),
    json_index('PCH003_MainCaliber',             3),
    json_index('PCH005_Support',                 4),
    json_index('PCH006_Withering',               5),
    json_index('PCH023_Warrior',                 6),
    json_index('PCH010_Retribution',             7),
    json_index('PCH017_Fireproof',               8),
    json_index('PCH012_Arsonist',                9),
    json_index('PCH020_ATBACaliber',            10),
    json_index('PCH001_DoubleKill',             11),
    json_index('PCH174_AirDefenseExpert',       12),
    json_index('PCH019_Detonated',              13),
    json_index('PCH014_Headbutt',               14),
    json_index('PCH002_OneSoldierInTheField',   15),
    json_index('PCH018_Unsinkable',             16),
    json_index('PCH395_CombatRecon',            17),
    json_index('PCH366_Warrior_Squad',          18),
    json_index('PCH367_Support_Squad',          19),
    json_index('PCH368_Frag_Squad',             20),
    json_index('PCH364_MainCaliber_Squad',      21),
    json_index('PCH365_ClassDestroy_Squad',     22)
]

ach_index_dict = {
    4277330864: 'PCH016_FirstBlood',
    4289913776: 'PCH004_Dreadnought',
    4282573744: 'PCH011_InstantKill',
    4290962352: 'PCH003_MainCaliber',
    4288865200: 'PCH005_Support',
    4287816624: 'PCH006_Withering',
    4269990832: 'PCH023_Warrior',
    4283622320: 'PCH010_Retribution',
    4276282288: 'PCH017_Fireproof',
    4281525168: 'PCH012_Arsonist',
    4273136560: 'PCH020_ATBACaliber',
    4293059504: 'PCH001_DoubleKill',
    4111655856: 'PCH174_AirDefenseExpert',
    4274185136: 'PCH019_Detonated',
    4279428016: 'PCH014_Headbutt',
    4292010928: 'PCH002_OneSoldierInTheField',
    4275233712: 'PCH018_Unsinkable',
    3879920560: 'PCH395_CombatRecon',
    3910329264: 'PCH366_Warrior_Squad',
    3909280688: 'PCH367_Support_Squad',
    3908232112: 'PCH368_Frag_Squad',
    3912426416: 'PCH364_MainCaliber_Squad',
    3911377840: 'PCH365_ClassDestroy_Squad'
}

server_list = {
    'asia': 'http://vortex.worldofwarships.asia',
    'eu': 'http://vortex.worldofwarships.eu',
    'na': 'http://vortex.worldofwarships.com',
    'ru': 'http://vortex.korabli.su',
    'cn': 'http://vortex.wowsgame.cn'
}
clan_server_list = {
    'asia': 'https://clans.worldofwarships.asia',
    'eu': 'https://clans.worldofwarships.eu',
    'na': 'https://clans.worldofwarships.com',
    'ru': 'https://clans.worldofwarships.ru',
    'cn': 'https://clans.wowsgame.cn'
}
api_server_list = {
    'asia': 'https://api.worldofwarships.asia',
    'eu': 'https://api.worldofwarships.eu',
    'na': 'https://api.worldofwarships.com',
    'ru': '',
    'cn': ''
}

useless_index_list = [
    'damage_dealt_to_buildings',
    'max_damage_dealt_to_buildings',
    'max_premium_exp',
    'premium_exp',
    'dropped_capture_points',
    'capture_points',
    'max_suppressions_count',
    'suppressions_count',
    'battles_count_0910',
    'battles_count_078',
    'battles_count_0711',
    'battles_count_512',
    'battles_count_510',
]
base_index_list = [
    'battles_count',                 # 战斗总数
    'wins',                          # 胜利场数
    'losses',                        # 失败场数
    'damage_dealt',                  # 总伤害
    'ships_spotted',                 # 船只侦查数
    'frags',                         # 总击杀数
    'survived',                      # 存活的场数
    'scouting_damage',               # 总侦查伤害
    'original_exp',                  # 总经验（无高账加成）
    'exp',                           # 经验（大概是包括所有模式的总经验，虽然没啥用，但留着吧）
    'art_agro',                      # 总潜在伤害
    'tpd_agro',                      # 总鱼雷潜在伤害
    'win_and_survived',              # 胜利并存活场数
    'control_dropped_points',        # 总防御点数
    'control_captured_points',       # 总占领点数
    'team_control_captured_points',  # 团队总占领点数
    'team_control_dropped_points',   # 团队总防御点数
    'planes_killed',                 # 总飞机击落数

]
useful_index_list = [
    # 基本数据
    'battles_count',                 # 战斗总数
    'wins',                          # 胜利场数
    'losses',                        # 失败场数
    'damage_dealt',                  # 总伤害
    'ships_spotted',                 # 船只侦查数
    'frags',                         # 总击杀数
    'survived',                      # 存活的场数
    'scouting_damage',               # 总侦查伤害
    'original_exp',                  # 总经验（无高账加成）
    'exp',                           # 经验（大概是包括所有模式的总经验，虽然没啥用，但留着吧）
    'art_agro',                      # 总潜在伤害
    'tpd_agro',                      # 总鱼雷潜在伤害
    'win_and_survived',              # 胜利并存活场数
    'control_dropped_points',        # 总防御点数
    'control_captured_points',       # 总占领点数
    'team_control_captured_points',  # 团队总占领点数
    'team_control_dropped_points',   # 团队总防御点数
    'planes_killed',                 # 总飞机击落数

    # 最大记录
    'max_frags_by_planes',           # 最多通过飞机击杀数
    'max_total_agro',                # 最多潜在伤害
    'max_ships_spotted',             # 最多船只侦查数
    'max_frags_by_ram',              # 最多冲撞击杀
    'max_scouting_damage',           # 最大侦查伤害
    'max_frags_by_dbomb',            # 最多深水炸弹击杀
    'max_frags_by_main',             # 最多主炮击杀
    'max_planes_killed',             # 最多飞机击落
    'max_damage_dealt',              # 最大伤害
    'max_frags_by_tpd',              # 最多鱼雷击杀
    'max_exp',                       # 最多经验（无高账加成）
    'max_frags_by_atba',             # 最多副炮击杀数
    'max_frags',                     # 最多击杀数

    # 武器击杀数据
    'frags_by_ram',                  # 冲撞击杀数
    'frags_by_tpd',                  # 鱼雷击杀数
    'frags_by_planes',               # 通过飞机击杀数
    'frags_by_dbomb',                # 深水炸弹的击杀数
    'frags_by_atba',                 # 副炮击杀数
    'frags_by_main',                 # 主炮击杀数
    # 通过起火或进水击杀 = 总击杀 - 上面的累加

    # 武器命中数据
    'hits_by_main',                  # 命中的主炮数
    'shots_by_main',                 # 发射的主炮数
    'hits_by_skip',                  # 命中的跳弹数
    'shots_by_skip',                 # 发射的跳弹数
    'hits_by_atba',                  # 命中的副炮数
    'shots_by_atba',                 # 发射的副炮数
    'hits_by_rocket',                # 命中的火箭弹数
    'shots_by_rocket',               # 发射的火箭弹数
    'hits_by_bomb',                  # 命中的炸弹数
    'shots_by_bomb',                 # 投掷的炸弹数
    'hits_by_tpd',                   # 命中的鱼雷数
    'shots_by_tpd',                  # 发射的鱼雷数
    'hits_by_tbomb',                 # 命中的空袭炸弹数
    'shots_by_tbomb',                # 投掷的空袭炸弹数
]

cw_achievement = {
    '0': [
        3942835120,
        3944932272,
        3947029424,
        3949126576,
        3951223728,
        3953320880,
        3884114864,
        3968000944,
        3959612336,
        3961709488,
        3963806640,
        3980583856,
        3997361072,
        4014138288,
        4021478320,
        4025672624,
        4030915504,
        4036158384,
        4039304112,
        4049789872,
        4073907120,
        4092781488,
        4108510128,
        4109558704

    ],
    '1': [4128433072],
    '2': [4127384496],
    '3': [4126335920],
    '4': [4125287344]
}

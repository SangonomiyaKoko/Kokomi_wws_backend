
async def user_basic_parameters(
        token: str,
        aid: int,
        server: str,
        use_ac: bool = False,
        ac: str = None
):
    return {
        "token": token,
        "aid": aid,
        "server": server,
        "use_ac": use_ac,
        "ac": ac
    }


async def user_bind_parameters(
        token: str,
        user_id: str,
        aid: int,
        server: str,
        platform: str
):
    return {
        "token": token,
        "user_id": user_id,
        "aid": aid,
        "server": server,
        "platform": platform
    }


async def user_search_parameters(
        token: str,
        name: str,
        server: str
):
    return {
        "token": token,
        "name": name,
        "server": server
    }


async def user_platform_parameters(
        token: str,
        user_id: str,
        platform: str
):
    return {
        "token": token,
        "user_id": user_id,
        "platform": platform
    }


async def user_recent_parameters(
        token: str,
        aid: int,
        server: str,
        date: str,
        today: str,
        use_ac: bool = False,
        ac: str = None
):
    return {
        "token": token,
        "aid": aid,
        "server": server,
        "date": date,
        "today": today,
        "use_ac": use_ac,
        "ac": ac
    }


async def user_me_rank_parameter(
        token: str,
        aid: str,
        server: str,
        ship_id: str
):
    return {
        "token": token,
        "aid": aid,
        "server": server,
        "ship_id": ship_id
    }


async def user_server_rank_parameter(
        token: str,
        server: str,
        ship_id: str
):
    return {
        "token": token,
        "server": server,
        "ship_id": ship_id
    }


async def user_select_ship_parameter(
        token: str,
        aid: str,
        server: str,
        select: str,
        use_ac: bool = False,
        ac: str = None
):
    return {
        "token": token,
        "aid": aid,
        "server": server,
        "select": select,
        "use_ac": use_ac,
        "ac": ac
    }


async def user_single_ship_parameter(
        token: str,
        aid: str,
        server: str,
        ship_id: str,
        use_ac: bool = False,
        ac: str = None
):
    return {
        "token": token,
        "aid": aid,
        "server": server,
        "ship_id": ship_id,
        "use_ac": use_ac,
        "ac": ac
    }


async def clan_parameter(
        token: str,
        clan_id: str,
        server: str
):
    return {
        "token": token,
        "clan_id": clan_id,
        "server": server
    }


async def clan_season_parameter(
        token: str,
        clan_id: str,
        cvc_season: str,
        server: str
):
    return {
        "token": token,
        "clan_id": clan_id,
        "cvc_season": cvc_season,
        "server": server
    }


async def user_clan_parameter(
        token: str,
        aid: str,
        server: str
):
    return {
        "token": token,
        "aid": aid,
        "server": server
    }


async def clan_search_parameter(
        token: str,
        clan_name: str,
        server: str
):
    return {
        "token": token,
        "clan_name": clan_name,
        "server": server
    }


async def uid_parameter(
        token: str,
        uid: str
):
    return {
        "token": token,
        "uid": uid
    }


async def token_parameter(
        token: str
):
    return {
        "token": token
    }


async def ship_server_parameter(
        token: str,
        select: str
):
    return {
        "token": token,
        "select": select
    }


async def user_pr_parameters(
        token: str,
        user_id: str,
        use_pr: bool,
        platform: str
):
    return {
        "token": token,
        "user_id": user_id,
        "use_pr": use_pr,
        "platform": platform
    }


async def user_rank_ship_parameter(
        token: str,
        aid: str,
        server: str,
        ship_id: str
):
    return {
        "token": token,
        "aid": aid,
        "server": server,
        "ship_id": ship_id
    }


async def user_rank_season_parameter(
        token: str,
        aid: str,
        server: str,
        season: str
):
    return {
        "token": token,
        "aid": aid,
        "server": server,
        "season": season
    }

from ..apis.gateway_api import get

version="v1"

async def getLeaderboard(baseUrl: str, seasonId: str, teamMode: str, apiKey: str):
    """"Get Global Leaderboard for a specific game mode and season from API"""
    if teamMode.isnumeric and seasonId.isnumeric:
        data: list = await get(url=f"{baseUrl}/{version}/rank/top/{seasonId}/{teamMode}", headers={'x-api-key' : apiKey})
        chunks:list = []
        parsedData = parseLeaderboard(data['topRanks'])
        i = 0
        while i < len(parsedData):
            chunks.append(''.join(parsedData[i:i+25]))
            i+=25
        return chunks
    return []

async def getUserRank(baseUrl:str, nickname: str, seasonId: str, teamMode: str, apiKey: str):
    """"Get the passed in nickname's rank from API"""
    user = await getUser(baseUrl=baseUrl, nickname=nickname, apiKey=apiKey)
    userNum = user['userNum']
    if userNum:
        dataRank = await get(url=f"{baseUrl}/{version}/rank/{userNum}/{seasonId}/{teamMode}", headers={'x-api-key' : apiKey})
        if dataRank:
            return dataRank['userRank']['rank']
    else:
        return ''

async def getUser(baseUrl:str, nickname: str, apiKey: str):
    """"Get the passed in nicknames base information from API"""
    data = await get(url=f"{baseUrl}/{version}/user/nickname?query={nickname}", headers={'x-api-key': apiKey})
    if not data['code'] == 404: 
        return data['user']
    else: 
        return ''

async def getMatchHistory(baseUrl:str, userId: str, apiKey: str):
    """Gets the user's match history"""
    data = await get(url=f"{baseUrl}/{version}/user/games/{userId}", headers={'x-api-key': apiKey})
    if not data['code'] == 404:
        return data['userGames']
    else:
        return ''

def parseLeaderboard(data: list):
    """"Helper function for getLeaderboard that returns a list of formatted strings"""
    temp: list = []
    for player in data:
        temp.append(f"Rank {player['rank']}: {player['nickname']}\n")
    return temp

def gameModeSwitch(mode: any):
    """"General Helper function that takes in a string and matches it to a number if in the switch"""
    if type(mode) == str:
        modeName = mode.lower()
        switcher = {
        'solo': '1',
        'solos': '1',
        'duo': '2',
        'duos': '2',
        'squads': '3',
        'squad': '3'
        }
        return switcher.get(modeName, '')
    elif type(mode) == int:
        modeName = str(mode)
        switcher = {
        "1": 'Solo',
        "2": 'Duos',
        "3": 'Squads'
        }
        return switcher.get(modeName, '')

    
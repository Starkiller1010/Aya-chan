from ..apis.erbs_api import get

version="v1"

async def getLeaderboard(baseUrl: str, seasonId: str, teamMode: str, apiKey: str):
    if teamMode.isnumeric and seasonId.isnumeric:
        data: list = await get(url=f"{baseUrl}/{version}/rank/top/{seasonId}/{teamMode}", apiKey=apiKey)
        chunks:list = []
        parsedData = parseLeaderboard(data['topRanks'])
        chunks.append(''.join(parsedData[0:25]))
        chunks.append(''.join(parsedData[25:50]))
        chunks.append(''.join(parsedData[50:75]))
        chunks.append(''.join(parsedData[75:100]))
        return chunks
    return []

async def getUserRank(baseUrl:str, nickname: str, seasonId: str, teamMode: str, apiKey: str):
    user = await getUser(baseUrl=baseUrl, nickname=nickname, apiKey=apiKey)
    userNum = user['userNum']
    if userNum:
        dataRank = await get(url=f"{baseUrl}/{version}/rank/{userNum}/{seasonId}/{teamMode}", apiKey=apiKey)
        if dataRank:
            return dataRank['userRank']['rank']
    else:
        return ''

async def getUser(baseUrl:str, nickname: str, apiKey: str):
    data = await get(url=f"{baseUrl}/{version}/user/nickname?query={nickname}", apiKey=apiKey)
    print(data)
    if not data['code'] == 404: 
        return data['user']
    else: 
        return ''

def parseLeaderboard(data: list):
    temp: list = []
    for player in data:
        temp.append(f"Rank {player['rank']}: {player['nickname']}\n")
    return temp

def gameModeSwitch(modeName: str):
    modeName = modeName.lower()
    switcher = {
       'solo': '1',
       'solos': '1',
       'duo': '2',
       'duos': '2',
       'squads': '3',
       'squad': '3'
    }
    return switcher.get(modeName, '')

    
from src.apis.erbs_api import *

version="v1"

async def getLeaderboard(baseUrl: str, seasonId: str, teamMode: str, apiKey: str):
    if teamMode.isnumeric and seasonId.isnumeric:
        data: list = await get(f"{baseUrl}/{version}/rank/top/{seasonId}/{teamMode}", apiKey)
        chunks:list = []
        parsedData = parseLeaderboard(data)
        chunks.append(''.join(parsedData[0:25]))
        chunks.append(''.join(parsedData[25:50]))
        chunks.append(''.join(parsedData[50:75]))
        chunks.append(''.join(parsedData[75:100]))
        return chunks
    return []


def parseLeaderboard(data: list):
    temp: list = []
    for player in data:
        temp.append(f"Rank {player['rank']}: {player['nickname']}\n")
    return temp
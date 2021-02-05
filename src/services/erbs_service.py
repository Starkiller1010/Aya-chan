import json
import os
from ..apis.gateway_api import get
import sys
import collections

version="v1"
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

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

async def getMatchHistory(baseUrl:str, userId: str, apiKey: str, nextId: str = ''):
    """Gets the user's match history"""
    data: []
    if not nextId and nextId.isnumeric:
        data = await get(url=f"{baseUrl}/{version}/user/games/{userId}", headers={'x-api-key': apiKey})
    else:
        data = await get(url=f"{baseUrl}/{version}/user/games/{userId}?next={nextId}", headers={'x-api-key': apiKey})
    if not data['code'] == 404:
        return data
    else:
        return ''

async def findGameStats(matchHistory: dict, gameId: int):
    """Helper function for getUsersMatchStats that collects stats from Match History"""
    # url = 'https://open-api.bser.io/v1/data/'
    #TODO Need to dynamically create/update jsons being used
    # with open('D:/VegaG/Downloads/response_1611102330348.json', encoding='utf-8') as testJson:
    #     matchHistory = json.load(testJson)
    for match in matchHistory['userGames']:
        result = {}
        if match['gameId'] == gameId:
            skills = match['skillLevelInfo']

            result['character'] = findCharacter(match['characterNum'])
            result['kills'] = match['playerKill']
            result['assists'] = match['playerAssistant']
            result['id'] = match['gameId']
            result['level'] = match['characterLevel']
            result['placement'] = match['gameRank']
            result['hunts'] = match['monsterKill']
            result['maxHp'] = match['maxHp']
            result['maxSp'] = match['maxSp']
            result["attackPower"] = match['attackPower']
            result["defense"] = match['defense']
            result["hpRegen"] = match['hpRegen']
            result["spRegen"] = match['spRegen']
            result["attackSpeed"] = match['attackSpeed']
            result["moveSpeed"] = match['moveSpeed']
            result["outOfCombatMoveSpeed"] = match['outOfCombatMoveSpeed']
            result["sightRange"] = match['sightRange']
            result["attackRange"] = match['attackRange']
            result["criticalStrikeChance"] = match['criticalStrikeChance']
            result["criticalStrikeDamage"] = match['criticalStrikeDamage']
            result["coolDownReduction"] = match['coolDownReduction']
            result["lifeSteal"] = match['lifeSteal']

            result['mode'] = gameModeSwitch(match['matchingTeamMode'])
            result['masteryLevels'] = parseMastery(match['masteryLevel'])
            
            if '0' in match['equipment']:
                result['weapon'] = findEquipment(match['equipment']['0'], True)
            else: 
                result['weapon'] = 'N/A'
            if '1' in match['equipment']:
                result['chest'] = findEquipment(match['equipment']['1'])
            else: 
                result['chest'] = 'N/A'
            if '2' in match['equipment']:
                result['head'] = findEquipment(match['equipment']['2'])
            else: 
                result['head'] = 'N/A'
            if '3' in match['equipment']:
                result['gloves'] = findEquipment(match['equipment']['3'])
            else: 
                result['gloves'] = 'N/A'
            if '4' in match['equipment']:
                result['boots'] = findEquipment(match['equipment']['4'])
            else: 
                result['boots'] = 'N/A'
            if '5' in match['equipment']:
                result['accessory'] = findEquipment(match['equipment']['5'])
            else: 
                result['accessory'] = 'N/A'

            result['skillNames'] = findSkillNames(result['character'], skills)
            result['skillLevels'] = match['skillLevelInfo']

            result['skillLevelOrder'] = parseSkillOrder(match['skillOrderInfo'], result['skillNames'], list(skills.keys()), result['level'])


            return result
    return ''

def findSkillNames(characterName: str, skills: []):
    with open(os.path.join(__location__, '../resources/lookup/skillgroups.json'), encoding='utf-8') as b:
        groups = json.load(b)
    result = {}
    for skill in groups['data']:
        id:str = skill['skillId']
        passiveId:str = skill['passiveSkillId']
        if characterName in id:
            if 'Active1' in id:
                # result['Q'] = skill['name']
                result[skill['representGroup']] = 'Q'
                continue
            elif 'Active2' in id:
                # result['Q'] = skill['name']
                result[skill['representGroup']] = 'W'
                continue
            elif 'Active3' in id:
                # result['Q'] = skill['name']
                result[skill['representGroup']] = 'E'
                continue
            elif 'Active4' in id:
                # result['Q'] = skill['name']
                result[skill['representGroup']] = 'R'
                continue
        elif characterName in passiveId:
                # result['P'] = skill['name']
                result[skill['representGroup']] = 'P'
                continue
    values = list(result.keys())
    for skill in skills:
        if not values.__contains__(int(skill)):
            result[int(skill)] = 'D'
    return result

def findCharacter(charNum: int):
    with open(os.path.join(__location__, '../resources/lookup/characters.json'), encoding='utf-8') as c:
        characters = json.load(c)
    for character in characters['data']:
        if character['code'] == charNum:
            return character['name']
    return str(charNum)

def findEquipment(code: int, isWeapon: bool = False):
    with open(os.path.join(__location__, '../resources/lookup/itemNames.json'), encoding='utf-8') as a:
        inv_names = json.load(a)
        names = {v: k for k, v in inv_names.items()}
    if not isWeapon:
        with open(os.path.join(__location__, '../resources/lookup/armors.json'), encoding='utf-8') as b:
            equipments = json.load(b)
    else:
        with open(os.path.join(__location__, '../resources/lookup/weapons.json'), encoding='utf-8') as c:
            equipments = json.load(c)
    for equipment in equipments['data']:
        if equipment['code'] == code:
            if names[code]:
                return names[code]
            else:
                return equipment['name']
    return str(code)
                
def parseMastery(masteryLevels: dict):
    with open(os.path.join(__location__, '../resources/lookup/masteryCodes.json'), encoding='utf-8') as a:
        masteries = json.load(a)
    result = {}
    for code in masteryLevels:
        for key in masteries:
            if code == key:
                result[masteries[key]] = masteryLevels[code]
                break
    return result

def parseSkillOrder(skillLevels: dict, skillNames:{}, skills: [], levels: int):
    table = {"L":'|'}
    indices = list(skillNames.values())
    for x in range(len(skillNames)):
        table[indices[x]] = "|"
    i = 1
    while(i <= levels):
        table["L"] = table["L"] + f"{i%10}|"
        for x in range(len(skills)):
            if skillLevels[str(i)] == int(skills[x]):
                table[skillNames[int(skills[x])]] = table[skillNames[int(skills[x])]] + 'X|'
            else:
                table[skillNames[int(skills[x])]] = table[skillNames[int(skills[x])]] + ' |'
        i+=1
    for row in table:
        table[row] = table[row] + '\n'
    return table
    
    

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

    
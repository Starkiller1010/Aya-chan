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
                result['weapon'] = findEquipmentName(match['equipment']['0'], True)
            else: 
                result['weapon'] = 'N/A'
            if '1' in match['equipment']:
                result['chest'] = findEquipmentName(match['equipment']['1'])
            else: 
                result['chest'] = 'N/A'
            if '2' in match['equipment']:
                result['head'] = findEquipmentName(match['equipment']['2'])
            else: 
                result['head'] = 'N/A'
            if '3' in match['equipment']:
                result['gloves'] = findEquipmentName(match['equipment']['3'])
            else: 
                result['gloves'] = 'N/A'
            if '4' in match['equipment']:
                result['boots'] = findEquipmentName(match['equipment']['4'])
            else: 
                result['boots'] = 'N/A'
            if '5' in match['equipment']:
                result['accessory'] = findEquipmentName(match['equipment']['5'])
            else: 
                result['accessory'] = 'N/A'

            result['skillNames'] = findSkillNames(result['character'], skills)
            result['skillLevels'] = match['skillLevelInfo']

            result['skillLevelOrder'] = parseSkillOrder(match['skillOrderInfo'], result['skillNames'], list(skills.keys()), result['level'])


            return result
    return ''

async def findItem(itemName: str):
    code = findItemCode(item=itemName)
    item = []
    if code:
        item = findEquipment(code[0], True)
        if not item:
            item = findEquipment(code[0])
        if not item:
            item = findMiscItem(code=code[0])
        item['name'] = code[1]
    return item

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

def findEquipmentName(code: int, isWeapon: bool = False):
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

def findEquipment(code: int, isWeapon: bool = False):
    if not isWeapon:
        with open(os.path.join(__location__, '../resources/lookup/armors.json'), encoding='utf-8') as b:
            equipments = json.load(b)
    else:
        with open(os.path.join(__location__, '../resources/lookup/weapons.json'), encoding='utf-8') as c:
            equipments = json.load(c)
    for equipment in equipments['data']:
        if equipment['code'] == code:
            return equipment
    return []

def findMiscItem(code: int):
    with open(os.path.join(__location__, '../resources/lookup/miscItems.json'), encoding='utf-8') as a:
            items = json.load(a)
    for item in items['data']:
        if item['code'] == code:
            return item
    return str(code)

def findItemCode(item: str):
    nonFormattedName = item.split(' ')
    name = ''
    if len(nonFormattedName) > 1:
        for part in nonFormattedName:
            name = name.__add__(part.capitalize())
    else:
        name = nonFormattedName[0]
    with open(os.path.join(__location__, '../resources/lookup/itemNames.json'), encoding='utf-8') as a:
        inv_names = json.load(a)
    if name in inv_names:
        return [inv_names[name], name]
    else:
        return name
                
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

def parseItem(item: dict):
    if item['itemType'] == 'Weapon':
        return [("Name: ", f"```{item['name']}```", False),
                ("Type: ", f"```{item['itemType']}```", True),
                ("Rarity: ", f"```{item['itemGrade']}```", True),
                ("Category: ", f"```{item['weaponType']}```", True),
                ("Atk Power: ", f"```{item['attackPower']}```", True),
                ("Defense: ", f"```{item['defense']}```", True),
                ("Max Hp: ", f"```{item['maxHp']}```", True),
                ("HP Regen: ", f"```{item['hpRegen']}```", True),
                ("SP Regen: ", f"```{item['spRegen']}```", True),
                ("HP Regen %: ", f"```{item['hpRegenRatio']}```", True),
                ("SP Regen %: ", f"```{item['spRegenRatio']}```", True),
                ("Attack Speed %: ", f"```{item['attackSpeedRatio']}```", True),
                ("Crit Chance: ", f"```{item['criticalStrikeChance']}```", True),
                ("Crit Damage: ", f"```{item['criticalStrikeDamage']}```", True),
                ("Cooldown Reduction: ", f"```{item['cooldownReduction']}```", True),
                ("Life Steal: ", f"```{item['lifeSteal']}```", True),
                ("Move Speed: ", f"```{item['moveSpeed']}```", True),
                ("Sight Range: ", f"```{item['sightRange']}```", True),
                ("Attack Range: ", f"```{item['attackRange']}```", True),
                ("ENAD: ", f"```{item['increaseBasicAttackDamage']}```", True),
                ("Skill Damage: ", f"```{item['increaseSkillDamage']}```", True),
                ("Skill Damage %: ", f"```{item['increaseSkillDamageRatio']}```", True),
                ("Healing Reduction(Attack): ", f"```{item['decreaseRecoveryToBasicAttack']}```", True),
                ("Healing Reduction(Spell): ", f"```{item['decreaseRecoveryToSkill']}```", True)]
    elif item['itemType'] == 'Armor':
        return [("Name: ", f"```{item['name']}```", False),
                ("Type: ", f"```{item['itemType']}```", True),
                ("Rarity: ", f"```{item['itemGrade']}```", True),
                ("Category: ", f"```{item['armorType']}```", True),
                ("Atk Power: ", f"```{item['attackPower']}```", True),
                ("Defense: ", f"```{item['defense']}```", True),
                ("Max Hp: ", f"```{item['maxHp']}```", True),
                ("HP Regen: ", f"```{item['hpRegen']}```", True),
                ("SP Regen: ", f"```{item['spRegen']}```", True),
                ("HP Regen %: ", f"```{item['hpRegenRatio']}```", True),
                ("SP Regen %: ", f"```{item['spRegenRatio']}```", True),
                ("Attack Speed %: ", f"```{item['attackSpeedRatio']}```", True),
                ("Crit Chance: ", f"```{item['criticalStrikeChance']}```", True),
                ("Crit Damage: ", f"```{item['criticalStrikeDamage']}```", True),
                ("Cooldown Reduction: ", f"```{item['cooldownReduction']}```", True),
                ("Life Steal: ", f"```{item['lifeSteal']}```", True),
                ("Move Speed: ", f"```{item['moveSpeed']}```", True),
                ("Move Speed(Out of Combat): ", f"```{item['outOfCombatMoveSpeed']}```", True),
                ("Sight Range: ", f"```{item['sightRange']}```", True),
                ("Attack Range: ", f"```{item['attackRange']}```", True),
                ("ENAD: ", f"```{item['increaseBasicAttackDamage']}```", True),
                ("Skill Damage: ", f"```{item['increaseSkillDamage']}```", True),
                ("Skill Damage %: ", f"```{item['increaseSkillDamageRatio']}```", True),
                ("Healing Reduction(Attack): ", f"```{item['decreaseRecoveryToBasicAttack']}```", True),
                ("Healing Reduction(Spell): ", f"```{item['decreaseRecoveryToSkill']}```", True),
                ("Crit Damage Reduction", f"```{item['preventCriticalStrikeDamaged']}```", True),
                ("Attack Reduction: ", f"```{item['preventBasicAttackDamaged']}```", True),
                ("Spell Reduction: ", f"```{item['preventSkillDamagedRatio']}```", True)]
    elif item['itemType'] == 'Misc':
        return [("Name: ", f"```{item['name']}```", False),
                ("Type: ", f"```{item['itemType']}```", True),
                ("Rarity: ", f"```{item['itemGrade']}```", True),
                ("Stack Size: ", f"```{item['stackable']}```", True),
                ("Pick-up Amount: ", f"```{item['initialCount']}```", True)]
    else:
        return []

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
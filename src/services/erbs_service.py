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
                result['weapon'] = findItemName(match['equipment']['0'], True)
            else: 
                result['weapon'] = 'N/A'
            if '1' in match['equipment']:
                result['chest'] = findItemName(match['equipment']['1'])
            else: 
                result['chest'] = 'N/A'
            if '2' in match['equipment']:
                result['head'] = findItemName(match['equipment']['2'])
            else: 
                result['head'] = 'N/A'
            if '3' in match['equipment']:
                result['gloves'] = findItemName(match['equipment']['3'])
            else: 
                result['gloves'] = 'N/A'
            if '4' in match['equipment']:
                result['boots'] = findItemName(match['equipment']['4'])
            else: 
                result['boots'] = 'N/A'
            if '5' in match['equipment']:
                result['accessory'] = findItemName(match['equipment']['5'])
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
        if not item:
            item = findConsumable(code[0])
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

def findItemName(code: int, isWeapon: bool = False, isMisc: bool = False, isConsumable: bool = False):
    with open(os.path.join(__location__, '../resources/lookup/itemNames.json'), encoding='utf-8') as a:
        inv_names = json.load(a)
        names = {v: k for k, v in inv_names.items()}
    if isWeapon:
        with open(os.path.join(__location__, '../resources/lookup/weapons.json'), encoding='utf-8') as c:
            items = json.load(c)
    elif isMisc:
        with open(os.path.join(__location__, '../resources/lookup/miscItems.json'), encoding='utf-8') as d:
            items = json.load(d)
    elif isConsumable:
         with open(os.path.join(__location__, '../resources/lookup/consumables.json'), encoding='utf-8') as e:
            items = json.load(e)
    else:
        with open(os.path.join(__location__, '../resources/lookup/armors.json'), encoding='utf-8') as b:
            items = json.load(b)
    for item in items['data']:
        if item['code'] == code:
            if code in names:
                return names[code]
            else:
                return item['name']
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
    return []

def findConsumable(code: int):
    with open(os.path.join(__location__, '../resources/lookup/consumables.json'), encoding='utf-8') as a:
            items = json.load(a)
    for item in items['data']:
        if item['code'] == code:
            return item
    return []

def findItemCode(item: str):
    nonFormattedName = item.split(' ')
    name = ''
    if len(nonFormattedName) > 1:
        for part in nonFormattedName:
            name = name.__add__(part.capitalize())
    else:
        name = nonFormattedName[0].capitalize()
    with open(os.path.join(__location__, '../resources/lookup/itemNames.json'), encoding='utf-8') as a:
        inv_names: dict = json.load(a)
    if name in inv_names:
        return [inv_names[name], name]
    else:
        return ''
                
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

def parseWeapon(item: dict):
    tempArr: list = []
    tempArr.append(("Name: ", f"```{item['name']}```", False))
    tempArr.append(("Type: ", f"```{item['itemType']}```", True))
    tempArr.append(("Rarity: ", f"```{item['itemGrade']}```", True))
    tempArr.append(("Category: ", f"```{item['weaponType']}```", True))
    if item['attackPower'] != 0:
        tempArr.append(("Atk Power: ", f"```{item['attackPower']}```", True))
    if item['defense'] != 0:
        tempArr.append(("Defense: ", f"```{item['defense']}```", True))
    if item['maxHp'] != 0:
        tempArr.append(("Max Hp: ", f"```{item['maxHp']}```", True))
    if item['hpRegen'] != 0:
        tempArr.append(("HP Regen: ", f"```{item['hpRegen']}```", True))
    if item['spRegen'] != 0:
        tempArr.append(("SP Regen: ", f"```{item['spRegen']}```", True))
    if item['hpRegenRatio'] != 0:
        tempArr.append(("HP Regen %: ", f"```{item['hpRegenRatio']}```", True))
    if item['spRegenRatio'] != 0:
        tempArr.append(("SP Regen %: ", f"```{item['spRegenRatio']}```", True))
    if item['attackSpeedRatio'] != 0:
        tempArr.append(("Attack Speed %: ", f"```{item['attackSpeedRatio']}```", True))
    if item['criticalStrikeChance'] != 0:
        tempArr.append(("Crit Chance: ", f"```{item['criticalStrikeChance']}```", True))
    if item['criticalStrikeDamage'] !=0:
        tempArr.append(("Crit Damage: ", f"```{item['criticalStrikeDamage']}```", True))
    if item['cooldownReduction'] !=0:
        tempArr.append(("Cooldown Reduction: ", f"```{item['cooldownReduction']}```", True))
    if item['lifeSteal'] !=0:
        tempArr.append(("Life Steal: ", f"```{item['lifeSteal']}```", True))
    if item['moveSpeed'] !=0:
        tempArr.append(("Move Speed: ", f"```{item['moveSpeed']}```", True))
    if item['sightRange'] !=0:
        tempArr.append(("Sight Range: ", f"```{item['sightRange']}```", True))
    if item['attackRange'] !=0:
        tempArr.append(("Attack Range: ", f"```{item['attackRange']}```", True))
    if item['increaseBasicAttackDamage'] !=0:
        tempArr.append(("ENAD: ", f"```{item['increaseBasicAttackDamage']}```", True))
    if item['increaseSkillDamage'] !=0:
        tempArr.append(("Skill Damage: ", f"```{item['increaseSkillDamage']}```", True))
    if item['increaseSkillDamageRatio'] !=0:
        tempArr.append(("Skill Damage %: ", f"```{item['increaseSkillDamageRatio']}```", True))
    if item['decreaseRecoveryToBasicAttack'] !=0:
        tempArr.append(("Healing Reduction(Attack): ", f"```{item['decreaseRecoveryToBasicAttack']}```", True))
    if item['decreaseRecoveryToSkill'] !=0:
        tempArr.append(("Healing Reduction(Spell): ", f"```{item['decreaseRecoveryToSkill']}```", True))
    return tempArr


def parseArmor(item: dict):
    tempArr: list = []
    tempArr.append(("Name: ", f"```{item['name']}```", False))
    tempArr.append(("Type: ", f"```{item['itemType']}```", True))
    tempArr.append(("Rarity: ", f"```{item['itemGrade']}```", True))
    tempArr.append(("Category: ", f"```{item['armorType']}```", True))
    if item['attackPower'] != 0:
        tempArr.append(("Atk Power: ", f"```{item['attackPower']}```", True))
    if item['defense'] != 0:
        tempArr.append(("Defense: ", f"```{item['defense']}```", True))
    if item['maxHp'] != 0:
        tempArr.append(("Max Hp: ", f"```{item['maxHp']}```", True))
    if item['hpRegen'] != 0:
        tempArr.append(("HP Regen: ", f"```{item['hpRegen']}```", True))
    if item['spRegen'] != 0:
        tempArr.append(("SP Regen: ", f"```{item['spRegen']}```", True))
    if item['hpRegenRatio'] != 0:
        tempArr.append(("HP Regen %: ", f"```{item['hpRegenRatio']}```", True))
    if item['spRegenRatio'] != 0:
        tempArr.append(("SP Regen %: ", f"```{item['spRegenRatio']}```", True))
    if item['attackSpeedRatio'] != 0:
        tempArr.append(("Attack Speed %: ", f"```{item['attackSpeedRatio']}```", True))
    if item['criticalStrikeChance'] != 0:
        tempArr.append(("Crit Chance: ", f"```{item['criticalStrikeChance']}```", True))
    if item['criticalStrikeDamage'] != 0:
        tempArr.append(("Crit Damage: ", f"```{item['criticalStrikeDamage']}```", True))
    if item['cooldownReduction'] != 0:
        tempArr.append(("Cooldown Reduction: ", f"```{item['cooldownReduction']}```", True))
    if item['lifeSteal'] != 0:
        tempArr.append(("Life Steal: ", f"```{item['lifeSteal']}```", True))
    if item['moveSpeed'] != 0:
        tempArr.append(("Move Speed: ", f"```{item['moveSpeed']}```", True))
    if item['outOfCombatMoveSpeed'] != 0:
        tempArr.append(("Move Speed(Out of Combat): ", f"```{item['outOfCombatMoveSpeed']}```", True))
    if item['sightRange'] != 0:
        tempArr.append(("Sight Range: ", f"```{item['sightRange']}```", True))
    if item['attackRange'] != 0:
        tempArr.append(("Attack Range: ", f"```{item['attackRange']}```", True))
    if item['increaseBasicAttackDamage'] != 0:
        tempArr.append(("ENAD: ", f"```{item['increaseBasicAttackDamage']}```", True))
    if item['increaseSkillDamage'] != 0:
        tempArr.append(("Skill Damage: ", f"```{item['increaseSkillDamage']}```", True))
    if item['increaseSkillDamageRatio'] != 0:
        tempArr.append(("Skill Damage %: ", f"```{item['increaseSkillDamageRatio']}```", True))
    if item['decreaseRecoveryToBasicAttack'] != 0:
        tempArr.append(("Healing Reduction(Attack): ", f"```{item['decreaseRecoveryToBasicAttack']}```", True))
    if item['decreaseRecoveryToSkill'] != 0:
        tempArr.append(("Healing Reduction(Spell): ", f"```{item['decreaseRecoveryToSkill']}```", True))
    if item['preventCriticalStrikeDamaged'] != 0:
        tempArr.append(("Crit Damage Reduction", f"```{item['preventCriticalStrikeDamaged']}```", True))
    if item['preventBasicAttackDamaged'] != 0:
        tempArr.append(("Attack Reduction: ", f"```{item['preventBasicAttackDamaged']}```", True))
    if item['preventSkillDamagedRatio'] != 0:
        tempArr.append(("Spell Reduction: ", f"```{item['preventSkillDamagedRatio']}```", True))
    return tempArr

def parseMisc(item: dict):
    #we probably don't need this now but I'm implementing it this way just in case
    tempArr: list = []
    tempArr.append(("Name: ", f"```{item['name']}```", False))
    tempArr.append(("Type: ", f"```{item['itemType']}```", True))
    tempArr.append(("Rarity: ", f"```{item['itemGrade']}```", True))
    tempArr.append(("Stack Size: ", f"```{item['stackable']}```", True))
    tempArr.append(("Pick-up Amount: ", f"```{item['initialCount']}```", True))
    return tempArr

def parseConsume(item: dict):
    tempArr: list = []
    tempArr.append(("Name: ", f"```{item['name']}```", False))
    tempArr.append(("Type: ", f"```{item['itemType']}```", True))
    tempArr.append(("Rarity: ", f"```{item['itemGrade']}```", True))
    tempArr.append(("Food/Beverage: ", f"```{item['consumableType']}```", True))
    tempArr.append(("Stack Size: ", f"```{item['stackable']}```", True))
    tempArr.append(("Pick-up Amount: ", f"```{item['initialCount']}```", True))
    if item['heal'] != 0:
        tempArr.append(("Instant Heal: ", f"```{item['heal']}```", True))
    if item['hpRecover'] != 0:
        tempArr.append(("HP Recovery: ", f"```{item['hpRecover']}```", True))
    if item['spRecover'] != 0:
        tempArr.append(("SP Recovery: ", f"```{item['spRecover']}```", True))
    return tempArr

def parseItem(item: dict):
    itemStats:list = []
    if item['itemType'] == 'Weapon':
        itemStats =  parseWeapon(item)
    elif item['itemType'] == 'Armor':
        itemStats =  parseArmor(item)
    elif item['itemType'] == 'Misc':
        itemStats =  parseMisc(item)
    elif item['itemType'] == 'Consume':
        itemStats =  parseConsume(item)
    return itemStats

    
def parseBuildTree(material_1: int, material_2: int, parentName: str, tree: dict):
    """Recursive Function that creates a dictionary with nodes of an item's build tree."""
    # Checks if material_1 and material 2 are misc items
    item_1 = findMiscItem(material_1)
    item_2 = findMiscItem(material_2)

    
    if not item_1:
        # If material_1 was not a misc item, checks if it is a weapon
        item_1 = findEquipment(material_1, True)
    elif item_1['itemType'] == 'Misc':
        # If material_1 was a misc item, finds the item name and stores it.
        item_1['name'] = findItemName(material_1, False, True)

    if not item_1:
        # If material_1 was not a weapon item, checks if it is an armor
        item_1 = findEquipment(material_1)
    elif item_1['itemType'] == 'Weapon':
        # If material_1 was a weapon, finds the item name and stores it.
        item_1['name'] = findItemName(material_1, True)

    if not item_1:
        # If material_1 was not an armor, checks if it is a consumable
        item_1 = findConsumable(material_1)
    elif item_1['itemType'] == 'Armor':
        # If material_1 was an armor, finds the item name and stores it.
        item_1['name'] = findItemName(material_1)

    if not item_1:
        # If material_1 was not an armor, returns empty list to prevent further chaos
        return []
    elif item_1['itemType'] == 'Consume':
        # If material_1 was an armor, finds the item name and stores it.
        item_1['name'] = findItemName(material_1, False, False, True)

    #---------------------- Item 2 -----------------------------------------------

    if not item_2:
        # If material_2 was not a misc item, checks if it is a weapon
        item_2 = findEquipment(material_2, True)
    elif item_2['itemType'] == 'Misc':
        # If material_2 was a misc item, finds the item name and stores it.
        item_2['name'] = findItemName(material_2, False, True)

    if not item_2:
        # If material_2 was not a weapon item, checks if it is an armor
        item_2 = findEquipment(material_2)
    elif item_2['itemType'] == 'Weapon':
        # If material_2 was a weapon, finds the item name and stores it.
        item_2['name'] = findItemName(material_2, True)

    if not item_2:
        # If material_2 was not an armor, returns empty list to prevent further chaos
        item_2 = findConsumable(material_2)
    elif item_2['itemType'] == 'Armor':
        # If material_2 was an armor, finds the item name and stores it.
        item_2['name'] = findItemName(material_2)

    if not item_2:
        # If material_2 was not an armor, returns empty list to prevent further chaos
        return []
    elif item_2['itemType'] == 'Consume':
        # If material_2 was an armor, finds the item name and stores it.
        item_2['name'] = findItemName(material_2, False, False, True)

    # -------------------------- Binary Tree Manipulation ----------------------------

    # Creates an entry in dict where the itemName is the key the two material names are stored as a list
    tree[parentName] = [item_1['name'], item_2['name']]

    # Checks if material_1 also has a build tree. If yes, follows that build tree
    if 'makeMaterial1' in item_1 and item_1['makeMaterial1']:
        parseBuildTree(item_1['makeMaterial1'], item_1['makeMaterial2'], item_1['name'], tree)

    # Checks if material_2 also has a build tree. If yes, follows that build tree    
    if 'makeMaterial1' in item_2 and item_2['makeMaterial1']:
        parseBuildTree(item_2['makeMaterial1'], item_2['makeMaterial2'], item_2['name'], tree)

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
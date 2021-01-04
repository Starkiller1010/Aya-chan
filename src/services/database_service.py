from ..apis.database_api import getRecord, setRecord, deleteRecord, clearDB, getAllKeys

async def linkAccount(discordName: str, erbsName: str):
  """"Inserts a record using discord name as a key and erbs name as the value into repl.it db"""
  try:
    await getRecord(discordName)
    return False
  except KeyError:
    await setRecord(discordName, erbsName)
    return True
  except:
    return False

async def unlinkAccount(discordName: str):
  """"Deletes a record with the key of discord name from repl.it db"""
  try:
    await deleteRecord(discordName)
    return True
  except KeyError:
    return False

async def getAccountName(discordName: str):
  """"Gets a record's value from repl.it db where the key is discord name"""
  try:
    record = await getRecord(discordName)
    return record
  except:
    return ""

async def clearDatabase():
  """"Deletes all records in repl.it db"""
  try:
    await clearDB()
    return True
  except:
    return False
  
async def getAllLinkedAccountNames():
  """"Gets all keys in repl.it db"""
  return await getAllKeys()

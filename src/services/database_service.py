from src.apis.database_api import setRecord, getRecord, deleteRecord, clearDB

async def linkAccount(discordName: str, erbsName: str):
  try:
    await getRecord(discordName)
    return False
  except KeyError:
    await setRecord(discordName, erbsName)
    return True
  except:
    return False

async def unlinkAccount(discordName: str):
  try:
    await deleteRecord(discordName)
    return True
  except KeyError:
    return False

async def getAccountName(discordName: str):
  try:
    record = await getRecord(discordName)
    return record
  except KeyError:
    return ""

async def setEmail(discordName: str, emailAdd: str):
  emailKey = discordName + ".Email"
  await setRecord(emailKey, emailAdd)

async def getEmail(discordName: str):
  try: 
    emailKey = discordName + ".Email"
    return await getRecord(emailKey)
  except KeyError:
    return ""

async def clearDatabase():
  try:
    await clearDB()
    return True
  except:
    return False
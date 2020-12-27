from replit import db

async def setRecord(key:str, value:str):
  db[key] = value

async def getRecord(key: str):
  value = db[key]
  return value

async def deleteRecord(key: str):
  del db[key]

async def clearDB():
  db.clear()

async def getAllRecordsForUser(key: str):
  records = db.prefix(key)
  return records

async def getAllKeys():
  return db.keys()
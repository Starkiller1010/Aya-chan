from replit import db

async def setRecord(key:str, value:str):
  """"Sets/Creates a value using key"""
  db[key] = value

async def getRecord(key: str):
  """"Gets a value using key"""
  return db[key]

async def deleteRecord(key: str):
  """"Deletes entry using key"""
  del db[key]

async def clearDB():
  """"Deletes all keys and values"""
  db.clear()

async def getAllRecordsForUser(key: str):
  """"Returns all values that start with the same str"""
  return db.prefix(key)

async def getAllKeys():
  """"Gets all keys"""
  return db.keys()
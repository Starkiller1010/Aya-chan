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

def importDB():
    file = open('export_db.txt', 'r',encoding='utf8')
    importDB = file.readlines()
    for record in importDB:
        row = record.replace('"', '').split(':')
        key = row[0].strip()
        value = row[1].strip()
        print(key)
        print(value)
    file.close()

def exportDB():
    file = open('export_db.txt','w+',encoding='utf8')
    keys:list = db.keys()
    file.write('{\n')
    i = 0
    for key in keys:
      if not key == 'O//W//O' and not key == 'O//W//O#0282':
        file.write(f'\t"{str(key)}":"{db[str(key)]}"')
        if i < len(keys):
          file.write(',\n')
          i+=1
    file.write('}')
    file.close()
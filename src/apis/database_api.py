from replit import db

def setRecord(key, value):
  db[key] = value

def getRecord(key):
  return db[key]

def deleteRecord(key):
  del db[key]

def getAllRecords():
  return db
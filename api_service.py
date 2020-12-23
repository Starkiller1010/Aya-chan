import requests
import json

def get_erbs_root():
  response = requests.get("https://developer.eternalreturn.io/")
  json_data = json.load(response.text)
  print(f'{json_data} was returned from ERBS API')
  return
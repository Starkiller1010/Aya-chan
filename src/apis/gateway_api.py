import requests
import json

async def get(url: str, headers={}):
    """"Get HTTP call to an API"""
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    return json_data

async def post(url: str, payload: str, headers={}):
    """"Post HTTP call to an API using apiKey"""
    response = requests.post(url=url, data=payload,headers=headers)
    json_data = json.loads(response.text)
    return json_data

async def put(url: str, payload: str, headers={}):
    """"Put HTTP call to an API using apiKey"""
    response = requests.put(url=url, data=payload,headers=headers)
    json_data = json.loads(response.text)
    return json_data

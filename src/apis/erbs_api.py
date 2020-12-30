import requests
import json
async def get(url: str, apiKey: str):
    headers={'x-api-key': apiKey}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    ranks = json_data['topRanks']
    return ranks
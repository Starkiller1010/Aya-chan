import os
import discord
from command import command
from logger import setup
from dotenv import load_dotenv
from website import init_website

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
setup()
client = discord.Client()

@client.event
async def on_ready():
  print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  response = command(msg)

  if response:
    await message.channel.send(response)

init_website()
client.run(TOKEN)

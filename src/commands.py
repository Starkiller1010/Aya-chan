# Imports
import os
import discord
import random
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands
from discord import Forbidden
from .services.database_service import linkAccount, unlinkAccount, getAccountName, clearDatabase

############################################## 
# Environment Variables

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PWD = os.getenv('DEV_PWD')
description = "ERBS API bot"
intent = discord.Intents.default()
intent.members = True
embedVar = discord.Embed(title="Aya-chan", description="", color=0x00ff00)
embedVar.set_image(url="https://media.discordapp.net/attachments/790413678935015436/791136752260612126/ayayayayayya.png")
bot = commands.Bot(command_prefix='>', description=description, intent=intent)
commandListUrl = "https://Aya-chan.starkiller1010.repl.co"

############################################## 
# General Commands

# commandList : Returns url for general community commands.
@bot.command()
async def commandList(ctx):
  embedVar.add_field(name="commandList", value=f"Check all the commands at {commandListUrl}", inline=True)
  await ctx.send(embed=embedVar)

# ping : Returns string and only used to validate bot is listening
@bot.command()
async def ping(ctx):
    embedVar.add_field(name="Ping", value="ding dong, ding dong", inline=False)
    await ctx.channel.send(embed=embedVar)

# roll : Returns simulated dice roll based on input (XdS) where X is the number of dice and S is the number of sides
@bot.command()
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
      embedVar.add_field(name="roll", value="Format has to be in NdS where S is number of sides and N is number of dice.", inline=False)
      await ctx.send(embed=embedVar)
      return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    embedVar.add_field(name="roll", value=result, inline=False)
    await ctx.send(embed=embedVar)

@bot.command()
async def linkErbsAccount(ctx, erbsUserName: str):
  completed = await linkAccount(ctx.author.name, erbsUserName)
  if completed:
    embedVar.add_field(name="linkERBSAccount", value=f"{ctx.author} has linked their account username as {erbsUserName}.", inline=False)
  else:
    embedVar.add_field(name="linkERBSAccount", value=f"{ctx.author} failed to link their ERBS account. You may already have a linked username.", inline=False)
  await ctx.send(embed=embedVar)
  
@bot.command()
async def unlinkErbsAccount(ctx):
  completed = await unlinkAccount(ctx.author.name)
  if completed:
    embedVar.add_field(name="unlinkERBSAccount", value=f"{ctx.author} has unlinked their account.", inline=False)
  else:
    embedVar.add_field(name="unlinkERBSAccount", value=f"{ctx.author} failed to unlink their ERBS account. You may have not linked an account.", inline=False)
  await ctx.send(embed=embedVar)

@bot.command()
async def getErbsAccountName(ctx):
  record = await getAccountName(ctx.author.name)
  if record:
    embedVar.add_field(name="getErbsAccountName", value=f"Here is your erbs account name linked to this user: {record}.", inline=False)
  else:
    embedVar.add_field(name="getErbsAccountName", value=f"No erbs account name was found linked to this user.", inline=False)
  await ctx.send(embed=embedVar)

############################################## 
# Admin Commands

# adminCommandList : Returns url for admin commands.
@bot.command()
@commands.has_role("Admin")
async def adminCommandList(ctx):
  embedVar.add_field(name="commandList", value=f"Check all the commands at {commandListUrl}/admin", inline=True)
  await ctx.send(embed=embedVar)

# giveRole : Assigns role to any number of members that are passed
@bot.command(pass_context=True)
@commands.has_role("Admin")
async def giveRole(ctx, role: discord.Role, *members: discord.Member):
    try:
      for member in members:
        await member.add_roles(role)
        embedVar.add_field(name="giveRole", value=f"{member.name} has been giving a role: [{role.name}].", inline=False)
        await ctx.send(embed=embedVar)
      return
    except Forbidden:
      embedVar.add_field(name="giveRole", value=f"Failed to give role to {member.name} because you do not have permissions to do so.", inline=False)
    except:
      embedVar.add_field(name="giveRole", value=f"Failed to give role to {member.name}.", inline=False)
    finally:
      await ctx.send(embed=embedVar)

@bot.command(pass_context=True)
@commands.has_role("Admin")
async def deleteAllErbsLinkedAccounts(ctx, password: str):
  if not password == PWD:
    print("Permission rejected for 'deleteAllErbsLinkedAccounts'")
    return
  completed = await clearDatabase()
  if completed:
    embedVar.add_field(name="deleteAllErbsLinkedAccounts", value=f"Cleared Internal Database.", inline=False)
  else:
    embedVar.add_field(name="deleteAllErbsLinkedAccounts", value=f"Failed to clear database.", inline=False)
  await ctx.send(embed=embedVar)

# removeRole : Removes a role from any number of members passed
@bot.command(pass_context=True)
@commands.has_role("Admin")
async def removeRole(ctx, role: discord.Role, *members: discord.Member):
    try:
      for member in members:
        await member.remove_roles(role)
        embedVar.add_field(name="removeRole", value=f"{member.name} had the role: [{role.name}] removed.", inline=False)
        await ctx.send(embed=embedVar)
    except Forbidden:
      embedVar.add_field(name="removeRole", value=f"Failed to remove role from {member.name} because you do not have permissions to do so.", inline=False)
      await ctx.send(embed=embedVar)
    except:
      embedVar.add_field(name="removeRole", value=f"Failed to remove role from {member.name}.", inline=False)
      await ctx.send(embed=embedVar)


############################################## 
# Events

#Called at the beginning of bot initialization
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} at {datetime.now(timezone("US/Eastern"))}')
    print('-----------------------------------------------------')

#Override of default on_message. Clears embedVar before sending message to channel
@bot.event
async def on_message(message):
  embedVar.clear_fields()
  await bot.process_commands(message)


############################################## 
# Start Up
def start_bot():
  bot.run(TOKEN)
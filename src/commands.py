# Imports
import os
import discord
import random
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import ConversionError
from discord import Forbidden
from .services.database_service import linkAccount, unlinkAccount, getAccountName, clearDatabase, getAllLinkedAccountNames
from .services.erbs_service import getLeaderboard, getUserRank, getUser, gameModeSwitch
from DiscordUtils import Pagination

############################################## 
# Environment Variables

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PWD = os.getenv('DEV_PWD')
API_KEY = os.getenv('ERBS_API_KEY')
BASE_URL = os.getenv('ERBS_URL')
description = "ERBS API bot"
intent = discord.Intents.default()
intent.members = True
embedVar = discord.Embed(title="Aya-chan", description="", color=0x00ff00)
embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/790413678935015436/792628485335416902/ayayayayayayayayayayayayayaya.png")
bot = commands.AutoShardedBot(command_prefix='>', description=description, intent=intent)
commandListUrl = "https://Aya-chan.starkiller1010.repl.co"

############################################## 
# General Commands

# cmdList : Returns url for general community commands.
@bot.command()
async def cmdList(ctx):
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
  valid = await getUser(baseUrl=BASE_URL, nickname=erbsUserName, apiKey=API_KEY)
  if not valid:
    embedVar.add_field(name="linkERBSAccount", value=f"Username '{erbsUserName}' does not exist in ERBS.", inline=False)
    await ctx.send(embed=embedVar)
    return
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

@bot.command()
async def getErbsLeaderboard(ctx, gameMode: str):
  mode = gameModeSwitch(gameMode)
  if not mode:
    embedVar.add_field(name='getErbsLeaderboard', value=f'Game mode was incorrect. Please input any ONE of these:| Solo(s) | Duo(s) | Squad(s) |')
    await ctx.send(embed=embedVar)
    return
  leaders = await getLeaderboard(baseUrl=BASE_URL, seasonId='1', teamMode=mode, apiKey=API_KEY)
  if leaders:
    embeds:list = []
    embeds.append(discord.Embed(color=ctx.author.color).add_field(name="Rank 1-25", value=f"{''.join(leaders[0])}"))
    embeds.append(discord.Embed(color=ctx.author.color).add_field(name="Rank 26-50", value=f"{''.join(leaders[1])}"))
    embeds.append(discord.Embed(color=ctx.author.color).add_field(name="Rank 51-75", value=f"{''.join(leaders[2])}"))
    embeds.append(discord.Embed(color=ctx.author.color).add_field(name="Rank 76-100", value=f"{''.join(leaders[3])}"))

    paginator = Pagination.AutoEmbedPaginator(ctx)
    await paginator.run(embeds)
  else:
    embedVar.add_field(name="getErbsSquadLeaderboard", value=f"No Leaderboard was found.", inline=False)
    await ctx.send(embed=embeds)

@bot.command()
async def getMyCurrentRank(ctx, gameMode: str):
  erbsUsername = getAccountName(ctx.author.name)
  if not erbsUsername:
    embedVar.add_field(name="getMyCurrentRank", value=f"No erbs account name was found linked to this user.", inline=False)
    await ctx.send(embed=embedVar)
    return
  mode = gameModeSwitch(gameMode)
  if not mode:
    embedVar.add_field(name='getMyCurrentRank', value=f'Game mode was incorrect. Please input any ONE of these:| Solo | Duo| Squad |')
    await ctx.send(embed=embedVar)
    return
  rank = await getUserRank(baseUrl=BASE_URL, nickname=erbsUsername, seasonId='1', teamMode=mode, apiKey=API_KEY)
  if not rank == 0:
    embedVar.add_field(name='getMyCurrentRank', value=f'Your rank in season 1 of {gameMode} is rank: {rank}')
  elif rank == 0:
    embedVar.add_field(name='getMyCurrentRank', value=f'You have not played all your placement games. Please try again after playing more ranked.')
  else:
    embedVar.add_field(name='getMyCurrentRank', value=f'Failed to retrieve your rank. Double-check to see if your linked username is correct.')
  await ctx.send(embed=embedVar)


############################################## 
# Admin Commands

# adminHelp : Returns url for admin commands.
@bot.command()
@commands.has_permissions(manage_roles=True)
async def adminHelp(ctx):
  embedVar.add_field(name="commandList", value=f"Check all the commands at {commandListUrl}/admin", inline=True)
  await ctx.send(embed=embedVar)

# giveRole : Assigns role to any number of members that are passed
@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def giveRole(ctx, role: discord.Role, *members: discord.Member):
    try:
      for member in members:
        await member.add_roles(role)
        embedVar.add_field(name="giveRole", value=f"{member.name} has been giving a role: [{role.name}].", inline=False)
        await ctx.send(embed=embedVar)
      return
    except Forbidden:
      embedVar.add_field(name="giveRole", value=f"Failed to give role to {member.name} because Aya-chan does not have permissions to do so. Please lower the targeted role in Role list or raise ERBS API Bot role higher than target.", inline=False)
      await ctx.send(embed=embedVar)
    except:
      embedVar.add_field(name="giveRole", value=f"Failed to give role to {member.name}.", inline=False)
      await ctx.send(embed=embedVar)

@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
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
@commands.has_permissions(manage_roles=True)
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

#Gets a linked Erbs username from db that matches the name passed in. Can only be done by users with manage_role permission
@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def getUserErbsAccountName(ctx, member: discord.Member):
  try:
    record = await getAccountName(member)
    if record:
      embedVar.add_field(name="getUserErbsAccountName", value=f"{member.name} has the username {record} tied to their account.", inline=False)
    else:
      embedVar.add_field(name="getUserErbsAccountName", value=f"No Erbs username was found linked to the discord member {member.name}.", inline=False)
  except:
    embedVar.add_field(name="getUserErbsAccountName", value=f"Failed to retrieve linked account for {member.name}.", inline=False)
  await ctx.send(embed=embedVar)

#Sets a linked Erbs username from db that matches the name passed in. Can only be done by users with manage_role permission
@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def setUserErbsAccountName(ctx, member: discord.Member, erbsAccountName: str, password: str):
  if not password == PWD:
    print("Permission rejected for 'setUserErbsAccountName'")
    return
  try:
    record = await linkAccount(member.name, erbsAccountName)
    if record:
      embedVar.add_field(name="setUserErbsAccountName", value=f"{member.name} has the username {erbsAccountName} tied to their account.", inline=False)
    else:
      embedVar.add_field(name="setUserErbsAccountName", value=f"No Erbs username was found linked to the discord member {member.name}.", inline=False)
  except:
    embedVar.add_field(name="setUserErbsAccountName", value=f"Failed to retrieve linked account for {member.name}.", inline=False)
  await ctx.send(embed=embedVar)

#unlinks Erbs username from db that matches the name passed in. Can only be done by users with manage_role permission
@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def unlinkUserErbsAccountName(ctx, member: discord.Member, password: str):
  if not password == PWD:
    print("Permission rejected for 'setUserErbsAccountName'")
    return
  try:
    record = await unlinkAccount(member.name)
    if record:
      embedVar.add_field(name="setUserErbsAccountName", value=f"{member.name} had their erbs username removed from the database.", inline=False)
    else:
      embedVar.add_field(name="setUserErbsAccountName", value=f"No Erbs username was found linked to the discord member {member.name}.", inline=False)
  except:
    embedVar.add_field(name="setUserErbsAccountName", value=f"Failed to retrieve linked account for {member.name}.", inline=False)
  await ctx.send(embed=embedVar)  

#Gets all linked Erbs username from db. Can only be done by users with manage_role permission
@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def getAllErbsAccountNames(ctx):
  try:
    listOfNames = "Here is the list of all linked erbs accounts:\n"
    ErbsNames = await getAllLinkedAccountNames()
    for discName in ErbsNames:
      accName = await getAccountName(discName)
      listOfNames = listOfNames + " Discord: " + discName + ", ERBS: " + accName + "\n"
    embedVar.add_field(name="getAllErbsAccountName", value=f"{listOfNames}", inline=False)
  except:
    embedVar.add_field(name="getAllErbsAccountName", value=f"There was a problem in retrieving all linked erbs accounts.", inline=False)
  await ctx.send(embed=embedVar)

############################################## 
# Admin Error handling

@getUserErbsAccountName.error
async def getErbsUser_error(ctx, error):
    if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="getUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
        await ctx.send(embed=embedVar)
    else:
        raise error

@setUserErbsAccountName.error
async def setErbsUser_error(ctx, error):
    if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="setUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
        await ctx.send(embed=embedVar)
    else:
        raise error

@unlinkUserErbsAccountName.error
async def unlinkUser_error(ctx, error):
    if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="unlinkUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
        await ctx.send(embed=embedVar)
    else:
        raise error

@removeRole.error
async def removeRole_error(ctx, error):
    if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="removeRole", value=f"There was/were no member(s) in this discord with a name you have provided.", inline=False)
        await ctx.send(embed=embedVar)
    else:
        raise error

@giveRole.error
async def giveRole_error(ctx, error):
    if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="giveRole", value=f"There was no member in this discord with a name you have provided.", inline=False)
        await ctx.send(embed=embedVar)
    else:
        raise error
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
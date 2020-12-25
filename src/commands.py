import os
import discord
import random
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands
from discord import Forbidden
client = discord.Client
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "ERBS API bot"
intent = discord.Intents.default()
intent.members = True
embedVar = discord.Embed(title="Aya-chan", description="", color=0x00ff00)
embedVar.set_image(url="https://media.discordapp.net/attachments/790413678935015436/791136752260612126/ayayayayayya.png")
bot = commands.Bot(command_prefix='>', description=description, intent=intent)

# Status Command
# Simpy returns status of the website
@bot.command()
async def commandList(ctx):
    await ctx.send('Check all the commands at https://Aya-chan.starkiller1010.repl.co')

@bot.command()
async def ping(ctx):
    embedVar.add_field(name="Ping", value="ding dong, ding dong", inline=True)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def roll(ctx, dice: str):
    # Rolls a dice in NdN format.
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
      embedVar.add_field(name="roll", value="Format has to be in NdS where S is number of sides and N is number of dice.", inline=False)
      await ctx.send(embed=embedVar)
      return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    embedVar.add_field(name="roll", value=result, inline=False)
    await ctx.send(embed=embedVar)

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} at {datetime.now(timezone("US/Eastern"))}')
    print('-----------------------------------------------------')

@bot.event
async def on_message(message):
  embedVar.clear_fields()
  await bot.process_commands(message)

def start_bot():
  bot.run(TOKEN)
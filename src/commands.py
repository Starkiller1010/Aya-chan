import os
import discord
import random
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands
from discord import Forbidden
from discord.utils import get
client = discord.Client
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "ERBS API bot"
intent = discord.Intents.default()
intent.members = True
bot = commands.Bot(command_prefix='>', description=description, intent=intent)

# Status Command
# Simpy returns status of the website
@bot.command()
async def commandList(ctx):
    print("Aya received a status command")
    await ctx.send('Check all the commands at https://Aya-chan.starkiller1010.repl.co')

@bot.command()
async def ping(ctx):
    await ctx.send('```ding dong, ding dong```')

@bot.command()
async def roll(ctx, dice: str):
    # Rolls a dice in NdN format.
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('```Format has to be in SdN where S is number of sides and N is number of times```')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)

@bot.command(pass_context=True)
@commands.has_role("Admin")
async def addAttendee(ctx, member: discord.Member):
    try:
      role = get(ctx.guild.roles, name="Tournament Attendees")
      await member.add_roles(role)
      await ctx.send(f"```{member.name} has been giving a role: {role.name}```")
    except Forbidden:
      await ctx.send(f'```Failed to give role to {member.name} because you do not have permissions to do so```')
    except:
      await ctx.send(f'```Failed to give role to {member.name}```')

@bot.command(pass_context=True)
@commands.has_role("Admin")
async def giveRole(ctx, member: discord.Member, role: discord.Role):
    try:
      await member.add_roles(role)
      await ctx.send(f"```{member.name} has been giving a role: [{role.name}]```")
    except Forbidden:
      await ctx.send(f'```Failed to give role to {member.name} because you do not have permissions to do so```')
    except:
      await ctx.send(f'```Failed to give role to {member.name}```')

@bot.command(pass_context=True)
@commands.has_role("Admin")
async def removeRole(ctx, member: discord.Member, role: discord.Role):
    try:
      await member.remove_roles(role)
      await ctx.send(f"```{member.name} had the role: [{role.name}] removed```")
    except Forbidden:
      await ctx.send(f'```Failed to remove role from {member.name} because you do not have permissions to do so.```')
    except:
      await ctx.send(f'```Failed to remove role from {member.name}```')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} at {datetime.now(timezone("US/Eastern"))}')
    print('-----------------------------------------------------')

def start_bot():
  bot.run(TOKEN)
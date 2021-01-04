# Imports
import os
from datetime import datetime
from .logger import logInfo, logErr
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pytz import timezone
import traceback
import sys


############################################## 
# Environment Variables

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ID = os.getenv('OWNER_ID')
BOT_IMAGE = os.getenv('IMAGE_URL')

intent = discord.Intents.default()
intent.members = True

bot = commands.AutoShardedBot(command_prefix='>', description="ERBS API bot", intent=intent)
startup_extensions = ["src.cogs.erbs", "src.cogs.admin", "src.cogs.db_admin", "src.cogs.basic"]

embedVar = discord.Embed(color=0x00ff00)
embedVar.set_thumbnail(url=BOT_IMAGE)

async def is_owner(ctx):
    return ctx.author.id == int(ID)
############################################## 
# General Commands

@bot.command(hidden=True)
@commands.check(is_owner)
async def load(ctx, extension_name : str):
    """Loads an extension"""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extension_name))

@bot.command(hidden=True)
@commands.check(is_owner)
async def unload(ctx, extension_name : str):
    """Unloads an extension"""
    bot.unload_extension(extension_name)
    await ctx.send("{} unloaded.".format(extension_name))

@bot.command(hidden=True)
@commands.check(is_owner)
async def reload(ctx, extension_name : str):
    """Reloads an extension"""
    try:
        bot.reload_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extension_name))
############################################## 
# Events

#Called at the beginning of bot initialization
@bot.event
async def on_ready():
    """Listener to on_ready event"""
    print(f'Logged in as {bot.user.name} at {datetime.now(timezone("US/Eastern"))}')
    print('-----------------------------------------------------')
    logInfo(f'{bot.user.name} online')

#Override of default on_message. Clears embedVar before sending message to channel
@bot.event
async def on_message(message):
    """Listener to on_message event"""  
    embedVar.clear_fields()
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    """Listener to on_command_error event"""
    if isinstance(error, commands.errors.CheckFailure):
        logInfo(f'{ctx.author.name} failed to authorize check for {ctx.command}')
        pass
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        logErr(f'Error occurred in {ctx.command} by {ctx.author.name}: {error}')


############################################## 
# Start Up
def start_bot():
    """Entry method. Loads all extension files and runs the bot"""
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    bot.run(TOKEN)

def getEmbedVar():
    """Returns embedVar global variable"""
    return embedVar

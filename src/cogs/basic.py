import os
import random
import discord
from discord.ext import commands
from ..bot import getEmbedVar
from ..logger import logInfo, logErr
embedVar = getEmbedVar()
BASE_SITE= f"{os.getenv('SITE_URL')}"

class basicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#########################################
# Commands

    # ping : Returns string and only used to validate bot is listening
    @commands.command(brief="Pings bot")
    async def ping(self, ctx):
        """Verify bot is receiving commands"""
        embedVar.add_field(name="Ping", value="ding dong, ding dong", inline=False)
        await ctx.channel.send(embed=embedVar)

    # roll : Returns simulated dice roll based on input (XdS) where X is the number of dice and S is the number of sides
    @commands.command(brief="Rolls Dice")
    async def roll(self, ctx, dice: str):
        """Rolls X amount of dice with N amount of faces. Params: {X}d{N}"""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
          embedVar.add_field(name="roll", value="Format has to be in NdS where S is number of sides and N is number of dice.", inline=False)
          await ctx.send(embed=embedVar)
          return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        embedVar.add_field(name="roll", value=result, inline=False)
        await ctx.send(embed=embedVar)
    
#########################################
# Error Handling

    @roll.error
    async def roll_error(self, ctx, error):
        """Error handing roll"""
        logErr(f'Error within roll: {error}')
        if isinstance(error, (commands.ConversionError, commands.BadArgument)):
            embedVar.add_field(name="roll_error", value="The format for the command is XdN where X is the number of dice and N is the number of faces")
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="roll_error", value="Please add after the command XdN, where X is the number of dice and N is the number of faces")
            await ctx.send(embed=embedVar)
        else:
            raise error
#########################################
# Link
def setup(bot):
    """Adds extension as a cog"""
    bot.add_cog(basicCommands(bot))
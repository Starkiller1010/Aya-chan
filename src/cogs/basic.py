import os
import random
import discord
from discord.ext import commands
from ..bot import getEmbedVar

embedVar = getEmbedVar()
BASE_SITE= f"{os.getenv('SITE_URL')}"

class basicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#########################################
# Commands

    # cmdList : Returns url for general community commands.
    @commands.command()
    async def cmdList(self, ctx):
      embedVar.add_field(name="cmdList", value=f"Check all the commands at {BASE_SITE}", inline=True)
      await ctx.send(embed=embedVar)

    # ping : Returns string and only used to validate bot is listening
    @commands.command()
    async def ping(self, ctx):
        embedVar.add_field(name="Ping", value="ding dong, ding dong", inline=False)
        await ctx.channel.send(embed=embedVar)

    # roll : Returns simulated dice roll based on input (XdS) where X is the number of dice and S is the number of sides
    @commands.command()
    async def roll(self, ctx, dice: str):
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
#########################################
# Link
def setup(bot):
    bot.add_cog(basicCommands(bot))
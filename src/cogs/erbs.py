import os

import discord
from discord.ext import commands
from discord.ext.commands import ConversionError
from DiscordUtils import Pagination

from ..bot import getEmbedVar
from ..services.database_service import (getAccountName, linkAccount,
                                         unlinkAccount)
from ..services.erbs_service import (gameModeSwitch, getLeaderboard, getUser,
                                     getUserRank)

API_KEY = os.getenv('ERBS_API_KEY')
BASE_URL = os.getenv('ERBS_URL')

embedVar = getEmbedVar

class ERBSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

##########################################
# Commands

    @commands.command(name="linkAccount")
    async def linkERBSUserName(self, ctx, erbsUserName: str):
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

    @commands.command(name="unlinkAccount")
    async def unlinkERBSUserName(self, ctx):
        completed = await unlinkAccount(ctx.author.name)
        if completed:
            embedVar.add_field(name="unlinkERBSAccount", value=f"{ctx.author} has unlinked their account.", inline=False)
        else:
            embedVar.add_field(name="unlinkERBSAccount", value=f"{ctx.author} failed to unlink their ERBS account. You may have not linked an account.", inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(name="getLeaderboard")
    async def getErbsLeaderboard(self, ctx, gameMode: str):
        mode = gameModeSwitch(gameMode)
        if not mode:
          embedVar.add_field(name='getErbsLeaderboard', value=f'Game mode was incorrect. Please input any ONE of these:| Solo(s) | Duo(s) | Squad(s) |')
          await ctx.send(embed=embedVar)
          return
        leaders = await getLeaderboard(baseUrl=BASE_URL, seasonId='1', teamMode=mode, apiKey=API_KEY)
        if leaders:
          embeds:list = []
          i = 1
          for page in leaders:
            embeds.append(discord.Embed(color=ctx.author.color).add_field(name=f"Rank {i}-{i+24}", value=f"{''.join(page)}"))
            i+=25 
          paginator = Pagination.AutoEmbedPaginator(ctx)
          await paginator.run(embeds)
        else:
          embedVar.add_field(name="getErbsSquadLeaderboard", value=f"No Leaderboard was found.", inline=False)
          await ctx.send(embed=embeds)

    @commands.command(name="getMyUsername")
    async def getErbsAccountName(self, ctx):
      record = await getAccountName(ctx.author.name)
      if record:
        embedVar.add_field(name="getErbsAccountName", value=f"Here is your erbs account name linked to this user: {record}.", inline=False)
      else:
        embedVar.add_field(name="getErbsAccountName", value=f"No erbs account name was found linked to this user.", inline=False)
      await ctx.send(embed=embedVar)

    @commands.command(name="getMyRank")
    async def getMyCurrentRank(self, ctx, gameMode: str):
      erbsUsername = await getAccountName(ctx.author.name)
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

##################################################
# Error Handling

    @getErbsLeaderboard.error
    async def getLeaderboard_error(self, ctx, error):
      if isinstance(error, (ConversionError, commands.BadArgument)):
          embedVar.add_field(name="getMyCurrentRank", value=f"Please input a gameMode. [Solo, Duo, Squad]", inline=False)
          await ctx.send(embed=embedVar)
      else:
          raise error


    @getMyCurrentRank.error
    async def getRank_error(self, ctx, error):
      if isinstance(error, (ConversionError, commands.BadArgument)):
          embedVar.add_field(name="getMyCurrentRank", value=f"Please input a gameMode. [Solo, Duo, Squad]", inline=False)
          await ctx.send(embed=embedVar)
      else:
          raise error
###################################
# Link
def setup(bot):
    bot.add_cog(ERBSCommands(bot))

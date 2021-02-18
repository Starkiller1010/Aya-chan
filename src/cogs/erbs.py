import os

import discord
from discord.ext import commands
from discord.ext.commands import ConversionError, Greedy
from DiscordUtils import Pagination
from ..logger import logInfo, logErr
from ..bot import getEmbedVar, getThumbnailUrl
from ..services.database_service import (getAccountName, linkAccount,
                                         unlinkAccount)
from ..services.erbs_service import (gameModeSwitch, getLeaderboard, getUser,
                                     getUserRank, getMatchHistory, findGameStats, findItem, parseItem, parseBuildTree)

API_KEY = os.getenv('ERBS_API_KEY')
BASE_URL = os.getenv('ERBS_URL')

embedVar = getEmbedVar()
currentSeasonId = '1'
class ERBSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

##########################################
# Commands

    @commands.command(name="linkAccount", brief="Links ERBS Account")
    async def linkERBSUserName(self, ctx, erbsUserName: str):
      """Links user to an ERBS account's username."""
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

    @commands.command(name="unlinkAccount", brief="Unlinks ERBS Account")
    async def unlinkERBSUserName(self, ctx):
        """Deletes linked ERBS Username of this user."""
        completed = await unlinkAccount(ctx.author.name)
        if completed:
            embedVar.add_field(name="unlinkERBSAccount", value=f"{ctx.author} has unlinked their account.", inline=False)
        else:
            embedVar.add_field(name="unlinkERBSAccount", value=f"{ctx.author} failed to unlink their ERBS account. You may have not linked an account.", inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(name="getLeaderboard", brief="Gets Global Leaderboard")
    async def getErbsLeaderboard(self, ctx, gameMode: str):
        """Gets Global Leaderboard of a specific game mode."""
        mode = gameModeSwitch(gameMode)
        if not mode:
          embedVar.add_field(name='getErbsLeaderboard', value=f'Game mode was incorrect. Please input any ONE of these:| Solo(s) | Duo(s) | Squad(s) |')
          await ctx.send(embed=embedVar)
          return
        leaders = await getLeaderboard(baseUrl=BASE_URL, seasonId=currentSeasonId, teamMode=mode, apiKey=API_KEY)
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

    @commands.command(name="getMyUsername", brief="Gets User's ERBS name")
    async def getErbsAccountName(self, ctx):
      """Gets the author's ERBS username. Must have account linked. """
      record = await getAccountName(ctx.author.name)
      if record:
        embedVar.add_field(name="getErbsAccountName", value=f"Here is your erbs account name linked to this user: {record}.", inline=False)
      else:
        embedVar.add_field(name="getErbsAccountName", value=f"No erbs account name was found linked to this user.", inline=False)
      await ctx.send(embed=embedVar)

    @commands.command(name="getMyRank", brief="Gets User's Rank")
    async def getMyCurrentRank(self, ctx, gameMode: str):
      """Gets the author's global rank for a specific game mode. Must have account linked."""
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
      rank = await getUserRank(baseUrl=BASE_URL, nickname=erbsUsername, seasonId=currentSeasonId, teamMode=mode, apiKey=API_KEY)
      if not rank == 0:
        embedVar.add_field(name='getMyCurrentRank', value=f'Your rank in season {currentSeasonId} of {gameMode} is rank: {rank}')
      elif rank == 0:
        embedVar.add_field(name='getMyCurrentRank', value=f'You have not played all your placement games. Please try again after playing more ranked.')
      else:
        embedVar.add_field(name='getMyCurrentRank', value=f'Failed to retrieve your rank. Double-check to see if your linked username is correct.')
      await ctx.send(embed=embedVar)

    @commands.command(name="getMatchHistory", brief="User's Match History")
    async def getMatchHistory(self, ctx, gameId: Greedy[int] = None, nickname: str = ''):
      """Gets the author's match history in a specific game mode. 
      If no nickname passed, uses linked account assigned to user.
      If a gameId is passed in, will user's stats for that game."""
      user: dict
      if nickname:
        user = await getUser(baseUrl=BASE_URL, nickname=nickname, apiKey=API_KEY)
      else:
        erbsUsername = await getAccountName(ctx.author.name)
        if not erbsUsername:
          embedVar.add_field(name="getMatchHistory", value=f"No erbs account name was found linked to this user.", inline=False)
          await ctx.send(embed=embedVar)
          return
        else: 
          user = (await getUser(baseUrl=BASE_URL, nickname=erbsUsername, apiKey=API_KEY))
      if not user:
          embedVar.add_field(name="getMatchHistory", value=f"User was not found in ERBS.", inline=False)
          await ctx.send(embed=embedVar)
          return
      else: 
        history = await getMatchHistory(baseUrl=BASE_URL, userId=user['userNum'], apiKey=API_KEY)
      if not history:
        embedVar.add_field(name="getMatchHistory", value=f"No history was found for this user.", inline=False)
        await ctx.send(embed=embedVar)
        return
      elif gameId:
        while(True):
          match = await findGameStats(matchHistory=history, gameId=gameId[0])
          if not match:
            if not 'next' in history:
              embedVar.add_field(name="getMatchHistory", value=f"No game with that id was found for this user.", inline=False)
              await ctx.send(embed=embedVar)
              return
            else:
              history = await getMatchHistory(baseUrl=BASE_URL, userId=user['userNum'], apiKey=API_KEY, nextId=history['next'])
              continue
          else:
            embeds:list = []
            page0 = [("Game ID", f"```{match['id']}```", False),
                      ("Character", f"```{match['character']}```", True),
                      ("Ranked", f"```{match['placement']}```", True),
                      ("Game Mode", f"```{match['mode']}```", True),                    
                      ("Kills", f"```{match['kills']}```", True),
                      ("Assists", f"```{match['assists']}```", True),
                      ("Hunts", f"```{match['hunts']}```", True),
                      ("Max HP", f"```{match['maxHp']}```", True),
                      ("Max SP", f"```{match['maxSp']}```", True),
                      ("Attack Power", f"```{match['attackPower']}```", True),
                      ("Defense", f"```{match['defense']}```", True),
                      ("HP Regen", f"```{match['hpRegen']}```", True),
                      ("SP Regen", f"```{match['spRegen']}```", True),
                      ("Attack Speed", f"```{match['attackSpeed']}```", True),
                      ("Move Speed", f"```{match['moveSpeed']}```", True),
                      ("Sight Range", f"```{match['sightRange']}```", True),
                      ("Attack Range", f"```{match['attackRange']}```", True),
                      ("Critical Chance", f"```{match['criticalStrikeChance']}```", True),
                      ("Critical Damage", f"```{match['criticalStrikeDamage']}```", True),
                      ("Cooldown Reduction", f"```{match['coolDownReduction']}```", True),
                      ("LifeSteal", f"```{match['lifeSteal']}```", True)]
          skills = ""
          for skill in match['skillLevelOrder']:
            skills = skills + f"{skill}: {match['skillLevelOrder'][skill]}"

          mastery = ""
          for masteryCode in match['masteryLevels']:
            mastery = mastery + f"```{masteryCode}: {match['masteryLevels'][masteryCode]}```"
            

          page1 = [("Level", f"```{match['level']}```", False),
                    ("Mastery", f"{mastery}", False),
                    ("Skill Order", f"```{skills}```", False),
                    ("Weapon", f"```{match['weapon']}```", True),
                    ("Chest", f"```{match['chest']}```", True),
                    ("Head", f"```{match['head']}```", True),
                    ("Gloves", f"```{match['gloves']}```", True),
                    ("Boots", f"```{match['boots']}```", True),
                    ("Accessory", f"```{match['accessory']}```", True)]

          embeds.append(discord.Embed())
          for name, value, inline in page0:
            embeds[0].add_field(name=name, value=value, inline=inline)

          embeds.append(discord.Embed())
          for name, value, inline in page1:
            embeds[1].add_field(name=name, value=value, inline=inline)
          
          for x in range(len(embeds)):
            embeds[x].set_thumbnail(url=getThumbnailUrl())

          paginator = Pagination.AutoEmbedPaginator(ctx)
          await paginator.run(embeds)
          return
      else:
        embeds:list = []
        while True:
          matchHistory = history["userGames"]
          for match in matchHistory:
            fields = [("Game: ", f"```{match['gameId']}```", False),
                      ("Mode: ", f"```{gameModeSwitch(match['matchingTeamMode'])}```", False),
                      ("Level: ", f"```{match['characterLevel']}```", False),
                      ("Placement: ", f"```{match['gameRank']}```", False),
                      ("Kills: ", f"```{match['playerKill']}```", False),
                      ("Assists: ", f"```{match['playerAssistant']}```", False),
                      ("Hunts: ", f"```{match['monsterKill']}```", False)]
            embeds.append(discord.Embed())
            for name, value, inline in fields:
              embeds[len(embeds) - 1].add_field(name=name, value=value, inline=inline)
          for x in range(len(embeds)):
              embeds[x].set_thumbnail(url=getThumbnailUrl())
          if 'next' in history:
            history = await getMatchHistory(baseUrl=BASE_URL, userId=user['userNum'], apiKey=API_KEY, nextId=history['next'])
          else:
            break
        paginator = Pagination.AutoEmbedPaginator(ctx)
        await paginator.run(embeds)

    @commands.command(name='getItem', brief='Item build and description')
    async def getItemTree(self, ctx, *, itemName: str):
      item = await findItem(itemName)
      fields = parseItem(item)
      embeds:list = []
      tree: dict = {}
      embed = discord.Embed()
      if 'makeMaterial1' in item and item['makeMaterial1']:
        parseBuildTree(item['makeMaterial1'], item['makeMaterial2'], item['name'], tree)
        fields.append(("Builds From: ", f"```{tree[item['name']][0]} + {tree[item['name']][1]}```", True))
        print(tree)
      i = 0
      for name, value, inline in fields:
            if i < 25:
              embed.add_field(name=name, value=value, inline=inline)
              i += 1
            else:
              i = 0
              embeds.append(embed)
              embed = discord.Embed()
              embed.add_field(name=name, value=value, inline=inline)
      embeds.append(embed)
      if tree:
        for node in tree:
          print(tree[node])
          if item['name'] == node:
            continue
          else:
            embed = discord.Embed()
            item = await findItem(node)
            fields:list = parseItem(item)
            fields.append(("Builds From: ", f"```{tree[node][0]} + {tree[node][1]}```", True))
            i = 0
            for name, value, inline in fields:
              if i < 25:
                embed.add_field(name=name, value=value, inline=inline)
                i += 1
              else:
                i = 0
                embeds.append(embed)
                embed = discord.Embed()
                embed.add_field(name=name, value=value, inline=inline)
            embeds.append(embed)
        for x in range(len(embeds)):
          embeds[x].set_thumbnail(url=getThumbnailUrl())
      paginator = Pagination.AutoEmbedPaginator(ctx)
      await paginator.run(embeds)
      

##################################################
# Error Handling


    @linkERBSUserName.error
    async def linkAccount_error(self, ctx, error):
      """Error handling for linkERBSUsername"""
      logErr(f'Error within linkERBSUsername: {error}')
      if isinstance(error, (ConversionError, commands.BadArgument)):
          embedVar.add_field(name="linkERBSUserName", value=f"You have inputted an non-valid username, please make sure it is a string of characters.", inline=False)
          await ctx.send(embed=embedVar)
      elif isinstance(error, commands.MissingRequiredArgument):
          embedVar.add_field(name="linkERBSUserName", value=f"Please enter your ERBS username after the command.", inline=False)
          await ctx.send(embed=embedVar)
      else:
        raise error

    @getErbsLeaderboard.error
    async def getLeaderboard_error(self, ctx, error):
      """Error handling for getLeaderboard"""
      logErr(f'Error within getLeaderboard: {error}')
      if isinstance(error, (ConversionError, commands.BadArgument)):
          embedVar.add_field(name="getErbsLeaderboard", value=f"You have inputted an non-valid gameMode. Try again with any of the following: [Solo, Duo, Squad]", inline=False)
          await ctx.send(embed=embedVar)
      elif isinstance(error, commands.MissingRequiredArgument):
          embedVar.add_field(name="getErbsLeaderboard", value=f"Please input a gameMode. [Solo, Duo, Squad]", inline=False)
          await ctx.send(embed=embedVar)
      else:
          raise error

    @getMyCurrentRank.error
    async def getRank_error(self, ctx, error):
      """Error handling for getRank"""
      logErr(f'Error within getRank: {error}')
      if isinstance(error, (ConversionError, commands.BadArgument)):
          embedVar.add_field(name="getMyCurrentRank", value=f"You have inputted an non-valid gameMode. Try again with any of the following: [Solo, Duo, Squad]", inline=False)
          await ctx.send(embed=embedVar)
      elif isinstance(error, commands.MissingRequiredArgument):
          embedVar.add_field(name="getMyCurrentRank", value=f"Please input a gameMode. [Solo, Duo, Squad]", inline=False)
          await ctx.send(embed=embedVar)
      else:
          raise error

    @getItemTree.error
    async def getItem_error(self, ctx, error):
      """Error handling for getRank"""
      logErr(f'Error within getRank: {error}')
      if isinstance(error, (ConversionError, commands.BadArgument)):
          embedVar.add_field(name="getItemTree", value=f"You have given an invalid argument. Please pass in an item name", inline=False)
          await ctx.send(embed=embedVar)
      elif isinstance(error, commands.MissingRequiredArgument):
          embedVar.add_field(name="getItemTree", value=f"Please insert an item name.", inline=False)
          await ctx.send(embed=embedVar)
      else:
          raise error

    
###################################
# Link
def setup(bot):
  """Adds extension as a cog"""
  bot.add_cog(ERBSCommands(bot))

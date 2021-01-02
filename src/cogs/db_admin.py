import os

import discord
from discord import Forbidden
from discord.ext import commands
from discord.ext.commands import ConversionError
from dotenv import load_dotenv

from ..bot import getEmbedVar
from ..services.database_service import (clearDatabase, getAccountName,
                                         getAllLinkedAccountNames, linkAccount,
                                         unlinkAccount)

load_dotenv()
PWD = os.getenv('DEV_PWD')

embedVar = getEmbedVar

class DB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#############################################
# Commands
    
    #Gets a linked Erbs username from db that matches the name passed in. Can only be done by users with manage_role permission
    @commands.command(pass_context=True, name="getUsername")
    @commands.has_permissions(manage_roles=True)
    async def getUserErbsAccountName(self, ctx, member: discord.Member):
      try:
        record = await getAccountName(member)
        if record:
          embedVar.add_field(name="getUserErbsAccountName", value=f"{member.name} has the username {record} tied to their account.", inline=False)
        else:
          embedVar.add_field(name="getUserErbsAccountName", value=f"No Erbs username was found linked to the discord member {member.name}.", inline=False)
      except:
        embedVar.add_field(name="getUserErbsAccountName", value=f"Failed to retrieve linked account for {member.name}.", inline=False)
      await ctx.send(embed=embedVar)

    #Gets all linked Erbs username from db. Can only be done by users with manage_role permission
    @commands.command(pass_context=True, name="getAllUsernames")
    @commands.has_permissions(manage_roles=True)
    async def getAllErbsAccountNames(self, ctx):
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

      #Sets a linked Erbs username from db that matches the name passed in. Can only be done by users with manage_role permission
    @commands.command(pass_context=True, name="setUsername")
    @commands.has_permissions(manage_roles=True)
    async def setUserErbsAccountName(self, ctx, member: discord.Member, erbsAccountName: str, password: str):
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
    @commands.command(pass_context=True, name="deleteUsername")
    @commands.has_permissions(manage_roles=True)
    async def deleteUserErbsAccountName(self, ctx, member: discord.Member, password: str):
      if not password == PWD:
        print("Permission rejected for 'deleteUserErbsAccountName'")
        return
      try:
        record = await unlinkAccount(member.name)
        if record:
          embedVar.add_field(name="deleteUserErbsAccountName", value=f"{member.name} had their erbs username removed from the database.", inline=False)
        else:
          embedVar.add_field(name="deleteUserErbsAccountName", value=f"No Erbs username was found linked to the discord member {member.name}.", inline=False)
      except:
        embedVar.add_field(name="deleteUserErbsAccountName", value=f"Failed to retrieve linked account for {member.name}.", inline=False)
      await ctx.send(embed=embedVar)  

    @commands.command(pass_context=True, name="deleteAllLinkedUsernames")
    @commands.has_permissions(manage_roles=True)
    async def deleteAllErbsLinkedAccounts(self, ctx, password: str):
      if not password == PWD:
        print("Permission rejected for 'deleteAllErbsLinkedAccounts'")
        return
      completed = await clearDatabase()
      if completed:
        embedVar.add_field(name="deleteAllErbsLinkedAccounts", value=f"Cleared Internal Database.", inline=False)
      else:
        embedVar.add_field(name="deleteAllErbsLinkedAccounts", value=f"Failed to clear database.", inline=False)
      await ctx.send(embed=embedVar)

#############################################
# Error Handling

    @getUserErbsAccountName.error
    async def getErbsUser_error(self, ctx, error):
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="getUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

    @setUserErbsAccountName.error
    async def setErbsUser_error(self, ctx, error):
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="setUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

    @deleteUserErbsAccountName.error
    async def unlinkUser_error(self, ctx, error):
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="unlinkUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

#############################################
# Link
def setup(bot):
    bot.add_cog(DB(bot))

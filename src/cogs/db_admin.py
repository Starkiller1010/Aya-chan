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

embedVar = getEmbedVar()

class DB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#############################################
# Commands
    
    #Gets a linked Erbs username from db that matches the name passed in. Can only be done by users with manage_role permission
    @commands.command(pass_context=True, name="getUsername", brief="Gets Linked ERBS name")
    @commands.has_permissions(manage_roles=True)
    async def getUserErbsAccountName(self, ctx, member: discord.Member):
      """Gets the linked ERBS Username of a discord member."""
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
    @commands.command(pass_context=True, name="getAllUsernames", brief="Gets All linked ERBS names")
    @commands.has_permissions(manage_roles=True)
    async def getAllErbsAccountNames(self, ctx):
      """Gets All linked ERBS Usernames."""
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
    @commands.command(pass_context=True, name="setUsername", brief="Sets linked ERBS name", hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def setUserErbsAccountName(self, ctx, member: discord.Member, erbsAccountName: str, password: str):
      """Sets an user's linked ERBS Username."""
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
    @commands.command(pass_context=True, name="deleteUsername", brief="Removes linked ERBS name", hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def deleteUserErbsAccountName(self, ctx, member: discord.Member, password: str):
      """Removes linked ERBS Usernames from user."""
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

    @commands.command(pass_context=True, name="deleteAllLinkedUsernames", brief="Clears ERBS Usernames", hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def deleteAllErbsLinkedAccounts(self, ctx, password: str):
      """Removes All linked ERBS Usernames."""
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
        """Error handling for getErbsUser"""
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="getUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="getUserErbsAccountName", value="You are missing an argument, please pass in the discord name after the command.")
            await ctx.send(embed=embedVar)
        else:
            raise error

    @setUserErbsAccountName.error
    async def setErbsUser_error(self, ctx, error):
        """Error handling for setErbsUser"""
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="setUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="setUserErbsAccountName", value="You are missing an argument, please pass in the username and then the discord name after the command.")
            await ctx.send(embed=embedVar)
        else:
            raise error

    @deleteUserErbsAccountName.error
    async def unlinkUser_error(self, ctx, error):
        """Error handling for unlinkUser"""
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="unlinkUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="unlinkUserErbsAccountName", value="You are missing an argument, please pass in the discord name after the command.")
            await ctx.send(embed=embedVar)
        else:
            raise error

    @deleteAllErbsLinkedAccounts.error
    async def deleteAllNames_error(self, ctx, error):
      """Error handling for deleteAllErbsAccountNames"""
      if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="deleteAllErbsAccountNames", value=f"You passed in something that isn't a string.", inline=False)
        await ctx.send(embed=embedVar)
      elif isinstance(error, commands.MissingRequiredArgument):
        embedVar.add_field(name="deleteAllErbsAccountNames", value=f"You need to pass in a password for this command.", inline=False)
        await ctx.send(embed=embedVar)
      else:
        raise error

    @setUserErbsAccountName.error
    async def setUserErbsAccountName_error(self, ctx, error):
      """Error handling for setUserErbsAccountName"""
      if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="setUserErbsAccountName", value=f"There was no member in this discord with the name you provided.", inline=False)
        await ctx.send(embed=embedVar)
      elif isinstance(error, commands.MissingRequiredArgument):
        embedVar.add_field(name="setUserErbsAccountName", value=f"You need to pass in a discord name, username and, password for this command in that order.", inline=False)
        await ctx.send(embed=embedVar)
      else:
        raise error


#############################################
# Link
def setup(bot):
  """Adds extension as a cog"""
  bot.add_cog(DB(bot))

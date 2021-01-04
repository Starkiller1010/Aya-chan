import os

import discord
from discord import Forbidden
from discord.ext import commands
from discord.ext.commands import ConversionError

from ..bot import getEmbedVar

embedVar = getEmbedVar
ADMIN_SITE= f"{os.getenv('SITE_URL')}/admin"

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#####################################
# Commands

    # adminHelp : Returns url for admin commands.
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def adminHelp(self, ctx):
      embedVar.add_field(name="adminHelp", value=f"Check all the commands at {ADMIN_SITE}", inline=True)
      await ctx.send(embed=embedVar)

    # giveRole : Assigns role to any number of members that are passed
    @commands.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def giveRole(self, ctx, role: discord.Role, *members: discord.Member):
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

    # removeRole : Removes a role from any number of members passed
    @commands.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def removeRole(self, ctx, role: discord.Role, *members: discord.Member):
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

#####################################
# Error Handling

    @giveRole.error
    async def giveRole_error(self, ctx, error):
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="giveRole", value=f"There was no member in this discord with a name you have provided.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

    @removeRole.error
    async def removeRole_error(self, ctx, error):
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="removeRole", value=f"There was/were no member(s) in this discord with a name you have provided.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error
####################################
# Link    
def setup(bot):
    bot.add_cog(AdminCommands(bot))
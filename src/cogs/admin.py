import os

import discord
from discord import Forbidden
from discord.ext import commands
from discord.ext.commands import ConversionError

from ..bot import getEmbedVar

embedVar = getEmbedVar()
ADMIN_SITE= f"{os.getenv('SITE_URL')}/admin"

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#####################################
# Commands

    # giveRole : Assigns role to any number of members that are passed
    @commands.command(pass_context=True, brief="Adds role to member(s)")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def giveRole(self, ctx, role: discord.Role, *members: discord.Member):
        """Adds role to any number of members. This command requires any role for this bot to be above the role being assigned."""
        try:
          for member in members:
            if (ctx.guild.me.top_role.position > member.top_role.position 
                and not member.guild_permissions.administrator):
              await member.add_roles(role)
              embedVar.add_field(name="giveRole", value=f"{member.name} has been giving a role: [{role.name}].", inline=False)
              await ctx.send(embed=embedVar)
            else:
              embedVar.add_field(name="giveRole", value=f"{member.name} is a higher role than either the bot and/or the user.", inline=False)
              await ctx.send(embed=embedVar)
          return
        except Forbidden:
          embedVar.add_field(name="giveRole", value=f"Failed to give role to {member.name} because Aya-chan does not have permissions to do so. Please lower the targeted role in Role list or raise ERBS API Bot role higher than target.", inline=False)
          await ctx.send(embed=embedVar)
        except:
          embedVar.add_field(name="giveRole", value=f"Failed to give role to {member.name}.", inline=False)
          await ctx.send(embed=embedVar)

    # removeRole : Removes a role from any number of members passed
    @commands.command(pass_context=True, brief="Removes role from member(s)")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def removeRole(self, ctx, role: discord.Role, *members: discord.Member):
        """Removes role to any number of members. This command requires any role for this bot to be above the role being assigned."""
        try:
          for member in members:
            if (ctx.guild.me.top_role.position > member.top_role.position 
                and not member.guild_permissions.administrator):
              await member.remove_roles(role)
              embedVar.add_field(name="removeRole", value=f"{member.name} had the role: [{role.name}] removed.", inline=False)
              await ctx.send(embed=embedVar)
            else:
              embedVar.add_field(name="removeRole", value=f"{member.name} is a higher role than either the bot and/or the user.", inline=False)
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
        """Error handling for giveRole"""
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="giveRole", value=f"There was no member in this discord with a name you have provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="giveRole", value=f"You must pass a role AND at least one member name.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingPermissions):
            embedVar.add_field(name="giveRole", value=f"Either the bot or user does not have the necessary permissions to use this command.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

    @removeRole.error
    async def removeRole_error(self, ctx, error):
        """Error handling for removeRole"""
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="removeRole", value=f"There was/were no member(s) in this discord with a name you have provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="removeRole", value=f"You must pass a role AND at least one member name.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingPermissions):
            embedVar.add_field(name="removeRole", value=f"Either the bot or user does not have the necessary permissions to use this command.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error
####################################
# Link    
def setup(bot):
  """Adds extension as a cog"""
  bot.add_cog(AdminCommands(bot))

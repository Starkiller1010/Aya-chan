import os

import discord
from discord import Forbidden
from discord.ext import commands
from discord.ext.commands import ConversionError, Greedy
from ..logger import logInfo, logErr
from ..bot import getEmbedVar

from typing import Optional

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

    # Kick : Kicks a member from discord
    @commands.command(pass_context=True, brief="Kicks member(s) from discord")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, members: Greedy[discord.Member], *, reason: Optional[str]= "No reason provided."):
      """Removes all users passed in from the discord server."""
      for member in members:
        if (ctx.guild.me.top_role.position > member.top_role.position 
        and not member.guild_permissions.administrator):
          await member.kick(reason=reason)
          fields = [("Member kicked: ", f"{member.name}", True),
                    ("Actioned by", ctx.author.display_name, False),
                    ("Reason", reason, False)]
          embedVar.set_thumbnail(url=member.avatar_url)
          for name, value, inline in fields:
            embedVar.add_field(name=name, value=value, inline=inline)
        else:
          embedVar.add_field(name="kick", value=f"{member.name} could not be banned.", inline=False)
        await ctx.send(embed=embedVar)
      

    # ban : Bans a member from discord
    @commands.command(pass_context=True, brief="Bans member(s) from discord")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, members: Greedy[discord.Member], *, reason: Optional[str]= "No reason provided."):
      """Removes all users passed in from the discord server and puts them into ban list, preventing them from returning until removed from ban list."""
      for member in members:
        if (ctx.guild.me.top_role.position > member.top_role.position 
        and not member.guild_permissions.administrator):
          await member.ban(reason=reason)
          fields = [("Member banned: ", f"{member.name}", True),
                    ("Actioned by", ctx.author.display_name, False),
                    ("Reason", reason, False)]
          embedVar.set_thumbnail(url=member.avatar_url)
          for name, value, inline in fields:
            embedVar.add_field(name=name, value=value, inline=inline)
        else:
          embedVar.add_field(name="ban", value=f"{member.name} could not be banned.", inline=False)
        await ctx.send(embed=embedVar)

    # clear : Clears messages from channel used in
    @commands.command(name="clear", aliases=["purge"], brief="Clears messages")
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx,  members: Greedy[discord.Member], limit: Optional[int] = 1):
      """Deletes messages within the channel command is executed in. 
      Can change the number and specify members to delete messages from them."""
      def _targetCheck(message):
        return not len(members) or message.author in members

      if 0 < limit <= 100:
        with ctx.channel.typing():
          await ctx.message.delete()
          deleted = await ctx.channel.purge(limit=limit, check=_targetCheck)

          await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)
      else:
        await ctx.send(f"Please send a limit number between 1-100")

#####################################
# Error Handling

    @giveRole.error
    async def giveRole_error(self, ctx, error):
        """Error handling for giveRole"""
        logErr(f'Error within giveRole: {error}')
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="giveRole", value=f"There was/were no member(s) or role in this discord with a name you have provided.", inline=False)
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
        logErr(f'Error within removeRole: {error}')
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="removeRole", value=f"There was/were no member(s) or role in this discord with a name you have provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="removeRole", value=f"You must pass a role AND at least one member name.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingPermissions):
            embedVar.add_field(name="removeRole", value=f"Either the bot or user does not have the necessary permissions to use this command.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

    @kick.error
    async def kick_error(self, ctx, error):
        """Error handling for kick"""
        logErr(f'Error within kick command: {error}')
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="kick", value=f"There was/were no member(s) in this discord with a name you have provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="kick", value=f"You must pass at least one member name.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingPermissions):
            embedVar.add_field(name="kick", value=f"Either the bot or user does not have the necessary permissions to use this command.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

    @ban.error
    async def ban_error(self, ctx, error):
        """Error handling for ban"""
        logErr(f'Error within ban command: {error}')
        if isinstance(error, (ConversionError, commands.BadArgument)):
            embedVar.add_field(name="ban", value=f"There was/were no member(s) in this discord with a name you have provided.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingRequiredArgument):
            embedVar.add_field(name="ban", value=f"You must pass at least one member name.", inline=False)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.MissingPermissions):
            embedVar.add_field(name="ban", value=f"Either the bot or user does not have the necessary permissions to use this command.", inline=False)
            await ctx.send(embed=embedVar)
        else:
            raise error

    @clear_messages.error
    async def clear_error(self, ctx, error):
      """Error handling for clear messages"""
      logErr(f'Error within clear_messages: {error}')
      if isinstance(error, (ConversionError, commands.BadArgument)):
        embedVar.add_field(name="clear", value=f"There was/were no member(s) in this discord with a name you have provided.", inline=False)
        await ctx.send(embed=embedVar)
####################################
# Link    
def setup(bot):
  """Adds extension as a cog"""
  bot.add_cog(AdminCommands(bot))

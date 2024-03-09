import discord, logging
from discord.ext import commands as cmds
class moderation(cmds.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @cmds.hybrid_command(name="purge",
                    description="Purge a certain amount of messages. ")
  @discord.app_commands.describe(amount="The amount of messages to purge. ")
  @cmds.has_permissions(manage_messages=True)
  @cmds.guild_only()
  async def purge(self, ctx, amount: int):
    await ctx.reply(f"Purging {amount} messages...", ephemeral=True)
    await ctx.channel.purge(limit=amount + 1)
    await ctx.channel.send(f"Purged {amount} messages. ")

  

async def setup(bot):
  await bot.add_cog(moderation(bot))
  logging.info("moderation loaded. ")
import discord, json, logging
from discord.ext import commands as cmds
from time import time, sleep

from discord.ext.commands import cog

with open("templates.json") as f:
  templates = json.load(f)


def load_data():
  global data
  with open("data.json", "r") as f:
    data = json.load(f)


def save_data(data):
  with open("data.json", "w") as f:
    json.dump(data, f)
  load_data()


load_data()


class leveling(cmds.Cog, name="leveling"):

  def __init__(self, bot):
    self.bot = bot

  @cmds.Cog.listener()
  async def on_message(self, message):
    if message.author == self.bot.user:
      return
    load_data()
    i = 0
    while True:
      i += 1
      sleep(2)
      try:
        author_id = str(message.author.id)
        guild_id = str(message.guild.id)
      except KeyError:
        if i >= 10:
          return
      else:
        break
    try:
      guild_data = data[guild_id]
    except KeyError:
      return
    try:
      member = data[guild_id]["members"][author_id]
    except KeyError:
      member = data[guild_id]["members"][author_id]

    if member["leveling"]["xp"] >= 100:
      member["leveling"]["level"] += 1
      member["leveling"]["xp"] = 0
      await self.bot.get_channel(
          int(guild_data["settings"]["leveling"]["notify_channel"])
      ).send(guild_data["settings"]["leveling"]["notify_message"].replace(
          "@u",
          message.author.mention).replace("@l",
                                          str(member["leveling"]["level"])))
    if member["leveling"]["last_message"] >= time() - guild_data["settings"]["leveling"]["timeout"]:
      await message.add_reaction("🚫")

    else:
      member["leveling"]["messages"] += 1
      member["leveling"]["xp"] += guild_data["settings"]["leveling"]["xp_by_message"]
    #print(data)
    member["leveling"]["last_message"] = time()
    data[guild_id]["members"][author_id] = member
    save_data(data)

  @cmds.hybrid_command(
      name="leveling_settings",
      description="Change settings for the leveling feature of the bot.")
  @discord.app_commands.describe(
      notify_channel="Set the channel for level up notifications to be sent. ",
      notify_message=
      "Set the notification message. Use @u to mention the user and @l to mention the level.",
      xp_by_message=
      "Set the amount of XP a user gets per message. Level up at 100 XP",
      timeout=
      "Set the amount of time the bot will wait between giving XP from messages. (Seconds)"
  )
  @cmds.has_permissions(manage_guild=True)
  @cmds.guild_only()
  async def settings(
      self,
      ctx,
      notify_channel: discord.TextChannel = None,
      notify_message: str = None,
      xp_by_message: int = 5,
      timeout: int = 0,
  ):
    load_data()
    try:
      data[ctx.guild.id]
    except KeyError:
      await ctx.send("Please run ``/setup`` first.")
      return
    if notify_channel is not None:
      data[ctx.guild.id]["settings"]["leveling"][
          "notify_channel"] = notify_channel.id
    if notify_message is not None:
      data[ctx.guild.
           id]["settings"]["leveling"]["notify_message"] = notify_message
    if xp_by_message is not None:
      data[ctx.guild.
           id]["settings"]["leveling"]["xp_by_message"] = xp_by_message
    if timeout is not None:
      data[ctx.guild.id]["settings"]["leveling"]["timeout"] = timeout
    save_data(data)
    await ctx.send("Settings have been updated.")

  @cmds.hybrid_command(name="set_level",
                       description="Set a user's level and XP. ")
  @discord.app_commands.describe(level="The level to set the user to")
  @cmds.has_permissions(manage_guild=True)
  @cmds.guild_only()
  async def set_level(self, ctx, user: discord.Member, level: int):
    load_data()
    try:
      data[ctx.guild.id]
    except KeyError:
      await ctx.send("Please run ``/setup`` first and reset `ALL`. ")
      return
    try:
      member = data[ctx.guild.id]["members"][user.id]
    except KeyError:
      member = templates["member"]
    pastlevel = member["leveling"]["level"]
    member["leveling"]["level"] = level
    save_data(data)
    e = discord.Embed(title="Success")
    e.add_field(name="User", value=user.display_name, inline=False)
    e.add_field(name="Past Level", value=pastlevel, inline=True)
    e.add_field(name="Updated Level", value=level, inline=True)
    await ctx.send(embed = e)

  @cmds.hybrid_command(name="xp",
                       description="Get a user's XP, level, and messages. ")
  @discord.app_commands.describe(user="The user to get the XP of")
  @cmds.guild_only()
  async def get_stats(self, ctx, user: discord.Member = None):
    load_data()
    try:
      data[str(ctx.guild.id)]
    except KeyError:
      await ctx.send("Ask an admin to run ``/setup`` and reset `ALL` first.")
      return

    if user == None:
      user = ctx.author

    try:
      member = data[str(ctx.guild.id)]["members"][str(user.id)]
    except KeyError:
      member = templates["member"]
    myembed = discord.Embed(title=f"{user.display_name}'s Stats: ",
                            type="rich")
    myembed.add_field(name="Level",
                      value=member["leveling"]["level"],
                      inline=True)
    myembed.add_field(name="XP", value=member["leveling"]["xp"], inline=True)
    myembed.add_field(name="Messages",
                      value=member["leveling"]["messages"],
                      inline=True)
    await ctx.send(embed=myembed)


async def setup(bot):
  await bot.add_cog(leveling(bot))
  logging.info("leveling loaded.")

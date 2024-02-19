import discord, os, json
from discord.ext import commands

with open("data.json") as f:
  data = json.load(f)

with open("templates.json") as f:
  templates = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%!', intents=intents)


@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')
  await bot.tree.sync()


@bot.event
async def on_guild_join(guild):
  data[str(guild.id)] = templates[guild]


@bot.tree.command(name="ping", description="Pong!")
async def ping(interaction: discord.Interaction):
  await interaction.response.send_message(
      "I don't have time to play table tennis!")


@bot.event
async def on_message(message):
  author_id = message.author.id
  guild_id = message.guild.id
  try:
    guild_data = data[str(guild_id)]
  except KeyError:
    return
  if message.author == bot.user:
    return
  try:
    member = data[str(guild_id)]["members"][str(author_id)]
  except KeyError:
    member = templates["member"]

  ## Leveling
  member["leveling"]["messages"] += 1
  member["leveling"]["xp"] += guild_data["settings"]["leveling"][
      "xp_by_message"]
  if member["leveling"]["xp"] >= 100:
    #try:
    member["leveling"]["level"] += 1
    member["leveling"]["xp"] = 0
    await bot.get_channel(
        int(guild_data["settings"]["leveling"]["notify_channel"])
    ).send(guild_data["settings"]["leveling"]["notify_message"].replace(
        "@u",
        message.author.mention).replace("@l",
                                        str(member["leveling"]["level"])))

  data[str(guild_id)][str(author_id)] = member
  with open("data.json", "w") as f:
    json.dump(data, f)


@bot.tree.command(name="setup",
                  description="Resets all settings, but can fix errors. ")
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
  data[str(interaction.guild_id)] = templates["guild"]
  with open("data.json", "w") as f:
    json.dump(data, f)
  await interaction.response.send_message("All settings have been reset. ")


### LEVELING
##
##
@bot.tree.command(name="leveling_settings")
@discord.app_commands.describe(
    notify_channel="Set the channel for level up notifications to be sent. ",
    notify_message=
    "Set the notification message. Use @u to mention the user and @l to mention the level.",
    xp_by_message=
    "Set the amount of XP a user gets per message. Level up at 100 XP",
    timeout=
    "Set the amount of time the bot will wait between giving xp from messages. (Seconds)"
)
@commands.has_permissions(manage_guild=True)
async def leveling_settings(
    interaction: discord.Interaction,
    notify_channel: discord.TextChannel = None,
    notify_message: str = None,
    xp_by_message: int = 5,
    timeout: int = 0,
):
  try:
    data[str(interaction.guild.id)]
  except KeyError:
    await interaction.response.send_message("Please run ``/setup`` first.")
    return
  else:
    if notify_channel is not None:
      data[str(interaction.guild.id
               )]["settings"]["leveling"]["notify_channel"] = notify_channel.id
    if notify_message is not None:
      data[str(interaction.guild.id
               )]["settings"]["leveling"]["notify_message"] = notify_message
    if xp_by_message is not None:
      data[str(interaction.guild.id
               )]["settings"]["leveling"]["xp_by_message"] = xp_by_message
    if timeout is not None:
      data[str(
          interaction.guild.id)]["settings"]["leveling"]["timeout"] = timeout
    with open("data.json", "w") as f:
      json.dump(data, f)
    await interaction.response.send_message("Settings have been updated.")


###MODERATION
##

bot.run(os.environ['TOKEN'])

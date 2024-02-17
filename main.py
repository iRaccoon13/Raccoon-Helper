import discord, os, json
from discord.ext import commands

with open("data.json") as f:
  data = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')
  await bot.tree.sync()


@bot.event
async def on_guild_join(guild):
  data[str(guild.id)] = {
      "settings": {
          "notify_channel": "",
          "notify_message": "",
          "timeout": 0,
          "xp_by_message": 0,
          "blacklisted_channels": [],
          "blacklisted_roles": [],
          "blacklisted_text": []
      },
      "members": {}
  }


@bot.tree.command(name="ping", description="Pong!")
async def ping(interaction: discord.Interaction):
  await interaction.response.send_message(
      "I don't have time to play table tennis!")


@bot.event
async def on_message(message):
  try:
    data[str(message.guild.id)]
  except KeyError:
    return
  if message.author == bot.user:
    return
  if message.content in data[str(
      message.guild.id)]["settings"]["blacklisted_text"]:
    return
  if message.channel in data[str(
      message.guild.id)]["settings"]["blacklisted_channels"]:
    return
  for role in message.author.roles:
    if role in data[str(message.guild.id)]["settings"]["blacklisted_roles"]:
      return
  if message.author.id not in list(data[str(
      message.guild.id)]["members"].keys()):
    print("hello")
    data[str(message.guild.id)]["members"][str(message.author.id)] = {
        "level": 0,
        "xp": 0,
        "messages": 1
    }
  data[str(message.guild.id)]["members"][str(
      message.author.id)]["messages"] += 1
  data[str(message.guild.id)]["members"][str(
      message.author.id)]["xp"] += data[str(
          message.guild.id)]["settings"]["xp_by_message"]

  with open("data.json", "w") as f:
    json.dump(data, f)


@bot.tree.command(name="setup", description="Resets all settings")
#@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
  data[str(interaction.guild_id)] = {
      "settings": {
          "notify_channel": "",
          "notify_message": "",
          "timeout": 0,
          "xp_by_message": 0,
          "blacklisted_channels": [],
          "blacklisted_roles": [],
          "blacklisted_text": []
      },
      "members": {}
  }
  with open("data.json", "w") as f:
    json.dump(data, f)
  await interaction.response.send_message("All settings have been reset")


@bot.tree.command(
    name="notifychannel",
    description="""Set the channel to send notifications to on level up""")
@commands.has_permissions(manage_guild=True)
async def notifychannel(interaction: discord.Interaction,
                        channel: discord.TextChannel):
  try:
    data[str(interaction.guild_id)]["settings"]["notify_channel"] = channel.id
    with open("data.json", "w") as f:
      json.dump(data, f)
  except ValueError:
    await interaction.response.send_message("Please run ``/setup`` first.")
  else:
    await interaction.response.send_message(
        f"Set notify channel to {channel.mention}")


@bot.tree.command(name="settings")
@discord.app_commands.describe(
    notifymessage=
    "Set the notification message. Use @u to mention the user and @l to mention the level."
)
@commands.has_permissions(manage_guild=True)
async def notifymessage(interaction: discord.Interaction, notifymessage: str):
  data[str(interaction.guild_id)]["settings"]["notify_message"] = notifymessage


bot.run(os.environ['TOKEN'])

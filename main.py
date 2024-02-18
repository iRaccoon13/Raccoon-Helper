import discord, os, json
from discord.ext import commands

with open("data.json") as f:
  data = json.load(f)

with open("templates.json") as f:
  templates = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


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
    data[str(message.guild.id)]["members"][str(message.author.id)] = templates["member"]
  data[str(message.guild.id)]["members"][str(
      message.author.id)]["messages"] += 1
  data[str(message.guild.id)]["members"][str(
      message.author.id)]["xp"] += data[str(
          message.guild.id)]["settings"]["xp_by_message"]

  with open("data.json", "w") as f:
    json.dump(data, f)


@bot.tree.command(name="setup", description="Resets all settings, but can fix errors. ")
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
  data[str(interaction.guild_id)] = templates[guild]
  with open("data.json", "w") as f:
    json.dump(data, f)
  await interaction.response.send_message("All settings have been reset. Now, run ``/settings``")


@bot.tree.command(
    name="notifychannel",
    description="""Set the channel to send notifications to on level up""")
@commands.has_permissions(manage_guild=True)
async def notifychannel(interaction: discord.Interaction,
                        channel: discord.TextChannel):

 

@bot.tree.command(name="settings leveling")
@discord.app_commands.describe(
    notify_channel="Set the channel for level up notifications to be sent. ",
    notify_message="Set the notification message. Use @u to mention the user and @l to mention the level.",
    xp_by_message="Set the amount of XP a user gets per message. Level up at 100 XP",
    timeout="Set the amount of time the bot will wait between giving xp from messages. (Seconds)")
@commands.has_permissions(manage_guild=True)
async def leveling_settings(interaction: discord.Interaction, 
    notify_channel:discord.TextChannel=None, 
    notify_message:str=None, 
    xp_by_message:int=5,
    timeout:int=0,
    ):
  try:
    data[str(interaction.guild.id)]
  except KeyError:
    await interaction.response.send_message("Please run ``/setup`` first.")
  args = locals()
  for option in [for item in args().keys() if args[item] != None and args[item] != interaction]:
    data[str(interaction.guild_id)]["settings"]["leveling"][option] = args[option]


bot.run(os.environ['TOKEN'])

import discord, json, logging
from discord.ext import commands as cmds
from time import sleep

class Confirm(discord.ui.View):
  def __init__(self):
    super().__init__()
    self.value = None

  # When the confirm button is pressed, set the inner value to `True` and
  # stop the View from listening to more input.
  # We also send the user an ephemeral message that we're confirming their choice.
  @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
  async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message('Confirming', ephemeral=True)
    self.value = True
    self.stop()

  # This one is similar to the confirmation button except sets the inner value to `False`
  @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
  async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.message.delete()
    await interaction.response.send_message('Cancelling', ephemeral=True)
    self.value = False
    self.stop()


def load_data():
  global data
  with open("data.json", "r") as f:
    data = json.load(f)


def save_data(data):
  with open("data.json", "w") as f:
    json.dump(data, f)


load_data()
with open("templates.json") as f:
  templates = json.load(f)


class misc(cmds.Cog):

  def __init__(self, bot):
    self.bot = bot

  @cmds.Cog.listener()
  async def on_guild_join(self, guild):
    load_data()
    data[str(guild.id)] = templates["guild"]
    save_data(data)

  @cmds.hybrid_command(name="ping", description="Pong!")
  async def ping(self, ctx):
    await ctx.send(
        f"I don't have time to play table tennis! Latency is `{round(self.bot.latency * 1000)}` ms. "
    )

  @cmds.Cog.listener()
  async def on_message(self, message):
    if message.author == self.bot.user:
      return
    load_data()
    author_id = str(message.author.id)
    guild_id = str(message.guild.id)
    guild_data = data[guild_id]
    try:
      member = guild_data["members"][author_id]
    except KeyError:
      member = templates["member"]
    guild_data["members"][author_id] = member
    data[guild_id] = guild_data
    save_data(data)

  @cmds.hybrid_command(name="setup",
                       description="Resets all settings, but can fix errors. ")
  @cmds.has_permissions(manage_guild=True)
  @cmds.guild_only()
  async def reset_settings(self, ctx):
    load_data()
    e = discord.Embed(title="Reset:",description="Choose an item to reset. ")

    class S(discord.ui.Select):
      def __init__(self):
        options=[
            discord.SelectOption(label="All",description="Reset EVERYTHING, including levels and moderation. "),
            discord.SelectOption(label="Leveling settings",description="Reset leveling settings. "),
            discord.SelectOption(label="Games settings",emoji="🎲",description="Reset games settings. ")
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
      async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        view = Confirm()
        await ctx.send(embed=discord.Embed(title="Are you sure?",description=f"Are you sure you want to reset `{self.values[0]}`?"),view=view)
        await view.wait()
        if view.value == None:
          interaction.message.delete()
        elif view.value == True:
          if self.values[0] == "ALL":
            data[str(interaction.guild.id)] = templates["guild"]
          elif self.values[0] == "Leveling settings":
            data[str(interaction.guild.id)]["settings"]["leveling"] = templates["guild"]["settings"]["leveling"]
        
        
    class V(discord.ui.View):
      def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(S())
        
    await ctx.send(embed=e, view=V())
  


async def setup(bot):
  await bot.add_cog(misc(bot))
  logging.info("misc loaded.")

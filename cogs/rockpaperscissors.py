import discord, json
from discord.ext import commands as cmds
from time import time
from ..other import views

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

class item_select(discord.ui.Select):
  def __init__(self):
    options=[
        discord.SelectOption(label="Rock",emoji="🗿",description="Heavy"),
        discord.SelectOption(label="Paper",emoji="�",description="It blows  away"),
        discord.SelectOption(label="Scissors",emoji="✂️",description="Snip Snip")
        ]
    super().__init__(placeholder="What's your choice?",max_values=1,min_values=1,options=options)
  async def callback(self, interaction: discord.Interaction):
    v = views.Confirm()
    await interaction.response.send_message(embed=discord.Embed(title="Are you sure? ", description=f"You chose {self.values[0]}"), view=v, ephemeral=True)
    game = data[f"{interaction.guild.id}"]["games"][f"{interaction.channel.id}"]
    await v.wait()
    if v.value == None:
      await interaction.message.delete()
    elif v.value == True:
      templateplayer = {
        "name": interaction.user.display_name,
        "choice": self.values[0] or None
      }
      game["players"][interaction.user] = templateplayer
    

class item_view(discord.ui.View):
  def __init__(self):
    self.add_item(item_select())
  @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
  async def callback(self, interaction: discord.Interaction, button: discord.Button):
    
    pass

class new_game_view(discord.ui.View):
  @discord.ui.Button(label="Join",style=discord.ButtonStyle.green)
  async def callback(self, interaction: discord.Interaction, button: discord.Button):
    e = discord.Embed(title="Select an item to join", description="We'll DM you if you win. ")
    v = item_view()
    await interaction.response.send_message(embed=e, view=v, ephemeral=True)
    
class rockpaperscissors_cog(cmds.Cog):
  def __init__(self, bot):
    self.bot = bot
  @cmds.hybrid_command(name="rockpaperscissors")
  async def new_game(self, ctx):
    load_data()
    guild_id = str(ctx.guild.id)
    templategame = {
      "type": "rockpaperscissors", 
      "creator": ctx.author, 
      "created_at": time(),
      "players": {}
    }
    data[guild_id]["games"][str(ctx.channel.id)] = templategame
    e = discord.Embed(title="Rock Paper Scissors Tournament", description="Press the button to join the tournament. ")
    await ctx.send(embed=e,view=new_game_view())
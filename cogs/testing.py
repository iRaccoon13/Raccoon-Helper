import discord
from discord.ext import commands as cmds

class test_cog(cmds.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  class test_view(discord.ui.View):
    @discord.ui.button(label="<",style=discord.ButtonStyle.green, disabled=False)
    async def button1_onclick(self, interaction: discord.Interaction, button: discord.ui.Button):
      button.disabled = True
      await interaction.response.edit_message(content="yay" if interaction.message.content != "yay" else "woohoo")

  @cmds.hybrid_command(name="testcommand")
  async def testcommand(self, ctx):
    await ctx.send("hello", view=self.test_view())

async def setup(bot):
  await bot.add_cog(test_cog(bot))
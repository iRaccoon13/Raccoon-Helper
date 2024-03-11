import discord, os, json, asyncio, logging
from discord.ext import commands
from discord.interactions import Interaction

discord.utils.setup_logging(level=logging.INFO)

cogs = [
  "leveling",
  "misc",
  "moderation"
]


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

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="R! ", intents=intents)

    
@bot.hybrid_command(name="reload", description="Reloads cogs.")
@commands.is_owner()
async def reload(ctx, cog: str):
  if ctx.author.id == 789003007601410048:
    try:
      await bot.reload_extension(f"cogs.{cog}")
      await ctx.send(f"Reloaded {cog}", ephemeral=True)
    except Exception as e:
      await ctx.send(f"Error reloading {cog}: {e}", ephemeral=True)
  else:
    await ctx.send("You do not have permission to use this command.", ephemeral=True)

  
@reload.error
async def reload_error(error, ctx):
  if isinstance(error, commands.errors.NotOwner):
    ctx.send("You can't use this! ", ephemeral=True)

@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')
  await bot.tree.sync()


async def load_exts(bot):
  for cog in cogs:
    await bot.load_extension(f"cogs.{cog}")


asyncio.run(load_exts(bot))

bot.run(os.environ["TOKEN"], log_handler=logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w'))

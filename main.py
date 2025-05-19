import os
import discord
from discord.ext import commands

TOKEN = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(TOKEN)
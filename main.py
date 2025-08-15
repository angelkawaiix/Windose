import os
import discord

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print(f'Logged in as: {client.user}')


client.run(TOKEN)

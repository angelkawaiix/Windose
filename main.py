import asyncio
import logging
import logging.handlers
import os
import random
import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
logger = logging.getLogger('bot')

# Bot configuration
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Bot events
@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game(
      name="Needy Streamer Overload"))
  print(f'Logged in as {bot.user.name} - {bot.user.id}')
  
  # Sync slash commands
  try:
    synced = await bot.tree.sync()
    logger.info(f'Synced {len(synced)} command(s)')
  except Exception as e:
    logger.error(f'Failed to sync commands: {e}')


@bot.event
async def on_error(event, *args, **kwargs):
  """Triggered when an error occurs in any bot event"""
  logger.error(f'An error occurred in event {event}', exc_info=True)


@bot.event
async def on_disconnect():
  """Triggered when the bot loses connection to Discord"""
  logger.warning('Bot disconnected from Discord')


@bot.event
async def on_resumed():
  """Triggered when the bot reconnects to Discord after a disconnection"""
  logger.info('Bot resumed connection to Discord')


# Slash commands
@bot.tree.command(name="windose_daily_event", description="Get a random daily task to complete")
async def windose_daily_event(interaction: discord.Interaction):
  """Select a random task from tasks.txt and send it as a message"""
  try:
    # Get random task
    with open('tasks/tasks.txt', 'r', encoding='utf-8') as file:
      tasks = [line.strip() for line in file.readlines() if line.strip()]
    
    if not tasks:
      await interaction.response.send_message("No tasks found in the file!", ephemeral=True)
      return
    
    random_task = random.choice(tasks)
    
    # Get random image
    image_files = [f for f in os.listdir('images') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if not image_files:
      await interaction.response.send_message("No images found in the images folder!", ephemeral=True)
      return
    
    random_image = random.choice(image_files)
    image_path = f'images/{random_image}'
    
    embed = discord.Embed(
      title="⊹₊ ⋆ ʚ┊ Daily task ┊ ɞ ⊹₊ ⋆",
      description=random_task,
      color=0xFF69B4
    )
    embed.set_footer(text="Have a productive day! 💕")
    
    # Attach the image file
    with open(image_path, 'rb') as image_file:
      file = discord.File(image_file, filename=random_image)
      embed.set_image(url=f"attachment://{random_image}")
      
      await interaction.response.send_message(embed=embed, file=file)
      logger.info(f'Sent daily task to {interaction.user}: {random_task} with image: {random_image}')
    
  except FileNotFoundError as e:
    await interaction.response.send_message("Required files not found!", ephemeral=True)
    logger.error(f'File not found: {e}')
  except Exception as e:
    await interaction.response.send_message("An error occurred while getting your task!", ephemeral=True)
    logger.error(f'Error in windose_daily_event command: {e}', exc_info=True)


# Auto-ping function
async def auto_ping():
  """Automatically ping the bot every 5 minutes invisibly (logs only)"""
  while True:
    try:
      await asyncio.sleep(300)  # Wait 5 minutes
      if bot.is_ready():
        logger.info(
            f'🏓 Auto-ping: Bot is alive! Connected to {len(bot.guilds)} guilds'
        )
        logger.info(f'Auto-ping: Latency: {round(bot.latency * 1000)}ms')
      else:
        logger.warning('Auto-ping: Bot is not ready, skipping ping')
    except Exception as e:
      logger.error(f'Auto-ping error: {e}', exc_info=True)


# Start the bot
if __name__ == "__main__":
  logger.info('Starting bot...')
  bot.run(TOKEN)

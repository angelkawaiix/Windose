import os
import discord
import logging
import asyncio

# ===== LOGGING CONFIGURATION SECTION =====
# This section sets up comprehensive logging for the bot
# It configures both general logging and Discord-specific logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.
    INFO,  # Log INFO level and above (INFO, WARNING, ERROR, CRITICAL)
    format=
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format with timestamp
    handlers=[logging.StreamHandler()]  # Output logs to console
)

# Configure Discord.py library logging to show internal Discord operations
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)

# Create a custom logger specifically for our bot events
logger = logging.getLogger('bot')

# ===== BOT CONFIGURATION SECTION =====
# This section handles bot token and client setup

# Get Discord bot token from environment variables (set in Secrets)
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

# Set up Discord client with default intents (permissions for what the bot can see)
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ===== BOT STARTUP EVENTS SECTION =====
# These events handle when the bot starts up and connects to Discord


@client.event
async def on_ready():
  """Triggered when the bot successfully connects to Discord"""
  logger.info(
      f'Bot is ready! Logged in as: {client.user} (ID: {client.user.id})')
  logger.info(f'Connected to {len(client.guilds)} guilds')
  # Log information about each server (guild) the bot is in
  for guild in client.guilds:
    logger.info(
        f'  - {guild.name} (ID: {guild.id}) - {guild.member_count} members')
  # Start the auto-ping task
  client.loop.create_task(auto_ping())


# ===== ERROR HANDLING SECTION =====
# These events handle errors and connection issues


@client.event
async def on_error(event, *args, **kwargs):
  """Triggered when an error occurs in any bot event"""
  logger.error(f'An error occurred in event {event}', exc_info=True)


@client.event
async def on_disconnect():
  """Triggered when the bot loses connection to Discord"""
  logger.warning('Bot disconnected from Discord')


@client.event
async def on_resumed():
  """Triggered when the bot reconnects to Discord after a disconnection"""
  logger.info('Bot resumed connection to Discord')


# ===== AUTO-PING SECTION =====
# This section handles the automatic invisible self-ping every 5 minutes


async def auto_ping():
  """Automatically ping the bot every 5 minutes invisibly (logs only, no messages)"""
  while True:
    try:
      await asyncio.sleep(300)  # Wait 5 minutes (300 seconds)
      if client.is_ready():
        # Invisible ping - just log that the bot is alive
        logger.info(
            f'🏓 Auto-ping: Bot is alive! Connected to {len(client.guilds)} guilds'
        )
        logger.info(f'Auto-ping: Latency: {round(client.latency * 1000)}ms')
      else:
        logger.warning('Auto-ping: Bot is not ready, skipping ping')
    except Exception as e:
      logger.error(f'Auto-ping error: {e}', exc_info=True)


# ===== BOT STARTUP SECTION =====
# This section starts the bot and connects to Discord

logger.info('Starting bot...')
client.run(TOKEN)  # Start the bot using the Discord token

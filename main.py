
import os
import discord
import logging

# ===== LOGGING CONFIGURATION SECTION =====
# This section sets up comprehensive logging for the bot
# It configures both general logging and Discord-specific logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,  # Log INFO level and above (INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format with timestamp
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
    logger.info(f'Bot is ready! Logged in as: {client.user} (ID: {client.user.id})')
    logger.info(f'Connected to {len(client.guilds)} guilds')
    # Log information about each server (guild) the bot is in
    for guild in client.guilds:
        logger.info(f'  - {guild.name} (ID: {guild.id}) - {guild.member_count} members')

# ===== MESSAGE HANDLING SECTION =====
# This section logs all messages the bot receives

@client.event
async def on_message(message):
    """Triggered every time a message is sent in a server or DM the bot can see"""
    logger.info(
        f'Message received: "{message.content}" from {message.author} in {message.guild.name if message.guild else "DM"}'
    )

# ===== SERVER (GUILD) EVENTS SECTION =====
# These events track when the bot joins or leaves servers

@client.event
async def on_guild_join(guild):
    """Triggered when the bot is added to a new server"""
    logger.info(f'Joined guild: {guild.name} (ID: {guild.id}) - {guild.member_count} members')

@client.event
async def on_guild_remove(guild):
    """Triggered when the bot is removed from a server"""
    logger.info(f'Left guild: {guild.name} (ID: {guild.id})')

# ===== MEMBER EVENTS SECTION =====
# These events track when users join or leave servers

@client.event
async def on_member_join(member):
    """Triggered when a new member joins a server the bot is in"""
    logger.info(f'Member joined: {member.name} in {member.guild.name}')

@client.event
async def on_member_remove(member):
    """Triggered when a member leaves a server the bot is in"""
    logger.info(f'Member left: {member.name} from {member.guild.name}')

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

# ===== BOT STARTUP SECTION =====
# This section starts the bot and connects to Discord

logger.info('Starting bot...')
client.run(TOKEN)  # Start the bot using the Discord token

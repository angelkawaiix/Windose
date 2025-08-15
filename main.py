import os
import discord
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Set discord.py logging to INFO level to see all actions
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)

# Create a logger for your bot
logger = logging.getLogger('bot')

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as: {client.user} (ID: {client.user.id})')
    logger.info(f'Connected to {len(client.guilds)} guilds')
    for guild in client.guilds:
        logger.info(f'  - {guild.name} (ID: {guild.id}) - {guild.member_count} members')

@client.event
async def on_message(message):
    logger.info(f'Message received: "{message.content}" from {message.author} in {message.guild.name if message.guild else "DM"}')

@client.event
async def on_guild_join(guild):
    logger.info(f'Joined guild: {guild.name} (ID: {guild.id}) - {guild.member_count} members')

@client.event
async def on_guild_remove(guild):
    logger.info(f'Left guild: {guild.name} (ID: {guild.id})')

@client.event
async def on_member_join(member):
    logger.info(f'Member joined: {member.name} in {member.guild.name}')

@client.event
async def on_member_remove(member):
    logger.info(f'Member left: {member.name} from {member.guild.name}')

@client.event
async def on_error(event, *args, **kwargs):
    logger.error(f'An error occurred in event {event}', exc_info=True)

@client.event
async def on_disconnect():
    logger.warning('Bot disconnected from Discord')

@client.event
async def on_resumed():
    logger.info('Bot resumed connection to Discord')

logger.info('Starting bot...')
client.run(TOKEN)

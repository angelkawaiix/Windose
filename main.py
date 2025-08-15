import os
import discord
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
logger = logging.getLogger('bot')

# Bot configuration
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """Triggered when the bot successfully connects to Discord"""
    logger.info(f'Bot is ready! Logged in as: {client.user} (ID: {client.user.id})')
    logger.info(f'Connected to {len(client.guilds)} guilds')

    for guild in client.guilds:
        logger.info(f'  - {guild.name} (ID: {guild.id}) - {guild.member_count} members')

    client.loop.create_task(auto_ping())


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


async def auto_ping():
    """Automatically ping the bot every 5 minutes invisibly (logs only)"""
    while True:
        try:
            await asyncio.sleep(300)  # Wait 5 minutes
            if client.is_ready():
                logger.info(f'🏓 Auto-ping: Bot is alive! Connected to {len(client.guilds)} guilds')
                logger.info(f'Auto-ping: Latency: {round(client.latency * 1000)}ms')
            else:
                logger.warning('Auto-ping: Bot is not ready, skipping ping')
        except Exception as e:
            logger.error(f'Auto-ping error: {e}', exc_info=True)


if __name__ == "__main__":
    logger.info('Starting bot...')
    client.run(TOKEN)
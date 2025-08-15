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



# Helper functions for tracking user responses
def ensure_response_files():
  """Ensure response tracking files exist"""
  os.makedirs('responses', exist_ok=True)
  for filename in ['did_it.txt', 'tried.txt', 'did_not_do.txt']:
    filepath = f'responses/{filename}'
    if not os.path.exists(filepath):
      open(filepath, 'w').close()

def remove_user_from_all_files(user_id):
  """Remove user from all response files"""
  files = ['responses/did_it.txt', 'responses/tried.txt', 'responses/did_not_do.txt']
  for filepath in files:
    if os.path.exists(filepath):
      with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() != str(user_id)]
      with open(filepath, 'w') as f:
        f.write('\n'.join(lines) + ('\n' if lines else ''))

def add_user_to_file(user_id, filename):
  """Add user to specific response file"""
  filepath = f'responses/{filename}'
  with open(filepath, 'a') as f:
    f.write(f'{user_id}\n')

class TaskResponseView(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
    
  @discord.ui.button(label="I did it! ✅", style=discord.ButtonStyle.success)
  async def did_it(self, interaction: discord.Interaction, button: discord.ui.Button):
    ensure_response_files()
    remove_user_from_all_files(interaction.user.id)
    add_user_to_file(interaction.user.id, 'did_it.txt')
    await interaction.response.send_message("Great job! You completed your task! 🎉", ephemeral=True)
    logger.info(f'{interaction.user} marked task as completed')
    
  @discord.ui.button(label="I tried 💪", style=discord.ButtonStyle.secondary)
  async def tried(self, interaction: discord.Interaction, button: discord.ui.Button):
    ensure_response_files()
    remove_user_from_all_files(interaction.user.id)
    add_user_to_file(interaction.user.id, 'tried.txt')
    await interaction.response.send_message("Good effort! Trying is what matters! 💪", ephemeral=True)
    logger.info(f'{interaction.user} marked task as attempted')
    
  @discord.ui.button(label="I did not do it 😔", style=discord.ButtonStyle.danger)
  async def did_not_do(self, interaction: discord.Interaction, button: discord.ui.Button):
    ensure_response_files()
    remove_user_from_all_files(interaction.user.id)
    add_user_to_file(interaction.user.id, 'did_not_do.txt')
    await interaction.response.send_message("That's okay! Tomorrow is a new day! 🌅", ephemeral=True)
    logger.info(f'{interaction.user} marked task as not completed')



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
@bot.tree.command(name="windose_end_day", description="View daily task completion summary")
async def windose_end_day(interaction: discord.Interaction):
  """Display summary of daily task completions"""
  try:
    ensure_response_files()
    
    # Get random image
    image_files = [f for f in os.listdir('images') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if not image_files:
      await interaction.response.send_message("No images found in the images folder!", ephemeral=True)
      return
    
    random_image = random.choice(image_files)
    image_path = f'images/{random_image}'
    
    # Read user responses from files
    def read_user_ids(filename):
      filepath = f'responses/{filename}'
      if os.path.exists(filepath):
        with open(filepath, 'r') as f:
          return [line.strip() for line in f.readlines() if line.strip()]
      return []
    
    completed_users = read_user_ids('did_it.txt')
    attempted_users = read_user_ids('tried.txt')
    not_completed_users = read_user_ids('did_not_do.txt')
    
    # Get all guild members (excluding bots)
    guild_members = [member for member in interaction.guild.members if not member.bot]
    all_participated = set(completed_users + attempted_users + not_completed_users)
    not_participated = [str(member.id) for member in guild_members if str(member.id) not in all_participated]
    
    # Build summary text
    summary_text = "**Users who completed the task:**\n"
    if completed_users:
      for user_id in completed_users:
        try:
          user = await bot.fetch_user(int(user_id))
          summary_text += f"• {user.display_name}\n"
        except:
          summary_text += f"• Unknown User ({user_id})\n"
    else:
      summary_text += "• None\n"
    
    summary_text += f"\n**Users who attempted:** {len(attempted_users)}\n"
    summary_text += f"**Users who didn't complete it:** {len(not_completed_users)}\n"
    summary_text += f"**Users who didn't participate:** {len(not_participated)}"
    
    embed = discord.Embed(
      title="⊹₊ ⋆ ʚ┊ Daily task summary ┊ ɞ ⊹₊ ⋆",
      description=summary_text,
      color=0xFF69B4
    )
    embed.set_footer(text="Great work today everyone! 💕")
    
    # Attach the image file
    with open(image_path, 'rb') as image_file:
      file = discord.File(image_file, filename=random_image)
      embed.set_image(url=f"attachment://{random_image}")
      
      await interaction.response.send_message(embed=embed, file=file)
      logger.info(f'Sent daily task summary to {interaction.user} with image: {random_image}')
      
      # Reset all response files after sending summary
      for filename in ['did_it.txt', 'tried.txt', 'did_not_do.txt']:
        filepath = f'responses/{filename}'
        with open(filepath, 'w') as f:
          f.write('')  # Clear the file
      logger.info('Reset all response files for new day')
    
  except Exception as e:
    await interaction.response.send_message("An error occurred while getting the summary!", ephemeral=True)
    logger.error(f'Error in windose_end_day command: {e}', exc_info=True)


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
    
    # Create buttons
    view = TaskResponseView()
    
    # Attach the image file
    with open(image_path, 'rb') as image_file:
      file = discord.File(image_file, filename=random_image)
      embed.set_image(url=f"attachment://{random_image}")
      
      await interaction.response.send_message(embed=embed, file=file, view=view)
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

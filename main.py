import discord
from discord.ext import commands

import bot_commands
import user_commands
import roles

intents = discord.Intents.all()
intents.guilds = True
intents.members = True
intents.messages = True

client = commands.Bot(command_prefix='!', intents=intents)

# gg 
token = ""

@client.event
async def on_ready():
    print(f'Bot has been initiated! {client.user}')

bot_commands.setup(client)
user_commands.setup(client)
roles.setup(client)

# Log in with the bot token
client.run(token)

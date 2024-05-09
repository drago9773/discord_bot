import discord
from discord.ext import commands

import bot_commands
import roles
import mod

intents = discord.Intents.all()
intents.guilds = True
intents.members = True
intents.messages = True  # Enable message content intent

client = commands.Bot(command_prefix='!', intents=intents)

# gg 
token = "MTIxNzcxMzAxMzc5Mjk2NDYyOA.GpZwr2.RVKfctk2b2lVcTWc5SUQU3l6gfQ0Ml4vkGEM2w"

@client.event
async def on_ready():
    print(f'Bot has been initiated! {client.user}')

bot_commands.setup(client)
user_commands.setup(client)
roles.setup(client)

# Log in with the bot token
client.run(token)

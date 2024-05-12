import discord
from discord.ext import commands

# Checks if the user is 'mod' role
def is_mod(guild, user_id):
    member = guild.get_member(user_id)
    if member is not None:
        mod_role = discord.utils.get(guild.roles, name="mod")
        return mod_role in member.roles
    return False
def is_mger(ctx):
    mger_role = discord.utils.get(ctx.guild.roles, name="mger")
    return mger_role in ctx.author.roles

roles_id = 1238924147971719292

# Based on the message ID, if the user reacts to a message they can
# be assigned the corresponding role.
def setup(client):
    @client.event
    @commands.check(is_mger)
    async def on_raw_reaction_add(payload):
        message_id = payload.message_id
        if message_id == roles_id:
            guild = client.get_guild(payload.guild_id)
            
            if payload.emoji.name == '1v1':
                print("1v1")
                role = discord.utils.get(guild.roles, name='1v1')  
            elif payload.emoji.name == 'EU':
                print("test")
                role = discord.utils.get(guild.roles, name='EU') 
            elif payload.emoji.name == 'SA':
                print("test")
                role = discord.utils.get(guild.roles, name='SA') 
            else:
                role = discord.utils.get(guild.roles, name=payload.emoji.name) 

            if role is not None:
                member = guild.get_member(payload.user_id)
                if member is not None:
                    await member.add_roles(role)
                    print("Done.")
            else:
                print("Role not found.")
    @client.event
    @commands.check(is_mger)
    async def on_raw_reaction_remove(payload):
        message_id = payload.message_id
        if message_id == roles_id:
            guild = client.get_guild(payload.guild_id)
            is_user_mod = is_mod(guild, payload.user_id)  # Call is_mod function to check if the user is a moderator
            if payload.emoji.name == '1v1':
                print("1v1")
                role = discord.utils.get(guild.roles, name='1v1')  
            elif payload.emoji.name == 'EU':
                print("EU")
                role = discord.utils.get(guild.roles, name='EU') 
            elif payload.emoji.name == 'SA':
                print("SA")
                role = discord.utils.get(guild.roles, name='SA') 
            else:
                role = discord.utils.get(guild.roles, name=payload.emoji.name) 

            if role is not None:
                member = guild.get_member(payload.user_id)
                if member is not None:
                    await member.remove_roles(role)
                    print("Done.")
            elif not is_user_mod:
                print("No permissions.")
            else:
                print("Role not found.")
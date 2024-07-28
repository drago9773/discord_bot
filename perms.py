import discord

def is_mod(ctx):
    role = discord.utils.get(ctx.guild.roles, name="admin")
    return role in ctx.author.roles
def is_mger(ctx):
    role = discord.utils.get(ctx.guild.roles, name="mger")
    return role in ctx.author.roles
def is_cup_3(ctx):
    role = discord.utils.get(ctx.guild.roles, name="CUP 3")
    return role in ctx.author.roles
def is_cup_4(ctx):
    role = discord.utils.get(ctx.guild.roles, name="CUP 4 Invite")
    return role in ctx.author.roles

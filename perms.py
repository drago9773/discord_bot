import discord

def is_mod(ctx):
    mod_role = discord.utils.get(ctx.guild.roles, name="admin")
    return mod_role in ctx.author.roles
def is_mger(ctx):
    mger_role = discord.utils.get(ctx.guild.roles, name="mger")
    return mger_role in ctx.author.roles
def is_cup_3(ctx):
    mger_role = discord.utils.get(ctx.guild.roles, name="CUP 3")
    return mger_role in ctx.author.roles
def is_cup_4(ctx):
    mger_role = discord.utils.get(ctx.guild.roles, name="CUP 4 Invite")
    return mger_role in ctx.author.roles

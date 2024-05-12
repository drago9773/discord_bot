import discord
import re
import webscrape
import math
from discord.ext import commands

# These functions check if the user running a command has the given
# role associated (is_mod checks if the user has 'mod' role)
def is_mod(ctx):
    mod_role = discord.utils.get(ctx.guild.roles, name="mod")
    return mod_role in ctx.author.roles
def is_mger(ctx):
    mger_role = discord.utils.get(ctx.guild.roles, name="mger")
    return mger_role in ctx.author.roles
def is_cup_3(ctx):
    mger_role = discord.utils.get(ctx.guild.roles, name="mger")
    return mger_role in ctx.author.roles

# This function saves the inputs from !add when teams sign up
# to a .txt file
def save_mentions(mentions, team_name):
    mention_names = ' '.join(str(mention.name) for mention in mentions)
    team_line = f"{team_name}: {' ' * (space_add - len(team_name))}{mention_names}"  # Adjusted for alignment
    with open("signups.txt", "a") as file:
        file.write(team_line + '\n')
    print("Data saved to file:", team_line)

# This function removes a role from a user 
def remove_role_from_user(user, role_name):
    # Check if the user has the role
    if discord.utils.get(user.roles, name=role_name):
        try:
            # Attempt to remove the role
            user.remove_roles(discord.utils.get(user.guild.roles, name=role_name))
            print(f"Role '{role_name}' removed from {user.display_name}")
        except Exception as e:
            print(f"An error occurred while removing role '{role_name}' from {user.display_name}: {e}")
    else:
        print(f"{user.display_name} does not have the role '{role_name}'")

# Global variables
double_elim = True
category_name = "MATCHES"
bracket_usernames = []
seed_members_life = []
winner_seeds = []
out = []
matchup_lower = []
matchup_upper = []
leftovers = []
round_num = 1
space_add = 25 # num spaces between team name and participants in signups.txt
role = 'Cup 3'

def setup(client):

    # Error handling for cooldown
    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.author.send(f"That command is on cooldown. Try again in a bit.")

    client.remove_command('help')  # Remove the default help command

    # commands.cooldown(# command uses, # seconds cooldown, user type)
    @commands.cooldown(3, 60, commands.BucketType.user)
    @client.command()
    @commands.check(is_mger)
    async def help(ctx):
        embed = discord.Embed(title="Bot Commands", description="List of available commands:", color=0x0000ff)
        embed.add_field(name="!add @user @user 'Team name", value="Sign up for the cup", inline=True)
        embed.add_field(name="!remove", value="Remove your team from the cup", inline=False)
        embed.add_field(name="!servers", value="Display servers for the cup", inline=False)
        embed.add_field(name="!whitelist", value="Display whitelist for the cup", inline=False)
        embed.add_field(name="!maps", value="Display maps for the cup", inline=False)
        # embed.add_field(name="!sponsors", value="", inline=False)
        # Add more fields as needed for other commands
        
        await ctx.send(embed=embed)

    # Display maps
    @commands.cooldown(2, 30, commands.BucketType.user)
    @client.command()
    @commands.check(is_mger)
    async def maps(ctx):
        await ctx.send("Logjam mid\nProcess 2nd\nReconner mid\nMetalworks mid\nGranary last\nProcess mid\nProduct mid\nBadlands mid")

    # Display whitelist
    @commands.cooldown(2, 30, commands.BucketType.user)
    @client.command()
    @commands.check(is_mger)
    async def whitelist(ctx):
        await ctx.send("https://whitelist.tf/14451")

    # Display servers (constantly updating)
    @commands.cooldown(3, 30, commands.BucketType.user)
    @client.command()
    @commands.check(is_cup_3)
    async def servers(ctx):
        await ctx.send("Chi1: connect 169.254.43.55:57128; password 'sfgdsA2ioYIga5'\nChi2: connect 169.254.94.78:12904; password 'A2ioyga21DYIga5'\nChi3: connect 169.254.94.189:38384; password 'ffaA2ioYIga5'\nChi4: connect 169.254.117.163:14496; password 'A2ioyga21DYIga5'\nDal1: connect 169.254.14.31:42936; password 'fauihfgaret'\nDal2: connect 169.254.119.128:62624; password 'eawoityuaa1231a'")

    # Signup for the cup. Entries are saved in signups.txt
    # ex: !add @user1 @user2 'teamname'
    @client.command()
    @commands.check(is_mger)
    async def add(ctx, *args):
        try:
            # Check if the command is invoked in the #team-registration channel
            if ctx.channel.name != 'team-registration':
               raise commands.BadArgument("You can only use this command in the #team-registration channel.")
                    # Check if both mentioned members have the 'mger' role

            # Check if both mentioned members have the 'mger' role
            mger_role = discord.utils.get(ctx.guild.roles, name="mger")
            if mger_role is None:
                raise commands.BadArgument("Role 'mger' not found.")
        
            if len(args) < 3:
                raise commands.BadArgument("Please provide two mentions and a team name.\nExample: !add @user @user Team Name")
            
            # Extract mentions and join the remaining arguments into a single string as the team name
            mentions = args[:2]
            team_name = ' '.join(args[2:])
            
            # Check if the team name is not over 20 characters long
            if len(team_name) > 25:
                raise commands.BadArgument("Team name must be 25 characters or less.")
            
            # Check if each mention is a valid member
            members = []
            for mention in mentions:
                member = discord.utils.get(ctx.guild.members, mention=mention)
                if member is None:
                    raise commands.MemberNotFound(mention)
                if mger_role not in member.roles:
                    raise commands.BadArgument(f"{member.display_name} needs to be verified and have 'mger' role.")
                members.append(member)
            
            # Check if the person running the command is one of the mentioned members
            if ctx.author not in members:
                raise commands.BadArgument("You must be one of the mentioned members.")
            
            # Check if ctx.author.name already exists in signups.txt
            with open('signups.txt', 'r') as file:
                if ctx.author.name in file.read():
                    raise commands.BadArgument("You are already signed up")
            
            # Save mentions and team name to file
            save_mentions(members, team_name)
            # await ctx.author.send("Sign-up successful!")

            # Assign 'Cup 3' role to successfully signed up users
            role_assign = discord.utils.get(ctx.guild.roles, name=role)
            for member in members:
                await member.send(f"You have been signed up by {ctx.author.display_name} to the team '{team_name}' for the 2v2 MGE cup.\nPlease pay the entry fee of 1 weapon PER PLAYER (of either vintage/genuine/strange quality) before the cup begins to Neptune and include your discord name.\nOne player may pay for both members if they want to. \nType !remove to remove your team from registration and contact Neptune if you payed and want your weapon back.\nNEPTUNE TRADE URL: https://steamcommunity.com/tradeoffer/new/?partner=122391808&token=3lTK-D1n")
                await member.add_roles(role_assign)
            
        except commands.CheckFailure:
            command_used = ctx.message.content
            await ctx.author.send(f"You can only use this command in the #team-registration channel.\n")
        except commands.MemberNotFound as e:
            error_msg = f"Member not found: {e.argument}"
            await ctx.author.send(error_msg)  # Send a personal message to the command invoker
            await ctx.message.delete()  # Delete the incorrect signup message
        except commands.BadArgument as e:
            command_used = ctx.message.content
            await ctx.author.send(f"{str(e)}\n")
            await ctx.message.delete()  # Delete the incorrect signup message

    # Remove team from signups. Either member can use this command
    @client.command()
    @commands.check(is_mger)
    async def remove(ctx):
        try:
            # Check if the command is invoked in the #team-registration channel
            if ctx.channel.name != 'team-registration':
               raise commands.BadArgument("You can only use this command in the #team-registration channel.")
            
            # Open the text file
            with open('signups.txt', 'r+') as file:
                lines = file.readlines()
                file.seek(0)
                
                participants_removed = False  # Flag to indicate if participants have been removed
                
                # Iterate through each line in the file
                for line in lines:
                    # Check if the user invoking the command is mentioned in the line
                    if str(ctx.author.name) in line:
                        participants_removed = True
                        # Split the line by colon
                        names = line.split(':')
                        # Extract the second part and remove extra whitespace
                        second_part = names[1].strip()
                        # Split the second part by whitespace to get both names
                        second_names = second_part.split()
                        # Print both names
                        for participant in second_names:
                            member = discord.utils.get(ctx.guild.members, name=participant)
                            if member:
                                role_assign = discord.utils.get(ctx.guild.roles, name=role)
                                await member.send(f"Your team in the 2v2 MGE cup has been removed up by {ctx.author.display_name}")
                                await member.remove_roles(role_assign)
                            else:
                                print(f"Member '{participant}' not found or roles already removed.")

                    else:
                        file.write(line)
                
                # If participants were removed, send a confirmation message
                if participants_removed:
                    await ctx.send("Your team has been removed")
                    
                # Truncate the file after writing the updated lines
                file.truncate()
        except commands.BadArgument as e:
            await ctx.send(str(e))

    # Display teams in signups.txt
    @commands.cooldown(2, 180, commands.BucketType.user)
    @client.command()
    @commands.check(is_mger)
    async def teams(ctx):
        try:
            filename = 'signups.txt'
            with open(filename, "r") as file:
                teams_data = file.readlines()
                if not teams_data:
                    await ctx.send("No teams found.")
                    return
                
                teams_message = ""
                for team_line in teams_data:
                    # Split the team line by colon to separate team name and members
                    team_info = team_line.strip().split(':')
                    team_name = team_info[0].strip()
                    member_names = team_info[1].strip().split()  # Split member names directly

                    # Create formatted line with team name and member names or nicknames
                    formatted_line = f"{team_name}: "
                    for member_name in member_names:
                        # Attempt to convert each member name to a member object
                        member = ctx.guild.get_member_named(member_name)
                        if member:
                            formatted_line += member.display_name + " "  # Use nickname if available
                        else:
                            formatted_line += member_name + " "  # Use username if member not found
                    teams_message += formatted_line.strip() + '\n'

                await ctx.send(teams_message)
        except FileNotFoundError:
            await ctx.send("File 'signups.txt' not found.")
        except Exception as e:
            await ctx.send("An error occurred while processing the command.")
            print("Error:", e)

    # For testing
    @client.command()
    @commands.check(is_mod)
    async def check_user(ctx):
        user_id = ctx.author.id
        username = ctx.author.name  # You can also use ctx.author.display_name to get the nickname if available
        await ctx.send(f"Your Discord ID: {user_id}, Your Username: {username}")

    # Display sponsors
    @commands.cooldown(2, 600, commands.BucketType.user)
    @client.command()
    @commands.check(is_mod)
    async def sponsors(ctx):
        await ctx.send("Mannco with 60 keys\nJebus with 50 keys\nOther donor with 60 keys")
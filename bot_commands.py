import discord
import re
import webscrape
import math
from discord.ext import commands

import perms

# This calculates how many total rounds will be in the bracket
# given the total number of participants
def calculate_rounds(num_participants):
    rounds = math.ceil(math.log2(num_participants))
    return rounds

# Determine the group for each seed
def get_seed_group(seed, group_range):
    max_seed = 32
    if(seed > max_seed):
        seed = seed - 32
    group = 1
    current_range = group_range
    
    while current_range < max_seed:
        if seed <= current_range:
            return group
        group += 1
        current_range += group_range
    return group  # Return the final group if the seed is within the last range

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

# This function subtracts a life from the teams that did not win their
# matchup. Only used for double elim and in the process of
# generating the next round of matchups
def subtract_life(seeds, loser_seeds):
    for team in loser_seeds:  # Iterate through loser_seeds one by one
        team_names = team[1]
        for j, (seed_num, names, life) in enumerate(seeds):
            if all(name in team_names for name in names):
                if life > 0:  # Check if life is greater than 0
                    seeds[j] = (seed_num, names, life - 1)
    return seeds


# Command to add a life back to a team
def override_add_life(seeds, name):
    for i, (seed_num, names, life) in enumerate(seeds):
        if name in names:
            seeds[i] = (seed_num, names, life + 1)
            break  # Exit the loop after updating the first occurrence of the team
    return seeds

# Command to remove a life from a team
def override_sub_life(seeds, name):
    for i, (seed_num, names, life) in enumerate(seeds):
        if name in names:
            seeds[i] = (seed_num, names, life - 1)
            break  # Exit the loop after updating the first occurrence of the team
    return seeds

# Split 'seed_members_life' which is ([seed][members][num lives]) and returns
# the seeds of 2 life teams, team members in 2 life teams, seeds of 1 life teams
# and team members of 1 life teams. Used for double elim
def categorize_teams(seed_members_life, double_elim):
    if(double_elim):
        two_life_teams = [(t[0], t[1], t[2]) for t in seed_members_life if t[2] == 2]
        one_life_teams = [(t[0], t[1], t[2]) for t in seed_members_life if t[2] == 1]
        two_life_seeds = [t[0] for t in two_life_teams]
        one_life_seeds = [t[0] for t in one_life_teams]
        return two_life_teams, one_life_teams, two_life_seeds, one_life_seeds
    else:
        single_elim_teams = [(t[0], t[1], t[2]) for t in seed_members_life if t[2] == 1]
        single_elim_seeds = [t[0] for t in single_elim_teams]
        return single_elim_teams, single_elim_seeds

# This re seeds teams based on true seeding (if a 15 seed beats a 2 seed)
# then they now have the 'path' of the 2 seed
def arrange_seeds(seeding, teams, num_participants):
    num_teams_upper = len(teams)
    og_seeds_two = seeding.copy()
    # Update each seed value based on the number of teams in the upper bracket
    for i, seed in enumerate(seeding):
        remaining_teams = num_participants
        while seed > num_teams_upper:
            if seed <= (remaining_teams // 2):
                seed = int((remaining_teams // 2) - seed + 1)
                remaining_teams //= 2
            else:
                seed = remaining_teams - seed + 1
                remaining_teams //= 2
            if seed <= num_teams_upper:
                break
        seeding[i] = seed

    # Sort the modified seed list and obtain the indices of the sorted elements
    sorted_indices = sorted(range(len(seeding)), key=lambda x: seeding[x])
    seeding.sort()

    # Reorder the original seeds list using the sorted indices
    og_seeds_two = [og_seeds_two[i] for i in sorted_indices]
    # Create a dictionary to map original seeds to modified seeds
    mapping_upper = dict(zip(og_seeds_two, seeding))
    # Rearrange the teams based on the mapping of seeds
    teams.sort(key=lambda x: mapping_upper[x[0]])
    # Extract seeds and members for upper bracket channel creation
    upper_seeds = []
    matchup_upper = []
    for i in range(len(teams) // 2):
        seed1 = og_seeds_two[i]  # Get seed1
        seed2 = og_seeds_two[len(og_seeds_two) - i - 1]  # Get seed2
        members1 = teams[i][1]
        members2 = teams[len(teams) - i - 1][1]
        upper_seeds.append((seed1, seed2))
        matchup_upper.append((i+1, members1))
        matchup_upper.append((i+1, members2))
    return seeding, teams, upper_seeds, matchup_upper

# This calculates the lower bracket matchups. 
# Lower bracket does NOT just go low seed vs high seed, based on which
# round you are in the bracket there are set matches for which matchup plays
# which matchup. 
# *** THIS IS SET FOR 64 TEAMS and needs to be adjusted a little for different sizes ***
def lower_bracket_next_round(matchup_lower, matchup_upper, winner_seeds, num_splits, leftovers=None, leftover_leftovers=None):
    loser_names = []
    # x = (2**((num_rounds-num_splits+1)//2)) * 2

    # Iterate through each entry in matchup_upper
    for seed, names in matchup_upper:
        # Check if the names are not present in winner_seeds
        if names not in [entry[1] for entry in winner_seeds]:
            loser_names.append((seed, names))

    winner_names = []
    # Iterate through each entry in matchup_lower
    # print(matchup_lower)
    for seed, names in matchup_lower:
        # Check if the names are also present in winner_seeds
        if names in [entry[1] for entry in winner_seeds]: 
            winner_names.append((seed, names))

    matchup = []

    print("test winner_names: ", winner_names)
    print("test matchup_lower: ", matchup_lower)
    print("test num_splits: ", num_splits)
    print("test leftovers: ", leftovers)
    print("test leftover_leftovers: ", leftover_leftovers)

    if winner_names:
        if num_splits == 2:
            print("num_splits == 2")
            for i in range(8):
                members = [
                    (2*i + 1, loser_names[2*i][1]),      # Matchup 1: Loser1 vs Winner2
                    (2*i + 1, winner_names[2*i + 1][1]), # Matchup 2: Loser1 vs Winner2
                    (2*i + 2, loser_names[2*i + 1][1]),  # Matchup 3: Loser2 vs Winner1
                    (2*i + 2, winner_names[2*i][1])      # Matchup 4: Loser2 vs Winner1
                ]
                matchup.extend(members)
        elif num_splits == 3:
            print("num_splits == 3")
            for i in range(8):
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, winner_names[16-i-1][1]),
                ]
                matchup.extend(members)
        elif num_splits == 4:
            print("num_splits == 4")
            for i in range(8):
                second_index = (i + 2) % 8  # Ensures wrapping around the list
                
                if i == 2 or i == 3 or i == 6 or i == 7:
                    second_index = (i - 2 + 8) % 8  # Ensures wrapping around the list
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, leftovers[second_index][1])
                ]
                matchup.extend(members)
        elif num_splits == 5:
            print("num_splits == 5")
            for i in range(4):
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, winner_names[8-i-1][1]),
                ]
                matchup.extend(members)
            leftover_leftovers = leftovers

        elif num_splits == 6:
            print("num_splits == 6")
            for i in range(4):
                second_index = (i + 1) % 4
                if i == 1 or i == 3:
                    second_index = (i - 1 + 4) % 4
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, leftover_leftovers[4-i - 1][1])
                ]
                matchup.extend(members)
            leftover_leftovers = leftovers

        elif num_splits == 7:
            print("num_splits == 7")
            for i in range(2):
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, winner_names[4-i - 1][1]),
                ]
                matchup.extend(members)
        elif num_splits == 8:
            print("num_splits == 8")
            for i in range(2):
                second_index = 1
                if i == 1:
                    second_index = 0
                print("Second index: ", second_index)
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, leftover_leftovers[second_index][1])
                ]
                matchup.extend(members)
            leftover_leftovers = leftovers
        elif num_splits == 9:
            print("num_splits == 9")
            for i in range(1):
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, winner_names[i+1][1])
                ]
                matchup.extend(members)
        elif num_splits == 10:
            print("num_splits == 10")
            for i in range(1):
                members = [
                    (i + 1, winner_names[i][1]),
                    (i + 1, leftover_leftovers[i][1])
                ]
                matchup.extend(members)
        else:
            print("ROUNDNUM OUT OF BOUNDS")
    else:
        print("No winner found yet.")

    if(num_splits == 7 or num_splits == 9):
        print("lol")
    else: 
        leftovers = loser_names

    return matchup, leftovers, leftover_leftovers

# Global variables
double_elim = True
bracket_usernames = []
category_name_upper = 'round_1'
category_name_lower = 'round_1'
grand_final_names = ""
seed_members_life = []
winner_seeds = []
out = []
matchup_lower = []
matchup_upper = []
leftovers = []
leftover_leftovers = []
round_num = 1
space_add = 25 # num spaces between team name and participants in signups.txt
role = 'Cup 3'

def setup(client):

    # Cooldown error
    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.author.send(f"That command is on cooldown. Try again in a bit.")

    # Adds the users team to the winner teams
    @client.command()
    @commands.check(is_cup_3)
    async def win(ctx):
        global winner_seeds
        global seed_members_life

        # Check if the message author is part of any seed
        for seed_info in seed_members_life:
            seed = seed_info[0]  # Extract seed number
            members = seed_info[1]  # Extract members from seed information
            if ctx.author.name in members:
                # Check if the seed is already in winner_seeds
                if seed not in [item[0] for item in winner_seeds]:
                    # Add the seed and its corresponding information to winner_seeds
                    winner_seeds.append(seed_info)
                    await ctx.send(f"Seed {seed} and its members have been added to the winner bracket.")
                    # print(winner_seeds)  # Print the winner seeds
                else:
                    await ctx.send(f"Seed {seed} is already in the winner bracket.")
                return  # Stop checking for other seeds if the member is found in one seed
        await ctx.send("You are not part of any seed.")

    # 'ow' stands for override_win. I was using it so much I truncated it
    #  This lets a mod add another team to the winner seeds
    @client.command()
    @commands.check(perms.is_helper)
    async def ow(ctx, *, args):
        global winner_seeds
        global seed_members_life

        seed_numbers = []

        # Get seeds 
        try:
            # Split the argument by comma and strip any whitespace
            seed_numbers = [int(seed.strip()) for seed in args.split(',')]
        except ValueError:
            await ctx.send(f"Invalid input. Please provide valid seed numbers separated by commas.")
            return

        added_seeds = []
        already_in_bracket = []

        # Add each seed number
        for seed in seed_numbers:
            seed_info = next((s for s in seed_members_life if s[0] == seed), None)
            if seed_info:
                if seed not in [item[0] for item in winner_seeds]:
                    winner_seeds.append(seed_info)
                    added_seeds.append(seed)
                else:
                    already_in_bracket.append(seed)
            else:
                await ctx.send(f"Seed {seed} not found.")
        
        # Add multiple seeds
        if added_seeds:
            await ctx.send(f"Seeds {', '.join(map(str, added_seeds))} and their members have been added to the winner bracket.")
        if already_in_bracket:
            await ctx.send(f"Seeds {', '.join(map(str, already_in_bracket))} are already in the winner bracket.")

    # This removes the user's team from the winner teams
    @client.command()
    @commands.check(is_cup_3)
    async def lose(ctx):
        global winner_seeds
        
        # Check if the user is part of any seed in winner_seeds
        for seed_info in winner_seeds:
            members = seed_info[1]  # Extract members from seed information
            if ctx.author.name in members:
                seed = seed_info[0]  # Extract seed number
                # Remove the seed from winner_seeds
                winner_seeds.remove(seed_info)
                await ctx.send(f"Removed Seed {seed} and its members from the winner bracket.")
                return
        
        await ctx.send("You are not part of any seed in the winner bracket.")

    # This lets a mod remove a team from the winner teams
    @client.command()
    @commands.check(perms.is_helper)
    async def override_lose(ctx, member: discord.Member):
        global winner_seeds

        # Check if the member provided belongs to any seed
        for seed_info in winner_seeds:
            members = seed_info[1]  # Extract members from seed information
            if member.name in members:
                seed = seed_info[0]  # Extract seed number
                # Remove the seed from winner_seeds
                winner_seeds.remove(seed_info)
                await ctx.send(f"Removed Seed {seed} and its members from the winner bracket.")
                return
        await ctx.send("The provided member is not part of any seed in the winner bracket.")

    # Displays the teams that have won their matchup and waiting for next round
    @client.command()
    @commands.check(is_cup_3)
    async def display_winners(ctx):
        global winner_seeds
        
        if not winner_seeds:
            await ctx.send("No winner seeds available.")
            return
        
        # Formatting winner seeds for display
        message = "Winner Seeds:\n"
        for seed_info in winner_seeds:
            seed = seed_info[0]  # seed number
            members = seed_info[1]  # members
            life = seed_info[2]  # life value
            message += f"Seed {seed}: {' '.join([member.mention if isinstance(member, discord.Member) else str(member) for member in members])} ({life} lifes)\n"
        
        await ctx.send(message)

    # Runs 'process_bracket' which webscrapes a bracket url
    @client.command()    
    @commands.check(perms.is_mod)
    async def create_bracket(ctx):
        global seed_members_life 
        seed_members_life = await _process_bracket(ctx, send_message=False)
        await ctx.send("Bracket created. Enter !bracket to display the bracket")
    async def _process_bracket(ctx, send_message=False):
        global bracket_usernames 
        global life

        life = 2 if double_elim else 1

        div_tags_with_class = webscrape.scrape_bracket(client)

        message = ""
        seed_members_life = []

        for i, tag in enumerate(div_tags_with_class, start=1):
            input_tag = tag.find("input")  # <input> tag within the <div> tag
            name = i  # Set the name as "Seed #" where # is the index
            value = input_tag["value"]  # Get the value of the "value"
            
            # Split names based on "/"
            usernames = value.split("/")
            seed_members = []
            
            # Try to convert each username to a member object and get their ID
            for username in usernames:
                try:
                    member = await commands.MemberConverter().convert(ctx, username)
                    seed_members.append(member.name)
                    bracket_usernames.append(member.name)  # Add the username to the global list
                except commands.errors.MemberNotFound:
                    await ctx.send(f"User '{username}' not found in the Discord server.")
                    seed_members.append(username)  # If user not found, send username as is

            seed_members_life.append((name, seed_members, life))  # Store seed name, members, and their life

            message += f"{name}: {' '.join([f'{member.mention if isinstance(member, discord.Member) else member}' for member in seed_members])} ({life} lifes)\n"

        # If !bracket is ran, display bracket
        if send_message:
            await ctx.send(message)

        return seed_members_life

    # Displays current bracket seeds/members/lifes
    @client.command()
    @commands.check(perms.is_mod)
    async def bracket(ctx):
        await _display_bracket(ctx)
    async def _display_bracket(ctx):
        global seed_members_life
        if seed_members_life:
            message = ""
            for name, seed_members, life in seed_members_life:
                message += f"{name}: {' '.join([f'{member.mention if isinstance(member, discord.Member) else member}' for member in seed_members])} ({life} lifes)\n"
            await ctx.send(message)
        else:
            await ctx.send("Bracket not created yet. Use !create_bracket first.")

    # Starts the 'tourney' and creates private channels for each round1 matchup
    @client.command()
    @commands.check(perms.is_mod)
    async def start_bracket(ctx):
        global round_num
        global winner_seeds
        global category_name_upper
        global seed_members_life

        category_name_upper = "upper_round_1"

        guild = ctx.guild
        num_seeds = len(seed_members_life)

        # Retrieve the category name
        category = discord.utils.get(guild.categories, name=category_name_upper)
        
        if not category:
            await ctx.send(f"Category '{category_name_upper}' not found.")
            return
        # Iterate over pairs of seeds
        for i in range(num_seeds // 2):
            # Get the seeds and members for the current pair
            seed1, members1, seed2, members2 = seed_members_life[i][0], seed_members_life[i][1], seed_members_life[num_seeds - i - 1][0], seed_members_life[num_seeds - i - 1][1]
            # significant_players_present = any(member_name in ['logannn1', 'botmode', '_jw'] for member_name in members1 + members2)
            
            # Format the channel names
            channel_name = f"Seed{seed1}_vs_Seed{seed2}"
            
            # Create the channel under the specified category
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Deny access to @everyone
                guild.me: discord.PermissionOverwrite(read_messages=True),  # Allow the bot to read messages
            }

            # == perms to view channel ==
            for member_name in members1 + members2:
                member = discord.utils.get(guild.members, name=member_name)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)

            producer = discord.utils.get(guild.roles, name="producer")
            if producer:
                overwrites[producer] = discord.PermissionOverwrite(read_messages=True)

            helper = discord.utils.get(guild.roles, name="helper")
            if helper:
                overwrites[helper] = discord.PermissionOverwrite(read_messages=True)
            # ===========================

            team1_mentions = []
            team2_mentions = []

            # Group every 8 seeds to distribute servers
            group_range = 8
            group1 = get_seed_group(seed1, group_range)
            group2 = get_seed_group(seed2, group_range)

            for member_name in members1:
                member = discord.utils.get(guild.members, name=member_name)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)  # Allow access to each member
                    team1_mentions.append(f"<@{member.id}>")
            for member_name in members2:
                member = discord.utils.get(guild.members, name=member_name)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)  # Allow access to each member
                    team2_mentions.append(f"<@{member.id}>")

            new_channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
            await new_channel.send(
                f"MAGGOTS, FIGHT!\n\n"
                f"- Seed {seed2} {' '.join(team2_mentions)} ban 4 maps.\n"
                f"- Seed {seed1} {' '.join(team1_mentions)} chooses map.\n"
                f"- Best of 1 game. Paste the score in chat.\n\n"

                f"Type !maps for the map pool.\n"
                f"Everyone must record a demo. See <#{1260749245200339026}>.\n"
                f"Review <#{1172645045887848589}> and <#{1260755247811399760}> before asking questions.\n\n"
                
                ":scroll: If you win type !win. If there is a mistake type !lose. :scroll:\n"
                ":rotating_light: If you troll and type !win when you didn't, you may receive a ban from all things mge.tf :rotating_light:\n\n"
                
                f"Servers: See <#{1262433210302992506}>\n\n"
                
                + ("- **Dal1:** `connect dal.serveme.tf:27015; password 'iuuhtiu4gwq'`\n"
                "- **Chi1:** `connect chi3.serveme.tf:27115; password 'a95kabta3AG'`\n"
                "- **KS1:** `connect ks2.serveme.tf:27015; password 'werenotinkansasanymore'`"
                if group1 == 1 else
                "- **Dal2:** `connect dal.serveme.tf:27025; password 'nbaha168ax'`\n"
                "- **Chi2:** `connect chi3.serveme.tf:27125; password 'q346reakgj'`\n"
                "- **KS1:** `connect ks2.serveme.tf:27015; password 'werenotinkansasanymore'`"
                if group1 == 2 else
                "- **Dal3:** `connect dal.serveme.tf:27035; password 'nmma811aha112'`\n"
                "- **Chi3:** `connect chi3.serveme.tf:27135; password '9jaoighoioh32'`\n"
                "- **KS2:** `connect ks2.serveme.tf:27025; password 'were49notinkansasanymore2'`"
                if group1 == 3 else
                "- **Dal4:** `connect dal.serveme.tf:27045; password 'blobahjhahe661'`\n"
                "- **Chi4:** `connect chi3.serveme.tf:27145; password 'kjhabba1251'`\n"
                "- **KS2:** `connect ks2.serveme.tf:27025; password 'were49notinkansasanymore2'`"
                if group1 == 4 else
                ""
                ) + "\n\n"
                
                "Type !EU to display EU servers! NA teams always have server priority."
            )
        # Reset winner seeds
        round_num = 1
        winner_seeds = []

    # After each round is complete, this command will start the next round and 
    # create private channels for the next round matchup
    @client.command()
    @commands.check(perms.is_mod)
    async def next_round(ctx):
        global winner_seeds
        global seed_members_life
        global matchup_lower
        global matchup_upper
        global leftovers
        global leftover_leftovers
        global round_num
        global category_name_lower
        global category_name_upper
        global grand_final_names
        
        category_name_lower = f"lower_round_{round_num}"
        if(round_num < 6):
            category_name_upper = f"upper_round_{round_num + 1}"
        elif(round_num == 10):
            category_name_lower = "OPEN_Grand_Finals"
        else:
            category_name_upper = "OPEN_Grand_Finals"

        guild = ctx.guild
    
        category_name_lower = discord.utils.get(guild.categories, name=category_name_lower)
        category_name_upper = discord.utils.get(guild.categories, name=category_name_upper)
        if not category_name_upper or not category_name_lower:
            await ctx.send(f"Category '{category_name_lower}' or '{category_name_upper}' not found.")
            return
        if not winner_seeds:
            await ctx.send("No winners from the previous round to create channels for.")
            return
        
        # Calculate loser seeds by taking the teams that did not win their matchup. When
        # a team types !win they are put into 'winner_seeds'
        # Extracting the names from winner_seeds and leftovers for comparison
        round_num += 1
        print(" === ROUND_NUM ===", round_num)
        print(.01)
        winner_names_only = [names for _, names, _ in winner_seeds]
        print(.02)
        leftover_names_only = [names for _, names in leftovers]
        print(.03)
        leftover_leftovers_names_only = [names for _, names in leftover_leftovers]
        print(.04)
        # 'leftover_names' are teams with a lower_round_bye
        if round_num == 5 or round_num == 6:
            loser_seeds = [member for member in seed_members_life
                            if member[1] not in winner_names_only and member[1] not in leftover_names_only]
            print(.05)

        # 'leftover_leftover_names' are teams with TWO lower_round_byes
        # 'leftover_leftover_names' then become 'leftover_names'
        elif round_num == 7:
            loser_seeds = [member for member in seed_members_life
                        if member[1] not in winner_names_only and member[1] not in leftover_names_only and member[1] not in leftover_leftovers_names_only and member not in grand_final_names]
            print(.06)
        elif round_num == 8 or round_num == 9 or round_num == 10:
            loser_seeds = [member for member in seed_members_life
                        if member[1] not in winner_names_only and member[1] not in leftover_names_only and member[1] not in leftover_leftovers_names_only and member not in grand_final_names]
            print(.07)
        else:
            loser_seeds = [name for name in seed_members_life if name not in winner_seeds]
            print(.08)

        # print("=== LEFTOVER NAMES === ", leftover_names_only)
        # print("=== WINNER SEEDS === ", winner_seeds)
        # print("=== LOSER SEEDS === ", loser_seeds)
        print(.09)
        subtract_life(seed_members_life, loser_seeds)
        print(.10)

        num_participants = len(seed_members_life)
        num_rounds = calculate_rounds(num_participants) + 1
        print(.11)
        if(double_elim):
            # Split up 'seed_members_life' which stores seeds/members/lifes of each team into 
            # seeds/members for 2 life teams and 1 life teams
            print(.12)
            two_life_teams, one_life_teams, two_life_seeds, one_life_seeds = categorize_teams(seed_members_life, double_elim)
            print(.13)
            print(two_life_teams)
            num_teams_upper = len(two_life_teams)
            print(num_teams_upper)
            print(.14)
            grand_final_names = [names for _, names, _ in two_life_teams]
            # grand_final_names = [name for sublist in temp_names for name in sublist]
            print("GF NAMES ", grand_final_names)
            # If it's the first round, arrange seeds lowest to highest for upper bracket
            # Otherwise do specialized seeding based on which round. See 'lower_bracket_next_round'
            num_splits = round_num - 1
            print("===NUM SPLITS=== ", num_splits)
            print(.15)
            if(num_splits == 1):
                print(.16)
                one_life_seeds, one_life_teams, lower_seeds, matchup_lower = arrange_seeds(one_life_seeds, one_life_teams, num_participants)        
            else:
                print(.17)
                matchup_lower, leftovers, leftover_leftovers = lower_bracket_next_round(matchup_lower, matchup_upper, winner_seeds, num_splits, leftovers, leftover_leftovers)
            # Re-arrange lower bracket based on true seeding. This only needs to be done for the first round of lower bracke
            print(.18)
            two_life_seeds, two_life_teams, upper_seeds, matchup_upper = arrange_seeds(two_life_seeds, two_life_teams, num_participants)
            # print("=== Two_life_seeds ===", two_life_seeds)
            # print(" === UPPER SEEDS ===", upper_seeds)
            # print(" === MATCHUP UPPER ===", matchup_upper)
            await create_channels(ctx, guild, category_name_upper, upper_seeds, matchup_upper, round_num, 1)
            # Create channels for each matchup
            if(num_splits == 0):
                await create_channels(ctx, guild, category_name_lower, lower_seeds, matchup_lower, round_num, 0)
            else:
                await create_lower_channels(ctx, guild, category_name_lower, seed_members_life, matchup_lower, round_num)
        # If single ELIM
        else:
            # Split up 'seed_members_life' which stores seeds/members/lifes of each team into seeds and teams 
            single_elim_teams, single_elim_seeds = categorize_teams(seed_members_life, double_elim)

            # Re-arrange lower bracket based on true seeding. This only needs to be done for the first round of lower bracke
            single_elim_seeds, single_elim_teams, seeds, matchup = arrange_seeds(single_elim_seeds, single_elim_teams, num_participants)

            # Create channels for each matchup
            await create_channels(ctx, guild, category_name_upper, seeds, matchup, round_num, 1)

        winner_seeds = []  # Reset winner_seeds for the next round
        print(.19)
        await ctx.send("Done")

    async def create_channels(ctx, guild, category, seeding, matchups, round_num, if_upper): 
        for i in range(len(seeding)):
            seed1, seed2 = seeding[i]
            team1, team2 = matchups[2*i][1], matchups[2*i+1][1]
            significant_players_present = any(member_name in ['userjebus', 'cormiez'] for member_name in team1 + team2)
            if if_upper:
                channel_name = f"Seed{seed1}_vs_Seed{seed2}"

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
            }

            producer = discord.utils.get(guild.roles, name="producer")
            if producer:
                overwrites[producer] = discord.PermissionOverwrite(read_messages=True)  # Allow access to the certain_role

            helper = discord.utils.get(guild.roles, name="helper")
            if helper:
                overwrites[helper] = discord.PermissionOverwrite(read_messages=True)  # Allow access to the helper role

            team1_mentions = []
            team2_mentions = []

            group_range = 8
            group1 = get_seed_group(seed1, group_range)
            group2 = get_seed_group(seed2, group_range)

            for member_name in team1:
                member = discord.utils.get(guild.members, name=member_name)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)  # Allow access to each member
                    team1_mentions.append(f"<@{member.id}>")

            for member_name in team2:
                member = discord.utils.get(guild.members, name=member_name)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)  # Allow access to each member
                    team2_mentions.append(f"<@{member.id}>")

            new_channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
            await new_channel.send(
                f"MAGGOTS, FIGHT!\n\n"
                f"- Seed {seed2} {' '.join(team2_mentions)} ban 4 maps.\n"
                f"- Seed {seed1} {' '.join(team1_mentions)} chooses map.\n"
                f"- Best of 1 game. Paste the score in chat.\n\n"

                f"Type !maps for the map pool.\n"
                f"Everyone must record a demo. See <#{1260749245200339026}>.\n"
                f"Review <#{1172645045887848589}> and <#{1260755247811399760}> before asking questions.\n\n"
                
                ":scroll: If you win type !win. If there is a mistake type !lose. :scroll:\n\n"
                
                f"Servers: See <#{1262433210302992506}>\n\n"
                
                + ("- **Dal1:** `connect dal.serveme.tf:27015; password 'iuuhtiu4gwq'`\n"
                "- **Chi1:** `connect chi3.serveme.tf:27115; password 'a95kabta3AG'`\n"
                "- **KS1:** `connect ks2.serveme.tf:27015; password 'werenotinkansasanymore'`"
                if group1 == 1 else
                "- **Dal2:** `connect dal.serveme.tf:27025; password 'nbaha168ax'`\n"
                "- **Chi2:** `connect chi3.serveme.tf:27125; password 'q346reakgj'`\n"
                "- **KS1:** `connect ks2.serveme.tf:27015; password 'werenotinkansasanymore'`"
                if group1 == 2 else
                "- **Dal3:** `connect dal.serveme.tf:27035; password 'nmma811aha112'`\n"
                "- **Chi3:** `connect chi3.serveme.tf:27135; password '9jaoighoioh32'`\n"
                "- **KS2:** `connect ks2.serveme.tf:27025; password 'were49notinkansasanymore2'`"
                if group1 == 3 else
                "- **Dal4:** `connect dal.serveme.tf:27045; password 'blobahjhahe661'`\n"
                "- **Chi4:** `connect chi3.serveme.tf:27145; password 'kjhabba1251'`\n"
                "- **KS2:** `connect ks2.serveme.tf:27025; password 'were49notinkansasanymore2'`"
                if group1 == 4 else
                ""
                ) + "\n\n"
                
                "Type !EU to display EU servers! NA teams always have server priority."
            )            
            # await ctx.send(f"Created channel '{channel_name}' under '{category.name}' category")

            # print("Significant players: ", significant_players_present)
            #if significant_players_present:
             #   await new_channel.send("userjebus or cormi")
            #else:
            #    await new_channel.send("No significant players found.")
    async def create_lower_channels(ctx, guild, category, seeding, matchups, round_num):
        for i in range(len(matchups) // 2):
            team1 = matchups[2*i][1]
            team2 = matchups[2*i+1][1]
  
            # Find the corresponding seeds from seeding
            for seed, players, _ in seeding:
                if players == team1:
                    seed1 = seed
                elif players == team2:
                    seed2 = seed

            channel_name = f"Seed{seed1}_vs_Seed{seed2}"
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
            }

            producer = discord.utils.get(guild.roles, name="producer")
            if producer:
                overwrites[producer] = discord.PermissionOverwrite(read_messages=True)  # Allow access to the certain_role

            helper = discord.utils.get(guild.roles, name="helper")
            if helper:
                overwrites[helper] = discord.PermissionOverwrite(read_messages=True)  # Allow access to the helper role

            team1_mentions = []
            team2_mentions = []

            group_range = 8
            group1 = get_seed_group(seed1, group_range)
            group2 = get_seed_group(seed2, group_range)

            for member_name in team1:
                member = discord.utils.get(guild.members, name=member_name)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)  # Allow access to each member
                    team1_mentions.append(f"<@{member.id}>")

            for member_name in team2:
                member = discord.utils.get(guild.members, name=member_name)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)  # Allow access to each member
                    team2_mentions.append(f"<@{member.id}>")

            new_channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
            await new_channel.send(
                f"MAGGOTS, FIGHT!\n\n"
                f"- Seed {seed2} {' '.join(team2_mentions)} ban 4 maps.\n"
                f"- Seed {seed1} {' '.join(team1_mentions)} chooses map.\n"
                f"- Best of 1 game. Paste the score in chat.\n\n"

                f"Type !maps for the map pool.\n"
                f"Everyone must record a demo. See <#{1260749245200339026}>.\n"
                f"Review <#{1172645045887848589}> and <#{1260755247811399760}> before asking questions.\n\n"

                ":scroll: If you win type !win. If there is a mistake type !lose. :scroll:\n\n"
                
                f"Servers: See <#{1262433210302992506}>\n\n"
                
                + ("- **Dal1:** `connect dal.serveme.tf:27015; password 'iuuhtiu4gwq'`\n"
                "- **Chi1:** `connect chi3.serveme.tf:27115; password 'a95kabta3AG'`\n"
                "- **KS1:** `connect ks2.serveme.tf:27015; password 'werenotinkansasanymore'`"
                if group1 == 1 else
                "- **Dal2:** `connect dal.serveme.tf:27025; password 'nbaha168ax'`\n"
                "- **Chi2:** `connect chi3.serveme.tf:27125; password 'q346reakgj'`\n"
                "- **KS1:** `connect ks2.serveme.tf:27015; password 'werenotinkansasanymore'`"
                if group1 == 2 else
                "- **Dal3:** `connect dal.serveme.tf:27035; password 'nmma811aha112'`\n"
                "- **Chi3:** `connect chi3.serveme.tf:27135; password '9jaoighoioh32'`\n"
                "- **KS2:** `connect ks2.serveme.tf:27025; password 'were49notinkansasanymore2'`"
                if group1 == 3 else
                "- **Dal4:** `connect dal.serveme.tf:27045; password 'blobahjhahe661'`\n"
                "- **Chi4:** `connect chi3.serveme.tf:27145; password 'kjhabba1251'`\n"
                "- **KS2:** `connect ks2.serveme.tf:27025; password 'were49notinkansasanymore2'`"
                if group1 == 4 else
                ""
                ) + "\n\n"
                
                "Type !EU to display EU servers! NA teams always have server priority."
            )            
            # await ctx.send(f"Created channel '{channel_name}' under '{category.name}' category")

    # This lets a mod add a life back to a team
    @client.command()
    @commands.check(perms.is_mod)
    async def override_add_life(ctx, member: discord.Member):
        global seed_members_life
        # Assuming 'seeds' is a list of tuples (seed_num, names, life)
        for i, (seed_num, names, life) in enumerate(seed_members_life):
            if member.name in names:
                seed_members_life[i] = (seed_num, names, life + 1)
                await ctx.send(f"Added Life to {member.display_name}, Seed: {seed_num}")
                break  # Exit the loop after updating the first occurrence of the team

    # This lets a mod take away a life from a team
    @client.command()
    @commands.check(perms.is_mod)
    async def override_sub_life(ctx, member: discord.Member):
        global seed_members_life
        # Assuming 'seeds' is a list of tuples (seed_num, names, life)
        for i, (seed_num, names, life) in enumerate(seed_members_life):
            if member.name in names:
                if life > 0:
                    seed_members_life[i] = (seed_num, names, life - 1)
                    await ctx.send(f"Removed 1 Life from {member.display_name}, Seed: {seed_num}")
                else:
                    await ctx.send(f"{member.display_name} in Seed: {seed_num} has no more lives")
                break  # Exit the loop after updating the first occurrence of the team

    # This removes all channels starting with 'seed' please be careful not to remove 
    # channels when they are in use or that should be archived!!
    @client.command()
    @commands.check(perms.is_mod)
    async def delete(ctx):
        
        # Iterate through all channels in the guild
        for channel in ctx.guild.channels:
            # Check if the channel name starts with 'seed'
            if channel.name.startswith('should_be_seed'):
                # Delete the channel
                await channel.delete()
        
        await ctx.send("All channels starting with 'seed' have been deleted.")

    # Shuts off bot
    @client.command()
    @commands.check(perms.is_mod)
    async def turnoff(ctx):
        await ctx.send("Turning off... Goodbye!")
        await client.close()
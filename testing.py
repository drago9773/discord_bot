# round_num = 5  # Example round number
# seed_members_life = [(1, ['MatchBox', 'MatchBox'], 2), (2, ['Minecord', 'Minecord'], 2), 
#                 (3, ['MoE', 'MoE'], 2), (4, ['Mudae', 'Mudae'], 2), 
#                 (5, ['Musico', 'Musico'], 2), (6, ['Mini Kraken', 'Mini Kraken'], 2), 
#                 (7, ['Neko', 'Neko'], 2), (8, ['neptune8222', 'neptune8222'], 2)]
# winner_seeds = [(5, ['Musico', 'Musico'], 2), (6, ['Mini Kraken', 'Mini Kraken'], 2), 
#                 (7, ['Neko', 'Neko'], 2), (8, ['neptune8222', 'neptune8222'], 2)]
# leftovers = [(1, ['MatchBox', 'MatchBox'])]

# # Extracting the names from winner_seeds and leftovers for comparison
# winner_names_only = [names for _, names, _ in winner_seeds]
# leftover_names_only = [names for _, names in leftovers]

# if round_num == 5 or round_num == 7:
#     loser_seeds = [member for member in seed_members_life 
#                    if member[1] not in winner_names_only and member[1] not in leftover_names_only]
# else:
#     loser_seeds = [name for name in seed_members_life if name not in winner_seeds]

# print(loser_seeds)
leftovers = [(1, ['Frequent.gg', 'Frequent.gg']), (2, ['Feline', 'Feline']), (3, ['drago9773', 'drago9773']), (4, ['Discraft', 'Discraft'])]
winner_names = [(1, ['Blerp', 'Blerp'], 2), (2, ['Chilling', 'Chilling'], 2), (9, ['Green-bot', 'Green-bot'], 1), (10, ['Herocord', 'Herocord'], 1), (11, ['Idle Miner', 'Idle Miner'], 1), (12, ['Karuta', 'Karuta'], 1), (13, ['Kazu', 'Kazu'], 1), (14, ['LevelingBot', 'LevelingBot'], 1), (15, ['Loco Bot', 'Loco Bot'], 1), (16, ['LoFi Man', 'LoFi Man'], 1)]
matchup = []
x=4

for i in range(x):
    second_index = (i + 1) % len(leftovers)
    if i == 1 or i == 3:
        second_index = (i - 1) % len(leftovers)
    
    members = [
        (i + 1, winner_names[i][1]),
        (i + 1, leftovers[second_index][1])
    ]
    matchup.extend(members)

# print(matchup)
two_life_teams = [(1, ['Blerp', 'Blerp'], 2)]
grand_final_names = [names for _, names, _ in two_life_teams]
flat_names = [name for sublist in grand_final_names for name in sublist]
print(flat_names)
def create_lower_channels(seeding, matchups, round_num):
    for i in range(len(matchups) // 2):
        team1 = matchups[2*i][1]
        team2 = matchups[2*i+1][1]
        print(team1, team2)

        for seed, players, _ in seeding:
            if players == team1:
                seed1 = seed
            elif players == team2:
                seed2 = seed

        print(seed1, "vs ", seed2)

loser_seed = [(1, ['neptune8222', 'neptune8222']), (1, ['bwd4961', 'bwd4961']), (2, ['.gachibass', '.gachibass']), (2, ['unc4nny', 'unc4nny']), 
 (3, ['userjebus', 'userjebus']), (3, ['plllloo_91121', 'plllloo_91121']), (4, ['_zebulon_', '_zebulon_']), (4, ['alphacue', 'alphacue']), 
 (5, ['banjo8528', 'banjo8528']), (5, ['beamstrice', 'beamstrice']), (6, ['ta5k', 'ta5k']), (6, ['erpor', 'erpor']), (7, ['slippi.', 'slippi.']), 
 (7, ['obelixetasterix', 'obelixetasterix']), (8, ['shaztastic.', 'shaztastic.']), (8, ['anthony.1118', 'anthony.1118'])]

seed_members_life = [(1, ['neptune8222', 'neptune8222'], 2), (2, ['drago9773', 'drago9773'], 2), (3, ['userjebus', 'userjebus'], 2), (4, ['cormiez', 'cormiez'], 2), 
 (5, ['banjo8528', 'banjo8528'], 2), (6, ['ta5k', 'ta5k'], 2), (7, ['shelz0r', 'shelz0r'], 2), (8, ['shaztastic.', 'shaztastic.'], 2), (9, ['elesage', 'elesage'], 2), 
 (10, ['anthony.1118', 'anthony.1118'], 2), (11, ['beamstrice', 'beamstrice'], 2), (12, ['erpor', 'erpor'], 2), (13, ['_zebulon_', '_zebulon_'], 2), 
 (14, ['alphacue', 'alphacue'], 2), (15, ['bwd4961', 'bwd4961'], 2), (16, ['unc4nny', 'unc4nny'], 2), (17, ['gangleader4246', 'gangleader4246'], 2), 
 (18, ['.gachibass', '.gachibass'], 2), (19, ['loucasheart', 'loucasheart'], 2), (20, ['plllloo_91121', 'plllloo_91121'], 2), (21, ['itzsassym8', 'itzsassym8'], 2), 
 (22, ['skateboard_pete', 'skateboard_pete'], 2), (23, ['slippi.', 'slippi.'], 2), (24, ['obelixetasterix', 'obelixetasterix'], 2), (25, ['team25', 'team25'], 2),
(26, ['team26', 'team26'], 2), (27, ['team27', 'team27'], 2), (28, ['team28', 'team28'], 2),
  (29, ['team29', 'team29'], 2), (30, ['team30', 'team30'], 2), (31, ['team31', 'team31'], 2), (32, ['team32', 'team32'], 2)]

create_lower_channels(seed_members_life, loser_seed, 1)

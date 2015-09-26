import nflgame as ng
from collections import defaultdict

teams = {
         team[0]: {
                   year: {
                          week: {
                                 'OWN': defaultdict(lambda: 0),
                                 'OPP': defaultdict(lambda: 0)
                                } for week in range(1, 18)
                         } for year in range(2000, 2016)
                  } for team in ng.teams
        }
passing_stats = ['passing_cmp', 'passing_att', 'passing_yds', 'passing_tds', 'passing_ints']
rushing_stats = ['rushing_att', 'rushing_yds', 'rushing_tds']
all_stats = passing_stats + rushing_stats
divider = '-' * (len(all_stats) * 2 + 3) * 7

def add_rushing_stats(year, week, game):
    rushing = game.players.rushing()
    for player in rushing:
        team = player.team
        opp = game.away if game.home == team else game.home
        for stat in rushing_stats:
            teams[team][year][week]['OWN'][stat] += player.__dict__[stat]
            teams[opp][year][week]['OPP'][stat] += player.__dict__[stat]

def add_passing_stats(year, week, game):
    passing = game.players.passing()
    for player in passing:
        team = player.team
        opp = game.away if game.home == team else game.home
        for stat in passing_stats:
            teams[team][year][week]['OWN'][stat] += player.__dict__[stat]
            teams[opp][year][week]['OPP'][stat] += player.__dict__[stat]

def get_team_stats(year, week, which_team):
    if week is None:
        week = list(range(1, 18))
    for wk in week:
        games = ng.games(year, wk)
        for game in games:
            teams[game.home][year][wk]['OWN']['OPP'] = game.away
            teams[game.away][year][wk]['OWN']['OPP'] = '@ ' + game.home
            teams[game.home][year][wk]['OWN']['pts'] = game.score_home
            teams[game.home][year][wk]['OPP']['pts'] = game.score_away
            teams[game.away][year][wk]['OWN']['pts'] = game.score_away
            teams[game.away][year][wk]['OPP']['pts'] = game.score_home
            if which_team is None or len(set(which_team) & set([game.home, game.away])) > 0:
                add_passing_stats(year, wk, game)
                add_rushing_stats(year, wk, game)

def print_team_stats(year, week, which_team):
    if isinstance(which_team, list):
        which_team = set(which_team)
    else:
        which_team = set([which_team])
    if week is None:
        week = list(range(1, 18))
    for team in ng.teams:
        if len(set(team) & which_team) > 0 or None in which_team:
            print '{year} {team}'.format(year=year, team=team[3])
            print 'week'.rjust(6),
            print ' '.join([(stat[0] + stat[7:]).rjust(6) for stat in all_stats]),
            print 'score'.rjust(6),
            print 'OPP'.rjust(6),
            print ' '.join([(stat[0] + stat[7:]).rjust(6) for stat in all_stats])
            print divider
            for wk in week:
                print str(wk).rjust(6),
                own_stats = teams[team[0]][year][wk]['OWN']
                opp_stats = teams[team[0]][year][wk]['OPP']
                print ' '.join([str(own_stats[key]).rjust(6) for key in all_stats]),
                print '{own}-{opp}'.format(own=own_stats['pts'], opp=opp_stats['pts']).rjust(6),
                print '{opp}'.format(opp=own_stats['OPP']).rjust(6),
                print ' '.join([str(opp_stats[key]).rjust(6) for key in all_stats])
            print divider
            print ''

def run(year, week, which_team):
    get_team_stats(year, week, which_team)
    print_team_stats(year, week, which_team)

def parse_seq(arg_str, integer=True):
    if arg_str:
        seq = arg_str.split(',')
        seq = [sq.split('-') for sq in seq]
    else:
        return None
    new_seq = []
    for sq in seq:
        assert (len(sq) < 3 and not (len(sq) > 1 and not integer))
        if len(sq) == 1:
            if integer:
                sq = int(sq[0])
                assert 1 <= sq < 18
            else:
                sq = sq[0].upper()
            new_seq.append(sq)
        elif integer:
            for i in range(int(sq[0]), int(sq[1]) + 1):
                assert 1 <= i < 18
                new_seq.append(i)
    return list(set(new_seq))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("year", help="which year do you want stats from?", type=int, choices=list(range(2009, 2016)))
    parser.add_argument("-w", "--week", help="Which week(s)? Use '1-5,7,...' for multiple weeks. Omit to include all weeks.")
    parser.add_argument("-t", "--team", help="Which team(s)? Use 'IND,NE,...' for multiple teams. Omit to include all teams.")
    args = parser.parse_args()
    year = args.year
    week = parse_seq(args.week)
    team = parse_seq(args.team, False)
    run(year, week, team)

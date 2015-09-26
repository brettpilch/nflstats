#!/usr/local/bin/python

"""
Query the NFL.com database to get weekly team-level stats for a given team(s)
in a given season and week(s). Call this script from the command-line with a
year argument to get all the weekly stats for every team in that year. Supply
optional week and team arguments to only show certain weeks or teams. The result
is a display of standard passing and rushing stats along with the opponent's stats
and the score for each game.

Dependencies:
    python 2.7
    nflgame (pip install nflgame) or (https://github.com/BurntSushi/nflgame)

usage: nflstats.py [-h] [-w WEEK] [-t TEAM]
                   {2009,2010,2011,2012,2013,2014,2015}

(The only required argument is the year, which must be between 2009 and 2015.)

Command-line example calls:
$ python -h
    -- displays the help file, documentation for the command-line arguments.

$ python nflstats.py 2014
    -- displays all the weekly stats for every team for every week of the 2014 season.

$ python nflstats.py 2013 -w 5 -t IND
    -- displays the Indianapolis Colts team stats in 2013 week 5.

$ python nflstats.py 2012 -w 3,5-9,13
    -- displays stats for all teams in 2012 weeks 3, 5-9, and 13.
    -- use commas to select multiple weeks.
    -- use hyphens to include a range of consecutive weeks.

$ python nflstats.py 2011 -t TB,NYG,CAR
    -- displays stats for Tampa Bay, New York Giants, and Carolina for all of 2011.
    -- use commas to separate team names
"""

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
    """
    Collect all rushing stats from a certain game.
    """
    rushing = game.players.rushing()
    for player in rushing:
        team = player.team
        opp = game.away if game.home == team else game.home
        for stat in rushing_stats:
            teams[team][year][week]['OWN'][stat] += player.__dict__[stat]
            teams[opp][year][week]['OPP'][stat] += player.__dict__[stat]

def add_passing_stats(year, week, game):
    """
    Collect all passing stats from a certain game.
    """
    passing = game.players.passing()
    for player in passing:
        team = player.team
        opp = game.away if game.home == team else game.home
        for stat in passing_stats:
            teams[team][year][week]['OWN'][stat] += player.__dict__[stat]
            teams[opp][year][week]['OPP'][stat] += player.__dict__[stat]

def get_team_stats(year, week, which_team):
    """
    Collect all stats for a given year, week(s), team(s).
    """
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
    """
    'Pretty-print' all the collected stats for the selected team(s) and week(s).
    """
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
    """
    Collect and print the stats for the selected team(s) and week(s)
    """
    get_team_stats(year, week, which_team)
    print_team_stats(year, week, which_team)

def parse_seq(arg_str, integer=True):
    """
    A helper function to convert comma- and hyphen-separated command-line arguments
    into a list.
    example: parse_seq('1,3-5,9') => [1,3,4,5,9]
    """
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

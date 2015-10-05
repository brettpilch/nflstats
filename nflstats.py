#!/usr/local/bin/python

"""
Query the NFL.com database to get weekly team-level stats for a given team(s)
in a given season and week(s). Call this script from the command-line with a
year argument to get all the weekly stats for every team in that year. Supply
optional week and team arguments to only show certain weeks or teams. The result
is a display of standard passing and rushing stats along with the opponent's stats
and the score for each game.

-----------------------------------------------------------------------------------------

DEPENDENCIES:
    python 2.7
    nflgame (pip install nflgame) or (https://github.com/BurntSushi/nflgame)

------------------------------------------------------------------------------------------

COMMAND-LINE DOCUMENTATION:
usage: nflstats.py [-h] [-w WEEK] [-t TEAM] [-c] [-r] {2009,2010,2011,2012,2013,2014,2015}

display NFL team stats for a given season, teams, and weeks

positional arguments:
  {2009,2010,2011,2012,2013,2014,2015}
                        which year do you want stats from?

optional arguments:
  -h, --help            show this help message and exit
  -w WEEK, --week WEEK  Which week(s)? Use '1-5,7,...' for multiple weeks.
                        Omit to include all weeks.
  -t TEAM, --team TEAM  Which team(s)? Use 'IND,NE,...' for multiple teams.
                        Omit to include all teams.
  -c, --cum             Flag to show cumulative stats instead of single-game
                        stats.
  -r, --rate            Flag to show rate stats instead of gross stats.

(The only required argument is the year, which must be between 2009 and 2015.)

------------------------------------------------------------------------------------------

COMMAND-LINE EXAMPLES:
$ python nflstats.py -h
    -- displays the help file (documentation for the command-line arguments).

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

PASSING_STATS = ['passing_cmp', 'passing_att', 'passing_yds', 'passing_tds', 'passing_ints']
RUSHING_STATS = ['rushing_att', 'rushing_yds', 'rushing_tds']
DEFENSE_STATS = ['defense_sk']
ALL_STATS = PASSING_STATS + DEFENSE_STATS + RUSHING_STATS
RATE_STATS = ['passing_cmp%', 'passing_ypa', 'passing_ypc',
              'passing_int%', 'passing_td%', 'passing_sk%', 'rushing_ypa']

STAT_MAP = {'passing_cmp': 'p_cmp', 'passing_att': 'p_att', 'passing_yds': 'p_yds',
            'passing_tds': 'p_tds', 'passing_ints': 'p_ints', 'defense_sk': 'p_sck',
            'rushing_att': 'r_att', 'rushing_yds': 'r_yds', 'rushing_tds': 'r_tds',
            'passing_cmp%': 'p_cmp%', 'passing_ypa': 'p_ypa', 'passing_ypc': 'p_ypc',
            'passing_int%': 'p_int%', 'passing_td%': 'p_td%', 'passing_sk%': 'p_sk%',
            'rushing_ypa': 'r_ypa'}

class League:
    """
    A class that collects data using the nflgame API, then uses it to get cumulative and rate stats.
    """
    def batch_init(self, year, week, which_team, cum=False, rate=False):
        self.year = year
        self.week = week
        self.which_team = which_team
        self.cum = cum
        self.rate = rate
        self.teams = self.structure()

    def structure(self):
        """
        Creates a nested dictionary data structure to hold the data.
        """
        teams = {team[0]: dict() for team in ng.teams}
        for team, teamdict in teams.items():
            for year in self.year:
                yeardict = teamdict[year] = dict()
                for wk in self.week:
                    weekdict = yeardict[wk] = dict()
                    for side in ['OWN', 'OPP', 'OWN_TOTAL', 'OPP_TOTAL']:
                        weekdict[side] = defaultdict(lambda: 0)
        return teams

    def make_rate_stats(self):
        """
        Use the accumulated stats to make rate stats like yards/carry, yards/attempt, completion %, etc.
        """
        for team, teamdict in self.teams.items():
            for year, yeardict in teamdict.items():
                weeks = 0
                for week, weekdict in yeardict.items():
                    if weekdict['OWN']['OPP']:
                        weeks += 1
                    if self.cum:
                        own = weekdict['OWN_TOTAL']
                        opp = weekdict['OPP_TOTAL']
                        for side in [own, opp]:
                            if weeks:
                                side['ppg'] = round(side['pts'] / float(weeks), 2)
                    for side, side_stats in weekdict.items():
                        if side_stats['passing_cmp'] > 0:
                            side_stats['passing_cmp%'] = \
                            round(side_stats['passing_cmp'] / float(side_stats['passing_att']) * 100, 2)
                            side_stats['passing_ypa'] = \
                            round(side_stats['passing_yds'] / float(side_stats['passing_att']), 2)
                            side_stats['passing_ypc'] = \
                            round(side_stats['passing_yds'] / float(side_stats['passing_cmp']), 2)
                            side_stats['passing_int%'] = \
                            round(side_stats['passing_ints'] / float(side_stats['passing_att']) * 100, 2)
                            side_stats['passing_td%'] = \
                            round(side_stats['passing_tds'] / float(side_stats['passing_att']) * 100, 2)
                            side_stats['rushing_ypa'] = \
                            round(side_stats['rushing_yds'] / float(side_stats['rushing_att']), 2)
                            side_stats['passing_sk%'] = \
                            round(side_stats['defense_sk'] / float(side_stats['defense_sk'] + side_stats['passing_att']) * 100, 2)

    def accumulate_stats(self):
        """
        Add all stats from previous weeks to each weekly total and store in the dictionary.
        """
        for team, teamdict in self.teams.items():
            for year, yeardict in teamdict.items():
                for week, thisweek in yeardict.items():
                    for stat in ALL_STATS + ['pts']:
                        if week - 1 in yeardict:
                            lastweek = yeardict[week - 1]
                            thisweek['OWN_TOTAL'][stat] = lastweek['OWN_TOTAL'][stat] + thisweek['OWN'][stat]
                            thisweek['OPP_TOTAL'][stat] = lastweek['OPP_TOTAL'][stat] + thisweek['OPP'][stat]
                        else:
                            thisweek['OWN_TOTAL'][stat] = thisweek['OWN'][stat]
                            thisweek['OPP_TOTAL'][stat] = thisweek['OPP'][stat]

    def add_rushing_stats(self, year, week, game):
        """
        Collect all rushing stats from a certain game.
        """
        for player in game.players.rushing():
            team = player.team
            opp = game.away if game.home == team else game.home
            for stat in RUSHING_STATS:
                if team in self.which_team:
                    self.teams[team][year][week]['OWN'][stat] += player.__dict__[stat]
                if opp in self.which_team:
                    self.teams[opp][year][week]['OPP'][stat] += player.__dict__[stat]

    def add_passing_stats(self, year, week, game):
        """
        Collect all passing stats from a certain game.
        """
        for player in game.players.passing():
            team = player.team
            opp = game.away if game.home == team else game.home
            for stat in PASSING_STATS:
                if team in self.which_team:
                    self.teams[team][year][week]['OWN'][stat] += player.__dict__[stat]
                if opp in self.which_team:
                    self.teams[opp][year][week]['OPP'][stat] += player.__dict__[stat]

    def add_defense_stats(self, year, week, game):
        for player in game.players.defense():
            team = player.team
            opp = game.away if game.home == team else game.home
            for stat in DEFENSE_STATS:
                if opp in self.which_team:
                    self.teams[opp][year][week]['OWN'][stat] += int(player.__dict__[stat])
                if team in self.which_team:
                    self.teams[team][year][week]['OPP'][stat] += int(player.__dict__[stat])

    def make_team_stats(self):
        """
        Collect all stats for a given year, week(s), team(s).
        """
        for yr in self.year:
            for wk in self.week:
                games = ng.games(yr, wk)
                for game in games:
                    matchup = {game.home: {'opp': game.away,
                                           'own_pts': game.score_home,
                                           'opp_pts': game.score_away},
                               game.away: {'opp': game.home,
                                           'own_pts': game.score_away,
                                           'opp_pts': game.score_home}}
                    for team, teamdict in matchup.items():
                        if team in self.which_team:
                            self.teams[team][yr][wk]['OWN']['OPP'] = teamdict['opp']
                            self.teams[team][yr][wk]['OWN']['pts'] = teamdict['own_pts']
                            self.teams[team][yr][wk]['OPP']['pts'] = teamdict['opp_pts']
                            self.teams[team][yr][wk]['OWN_TOTAL']['OPP'] = teamdict['opp']
                    self.add_defense_stats(yr, wk, game)
                    self.add_passing_stats(yr, wk, game)
                    self.add_rushing_stats(yr, wk, game)

    def __repr__(self):
        """
        Display stats in a nice-looking table.
        """
        if self.rate:
            which_stats = RATE_STATS
        else:
            which_stats = ALL_STATS
        divider = '-' * (len(which_stats) * 2 + 5) * 7
        if self.cum:
            mine = 'OWN_TOTAL'
            theirs = 'OPP_TOTAL'
        else:
            mine = 'OWN'
            theirs = 'OPP'
        output = ''
        for team in ng.teams:
            if len(set(team) & set(self.which_team)) > 0:
                output += '{team}\n'.format(team=team[3])
                output += 'year'.rjust(6) + 'week'.rjust(6)
                output += ' ' + ' '.join([STAT_MAP[stat].rjust(6) for stat in which_stats])
                output += 'Pts'.rjust(6) + 'oPts'.rjust(6)
                output += 'OPP'.rjust(6)
                output += ' '.join([STAT_MAP[stat].rjust(6) for stat in which_stats]) + '\n'
                output += divider + '\n'
                for yr in self.year:
                    for wk in self.week:
                        output += str(yr).rjust(6) + str(wk).rjust(6)
                        own_stats = self.teams[team[0]][yr][wk][mine]
                        opp_stats = self.teams[team[0]][yr][wk][theirs]
                        output += ' ' + ' '.join([str(own_stats[key]).rjust(6) for key in which_stats])
                        if self.rate and self.cum:
                            output += str(own_stats['ppg']).rjust(6) + str(opp_stats['ppg']).rjust(6)
                        else:
                            output += str(own_stats['pts']).rjust(6) + str(opp_stats['pts']).rjust(6)
                        output += str(own_stats['OPP']).rjust(6)
                        output += ' '.join([str(opp_stats[key]).rjust(6) for key in which_stats]) + '\n'
                    output += divider + '\n'
        return output

    def compile(self):
        self.make_team_stats()
        if self.cum:
            self.accumulate_stats()
        if self.rate:
            self.make_rate_stats()

def default(input_value, default_value):
    """
    If input is None, return the default_value.
    """
    if not input_value:
        return default_value
    else:
        return input_value

def run(year, week, which_team, cum=False, rate=False):
    """
    Collect and print the stats for the selected team(s) and week(s)
    """
    league = League()
    league.batch_init(year, week, which_team, cum, rate)
    league.compile()
    print(league)

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
            else:
                sq = sq[0].upper()
            new_seq.append(sq)
        elif integer:
            for i in range(int(sq[0]), int(sq[1]) + 1):
                new_seq.append(i)
    return list(set(new_seq))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="display NFL team stats for a given season, teams and weeks")
    parser.add_argument("-y", "--year", help="which year do you want stats from? Omitting defaults to 2014")
    parser.add_argument("-w", "--week", help="Which week(s)? Use '1-5,7,...' for multiple weeks. Omit to include all weeks.")
    parser.add_argument("-t", "--team", help="Which team(s)? Use 'IND,NE,...' for multiple teams. Omit to include all teams.")
    parser.add_argument("-c", "--cum", help="Flag to show cumulative stats instead of single-game stats.", action='store_true')
    parser.add_argument("-r", "--rate", help="Flag to show rate stats instead of gross stats.", action='store_true')
    args = parser.parse_args()
    year = default(parse_seq(args.year), [2013, 2014])
    week = default(parse_seq(args.week), list(range(1, 18)))
    team = default(parse_seq(args.team, False), list(ng.teams))
    run(year, week, team, args.cum, args.rate)

#!/usr/local/bin/python

"""
Query the NFL.com database to get weekly team-level stats for a given team(s)
in a given season and week(s). Call this script from the command-line with a
year argument to get all the weekly stats for every team in that year. Supply
optional week and team arguments to only show certain weeks or teams. The
result is a display of standard passing and rushing stats along with the
opponent's stats and the score for each game.

-------------------------------------------------------------------------------

DEPENDENCIES:
    python 2.7
    nflgame (pip install nflgame) or (https://github.com/BurntSushi/nflgame)

-------------------------------------------------------------------------------

COMMAND-LINE DOCUMENTATION:
usage: nflstats.py [-h] [-y YEAR] [-w WEEK] [-t TEAM] [-s SITE] [-c] [-r]

Display NFL team stats for a given season, teams and weeks

optional arguments:
  -h, --help            show this help message and exit
  -y YEAR, --year YEAR  Which year(s) do you want stats from? Acceptable years
                        are between 2009 and 2015. Use '2009,2011-2013,...'
                        for multiple years. Default value is 2013-2014
  -w WEEK, --week WEEK  Which week(s) do you want to include? Acceptable weeks
                        are between 1 and 17. Use '1-5,7,...' for multiple
                        weeks. Defaults to include all weeks.
  -t TEAM, --team TEAM  Which team(s) do you want to include? Accepts any of
                        the common 2-3 letter abbreviations. Use 'IND,NE,...'
                        for multiple teams. Defaults to include all teams.
  -s SITE, --site SITE  Which sites do you want to include? Acceptable values
                        are 'home' and 'away'. Defaults to include both sites
  -c, --cum             Flag to show cumulative stats instead of single-game
                        stats.
  -r, --rate            Flag to show rate stats instead of gross stats.

-------------------------------------------------------------------------------

COMMAND-LINE EXAMPLES:
$ python nflstats.py -h
    -- displays the help file (documentation for the command-line arguments).

$ python nflstats.py -y 2014 -s home
    -- displays all the weekly stats for every team for every week of the
       2014 season when they played at home.

$ python nflstats.py -y 2013 -w 5 -t IND -r
    -- displays the Indianapolis Colts rate stats in 2013 week 5.

$ python nflstats.py -y 2010,2012-2014 -w 3,5-9,13 -cr
    -- displays cumulative rate stats for all teams in 2010, 2012, 2013, and
       2014 for weeks 3, 5-9, and 13.
    -- use commas to select multiple years or weeks.
    -- use hyphens to include a range of consecutive years or weeks.

$ python nflstats.py -y 2011 -t TB,NYG
    -- displays stats for Tampa Bay, and New York Giants for all of 2011.
    -- use commas to separate team names
"""

from __future__ import division
import nflgame as ng
from collections import defaultdict

PASSING_STATS = ['passing_cmp', 'passing_att', 'passing_yds', 'passing_tds',
                 'passing_ints']
RUSHING_STATS = ['rushing_att', 'rushing_yds', 'rushing_tds']
DEFENSE_STATS = ['defense_sk']
ALL_STATS = PASSING_STATS + DEFENSE_STATS + RUSHING_STATS
RATE_STATS = ['passing_cmp%', 'passing_ypa', 'passing_ypc',
              'passing_int%', 'passing_td%', 'passing_sk%', 'rushing_ypa']

STAT_MAP = {'passing_cmp': 'p_cmp', 'passing_att': 'p_att',
            'passing_yds': 'p_yds', 'passing_tds': 'p_tds',
            'passing_ints': 'p_ints', 'defense_sk': 'p_sck',
            'rushing_att': 'r_att', 'rushing_yds': 'r_yds',
            'rushing_tds': 'r_tds', 'passing_cmp%': 'p_cmp%',
            'passing_ypa': 'p_ypa', 'passing_ypc': 'p_ypc',
            'passing_int%': 'p_int%', 'passing_td%': 'p_td%',
            'passing_sk%': 'p_sk%', 'rushing_ypa': 'r_ypa'}

class League(object):
    """
    A class that collects data using the nflgame API,
    then uses it to get cumulative and rate stats.
    """
    def __init__(self, year, week, which_team, site, cum=False, rate=False):
        """
        Tell the league which teams, years, weeks, etc. to get data for.
        """
        self.year = year
        self.week = week
        self.which_team = which_team
        self.site = site
        self.cum = cum
        self.rate = rate
        self.teams = self.structure()

    def structure(self):
        """
        Creates a nested dictionary data structure to hold the data.
        """
        teams = {team[0]: dict() for team in ng.teams}
        for teamdict in teams.values():
            for year in self.year:
                yeardict = teamdict[year] = dict()
                for week in self.week:
                    weekdict = yeardict[week] = dict()
                    for side in ['OWN', 'OPP', 'OWN_TOTAL', 'OPP_TOTAL']:
                        weekdict[side] = defaultdict(lambda: 0)
        return teams

    def make_rate_stats(self):
        """
        Use the accumulated stats to make rate stats like yards/carry,
        yards/attempt, completion %, etc.
        """
        for teamdict in self.teams.values():
            for yeardict in teamdict.values():
                weeks = 0
                for weekdict in yeardict.values():
                    if weekdict['OWN']['OPP']:
                        weeks += 1
                    if self.cum:
                        own = weekdict['OWN_TOTAL']
                        opp = weekdict['OPP_TOTAL']
                        for side in [own, opp]:
                            if weeks:
                                side['ppg'] = round(side['pts'] / float(weeks), 2)
                    for side_stats in weekdict.values():
                        if side_stats['passing_cmp'] > 0:
                            side_stats['passing_cmp%'] = \
                            round(side_stats['passing_cmp'] /
                                  side_stats['passing_att'] * 100, 2)
                            side_stats['passing_ypa'] = \
                            round(side_stats['passing_yds'] /
                                  side_stats['passing_att'], 2)
                            side_stats['passing_ypc'] = \
                            round(side_stats['passing_yds'] /
                                  side_stats['passing_cmp'], 2)
                            side_stats['passing_int%'] = \
                            round(side_stats['passing_ints'] /
                                  side_stats['passing_att'] * 100, 2)
                            side_stats['passing_td%'] = \
                            round(side_stats['passing_tds'] /
                                  side_stats['passing_att'] * 100, 2)
                            side_stats['rushing_ypa'] = \
                            round(side_stats['rushing_yds'] /
                                  side_stats['rushing_att'], 2)
                            side_stats['passing_sk%'] = \
                            round(side_stats['defense_sk'] /
                                  (side_stats['defense_sk'] +
                                   side_stats['passing_att']) * 100, 2)

    def accumulate_stats(self):
        """
        Add all stats from previous weeks to each weekly total
        and store in the dictionary.
        """
        for teamdict in self.teams.values():
            for yeardict in teamdict.values():
                for week, thisweek in yeardict.items():
                    for stat in ALL_STATS + ['pts']:
                        if week - 1 in yeardict:
                            lastweek = yeardict[week - 1]
                            thisweek['OWN_TOTAL'][stat] = \
                            lastweek['OWN_TOTAL'][stat] + thisweek['OWN'][stat]
                            thisweek['OPP_TOTAL'][stat] = \
                            lastweek['OPP_TOTAL'][stat] + thisweek['OPP'][stat]
                        else:
                            thisweek['OWN_TOTAL'][stat] = thisweek['OWN'][stat]
                            thisweek['OPP_TOTAL'][stat] = thisweek['OPP'][stat]

    def add_rushing_stats(self, which_team, year, week, game):
        """
        Collect all rushing stats from a certain game.
        """
        for player in game.players.rushing():
            team = player.team
            opp = game.away if game.home == team else game.home
            for stat in RUSHING_STATS:
                if team == which_team:
                    self.teams[team][year][week]['OWN'][stat] += \
                    player.__dict__[stat]
                elif opp == which_team:
                    self.teams[opp][year][week]['OPP'][stat] += \
                    player.__dict__[stat]

    def add_passing_stats(self, which_team, year, week, game):
        """
        Collect all passing stats from a certain game.
        """
        for player in game.players.passing():
            team = player.team
            opp = game.away if game.home == team else game.home
            for stat in PASSING_STATS:
                if team == which_team:
                    self.teams[team][year][week]['OWN'][stat] += \
                    player.__dict__[stat]
                elif opp == which_team:
                    self.teams[opp][year][week]['OPP'][stat] += \
                    player.__dict__[stat]

    def add_defense_stats(self, which_team, year, week, game):
        """
        Collect all defense stats from a certain game.
        """
        for player in game.players.defense():
            team = player.team
            opp = game.away if game.home == team else game.home
            for stat in DEFENSE_STATS:
                if opp == which_team:
                    self.teams[opp][year][week]['OWN'][stat] += \
                    float(player.__dict__[stat])
                elif team == which_team:
                    self.teams[team][year][week]['OPP'][stat] += \
                    float(player.__dict__[stat])

    def make_team_stats(self):
        """
        Collect all stats for a given year, week(s), team(s).
        """
        for year in self.year:
            for week in self.week:
                games = ng.games(year, week)
                for game in games:
                    if 'home' in self.site and game.home in self.which_team:
                        home_team = self.teams[game.home][year][week]
                        home_team['OWN']['game'] = game
                        home_team['OWN']['OPP'] = game.away
                        home_team['OWN']['pts'] = game.score_home
                        home_team['OPP']['pts'] = game.score_away
                        home_team['OWN_TOTAL']['OPP'] = game.away
                        self.add_defense_stats(game.home, year, week, game)
                        self.add_passing_stats(game.home, year, week, game)
                        self.add_rushing_stats(game.home, year, week, game)
                    if 'away' in self.site and game.away in self.which_team:
                        away_team = self.teams[game.away][year][week]
                        away_team['OWN']['game'] = game
                        away_team['OWN']['OPP'] = '@ ' + game.home
                        away_team['OWN']['pts'] = game.score_away
                        away_team['OPP']['pts'] = game.score_home
                        away_team['OWN_TOTAL']['OPP'] = game.home
                        self.add_defense_stats(game.away, year, week, game)
                        self.add_passing_stats(game.away, year, week, game)
                        self.add_rushing_stats(game.away, year, week, game)

    def game_player_stats(self, team, year, week):
        """
        Returns a list of player stats for a given week
        """
        game = self.teams[team][year][week]['OWN']['game']
        output = ['{year} week {week} {score}'.format(
            year = year, week = week, score = game.nice_score())]
        for side in [game.away, game.home]:
            output.append(side + ' Passing Stats:')
            passing_header = ''.rjust(20)
            passing_header += ' ' + ' '.join([STAT_MAP[stat].rjust(6)
                                              for stat in PASSING_STATS])
            output.append(passing_header)
            for player in game.players.passing():
                if player.team == side:
                    statline = str(player).rjust(20)
                    statline += ' '.join([str(player.__dict__[stat]).rjust(6) for stat in PASSING_STATS])
                    output.append(statline)
            output.append(side + ' Rushing Stats:')
            rushing_header = ''.rjust(20)
            rushing_header += ' ' + ' '.join([STAT_MAP[stat].rjust(6)
                                              for stat in RUSHING_STATS])
            output.append(rushing_header)
            for player in game.players.rushing():
                if player.team == side:
                    statline = str(player).rjust(20)
                    statline += ' '.join([str(player.__dict__[stat]).rjust(6) for stat in RUSHING_STATS])
                    output.append(statline)
            output.append(side + ' Defense Stats:')
            defense_header = ''.rjust(20)
            defense_header += 'sacks'.rjust(6)
            output.append(defense_header)
            for player in game.players.defense():
                if player.team == side and player.__dict__['defense_sk'] > 0:
                    statline = str(player).rjust(20)
                    statline += str(player.__dict__['defense_sk']).rjust(6)
                    output.append(statline)
        return output

    def game_pbp(self, team, year, week):
        """
        Returns a list of all plays in a game.
        """
        game = self.teams[team][year][week]['OWN']['game']
        plays = ng.combine_plays([game])
        return [game.nice_score(), ''] + [str(play) for play in plays]

    def game_scoring_plays(self, team, year, week):
        game = self.teams[team][year][week]['OWN']['game']
        return [game.nice_score(), ''] + game.scores


    def has_stats(self, team, year, week):
        """
        Return True if stats have been gathered from the given team,year,week.
        """
        return self.teams[team][year][week]['OWN']['passing_att'] > 0

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
            if team[0] in self.which_team:
                output += '{team}\n'.format(team=team[3])
                output += 'team'.rjust(6) + 'year'.rjust(6) + 'week'.rjust(6)
                output += ' ' + ' '.join([STAT_MAP[stat].rjust(6)
                                          for stat in which_stats])
                output += 'Pts'.rjust(6) + 'oPts'.rjust(6)
                output += 'OPP'.rjust(6)
                output += ' '.join([STAT_MAP[stat].rjust(6)
                                    for stat in which_stats]) + '\n'
                output += divider + '\n'
                for year in self.year:
                    for week in self.week:
                        if self.has_stats(team[0], year, week):
                            output += str(team[0]).rjust(6) + \
                                      str(year).rjust(6) + str(week).rjust(6)
                            own_stats = self.teams[team[0]][year][week][mine]
                            opp_stats = self.teams[team[0]][year][week][theirs]
                            output += ' '
                            output += ' '.join([str(own_stats[key]).rjust(6)
                                                for key in which_stats])
                            if self.rate and self.cum:
                                output += str(own_stats['ppg']).rjust(6)
                                output += str(opp_stats['ppg']).rjust(6)
                            else:
                                output += str(own_stats['pts']).rjust(6)
                                output += str(opp_stats['pts']).rjust(6)
                            output += str(own_stats['OPP']).rjust(6)
                            output += ' '.join([str(opp_stats[key]).rjust(6)
                                                for key in which_stats]) + '\n'
                    output += divider + '\n'
        return output

    def compile(self):
        """
        Collect the data, and make cumulative and rate stats if needed.
        """
        self.make_team_stats()
        if self.cum:
            self.accumulate_stats()
        if self.rate:
            self.make_rate_stats()

def run(year, week, which_team, site, cum=False, rate=False):
    """
    Collect and print the stats for the selected team(s) and week(s).
    """
    league = League(year, week, which_team, site, cum, rate)
    league.compile()
    print league

def parse_seq(arg_str, default_value, acceptable, integer=True):
    """
    A helper function to convert comma- and hyphen-separated command-line
    arguments into a list.
    example: parse_seq('1,3-5,9') => [1,3,4,5,9]
    """
    if arg_str:
        sequence = arg_str.split(',')
        sequence = [hyphenated.split('-') for hyphenated in sequence]
    else:
        return default_value
    new_sequence = []
    for seq in sequence:
        assert len(seq) < 3 and not (len(seq) > 1 and not integer)
        if len(seq) == 1:
            if integer:
                seq = int(seq[0])
            else:
                seq = str(seq[0])
            new_sequence.append(seq)
        elif integer:
            for i in range(int(seq[0]), int(seq[1]) + 1):
                new_sequence.append(i)
    for item in new_sequence:
        if item not in acceptable:
            print "WARNING: {} is not an acceptable input".format(item)
            print "using default value {} instead".format(default_value)
            return default_value
    return list(set(new_sequence))

def main():
    """
    Parse the command-line arguments and run the program accordingly.
    """
    import argparse
    parser = argparse.ArgumentParser(description="""Display NFL team
                        stats for a given season, teams and weeks""")
    parser.add_argument("-y", "--year",
                        help="""Which year(s) do you want stats from?
                        Acceptable years are between 2009 and 2015.
                        Use '2009,2011-2013,...' for multiple years.
                        Default value is 2013-2014""")
    parser.add_argument("-w", "--week",
                        help="""Which week(s) do you want to include?
                        Acceptable weeks are between 1 and 17.
                        Use '1-5,7,...' for multiple weeks.
                        Defaults to include all weeks.""")
    parser.add_argument("-t", "--team",
                        help="""Which team(s) do you want to include?
                        Accepts any of the common 2-3 letter abbreviations.
                        Use 'IND,NE,...' for multiple teams.
                        Defaults to include all teams.""")
    parser.add_argument("-s", "--site",
                        help="""Which sites do you want to include?
                        Acceptable values are 'home' and 'away'.
                        Defaults to include both sites""")
    parser.add_argument("-c", "--cum",
                        help="""Flag to show cumulative stats instead of
                        single-game stats.""",
                        action='store_true')
    parser.add_argument("-r", "--rate",
                        help="""Flag to show rate stats instead of gross
                        stats.""",
                        action='store_true')
    args = parser.parse_args()
    year = parse_seq(args.year, [2013, 2014], list(range(2009, 2016)))
    week = parse_seq(args.week, list(range(1, 18)), list(range(1, 18)))
    team = parse_seq(args.team, [team[0] for team in ng.teams],
                     [team[0] for team in ng.teams], False)
    site = parse_seq(args.site, ['home', 'away'], ['home', 'away'], False)
    run(year, week, team, site, args.cum, args.rate)

if __name__ == '__main__':
    main()

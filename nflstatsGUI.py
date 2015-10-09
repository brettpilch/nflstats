#!/usr/local/bin/python

"""
Query the NFL.com database to get weekly team-level stats for a given team(s)
in a given season and week(s). Run this script to open up a GUI interface in
which you can select a year, team, and weeks to get stats from. The result
is a display of standard passing and rushing stats along with the opponent's stats
and the score for each game. Check the 'show cumulative stats' and 'show rate stats'
buttons to show cumulative and rate stats.

-----------------------------------------------------------------------------------------

DEPENDENCIES:
    python 2.7
    nflgame (pip install nflgame) or (https://github.com/BurntSushi/nflgame)
"""

from nflstats import League, parse_seq
import Tkinter as gui
import nflgame as ng

TEAMS = ["All"] + [team[0] for team in ng.teams]
YEARS = ["All"] + list(range(2009, 2016))
WEEKS = ["All"] + list(range(1, 18))
SITES = ["All", "home", "away"]

class Status(object):
    def __init__(self):
        self.league = None

    def set_league(self, league):
        self.league = league


def get_results(team_list, year_list, week_list, site_list, cum, rate, widget, status):
    teams_index = map(int, team_list.curselection())
    teams = [TEAMS[index] for index in teams_index]
    if "All" in teams:
        thisteam = parse_seq(None, [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    else:
        team_str = ','.join(teams)
        thisteam = parse_seq(team_str, [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    week_index = map(int, week_list.curselection())
    weeks = [str(WEEKS[index]) for index in week_index]
    if "All" in weeks:
        thisweek = parse_seq(None, list(range(1, 18)), list(range(1, 18)))
    else:
        week_str = ','.join(weeks)
        thisweek = parse_seq(week_str, list(range(1, 18)),
                             list(range(1, 18)))
    year_index = map(int, year_list.curselection())
    years = [str(YEARS[index]) for index in year_index]
    if "All" in years:
        thisyear = parse_seq(None, [2013, 2014], list(range(2009, 2016)))
    else:
        year_str = ','.join(years)
        thisyear = parse_seq(year_str, [2013, 2014], list(range(2009, 2016)))
    site_index = map(int, site_list.curselection())
    sites = [SITES[index] for index in site_index]
    if "All" in sites:
        thissite = parse_seq(None, ['home', 'away'], ['home', 'away'], False)
    else:
        site_str = ','.join(sites)
        thissite = parse_seq(site_str, ['home', 'away'],
                             ['home', 'away'], False)
    league = League(thisyear, thisweek, thisteam, thissite, cum.get(), rate.get())
    league.compile()
    status.set_league(league)
    widget.delete(0, gui.END)
    for line in str(league).splitlines():
        widget.insert(gui.END, str(line))

def game_stats(game_list, status, widget, variety):
    if status.league:
        all_games = str(status.league).splitlines()
        game_index = map(int, game_list.curselection())
        games = [all_games[index] for index in game_index]
        widget.delete(0, gui.END)
        for game in games:
            gamesplit = game.split()[:3]
            if gamesplit[0] in TEAMS:
                team, year, week = game.split()[:3]
                game_obj = status.league.teams[team][int(year)][int(week)]['OWN']['game']
                stats = []
                if variety == 'player':
                    stats = status.league.game_player_stats(team, int(year), int(week))
                elif variety == 'pbp':
                    stats = status.league.game_pbp(team, int(year), int(week))
                elif variety == 'scores':
                    stats = status.league.game_scoring_plays(team, int(year), int(week))
                for row in stats:
                    widget.insert(gui.END, str(row))
                widget.insert(gui.END, '-' * 150)

def runGUI():
    status = Status()
    app = gui.Tk()
    app.title("NFL Team Stats Query")
    app.geometry("1400x800+10+10")

    league_info = gui.Listbox(app, width = 200, height = 20,
                               font = ["courier new", 14],
                               selectmode = gui.MULTIPLE,
                               exportselection = 0)
    league_info.insert(gui.END, "Select parameters below.")

    info = gui.Frame(app)

    selector = gui.Frame(info)

    bottom = gui.Frame(selector)

    select_left = gui.Frame(bottom)
    select_right = gui.Frame(bottom)

    team_label = gui.Label(select_left, text = "Team(s)")
    team_list = gui.Listbox(select_left, width = 10, height = 11,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
                            # exportselection = 0 allows for multiple listboxes
    team_list.insert(gui.END, "All")
    for team in ng.teams:
        team_list.insert(gui.END, team[0])

    # year_frame = gui.Frame(bottom)
    year_label = gui.Label(select_right, text = "Year(s)")
    year_list = gui.Listbox(select_right, width = 10, height = 7,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
    year_list.insert(gui.END, "All")
    for year in range(2009, 2016):
        year_list.insert(gui.END, str(year))

    week_label = gui.Label(select_right, text = "Week(s)")
    week_list = gui.Listbox(select_right, width = 10, height = 7,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
    week_list.insert(gui.END, "All")
    for week in range(1, 18):
        week_list.insert(gui.END, str(week))

    # site_frame = gui.Frame(bottom)
    site_label = gui.Label(select_left, text = "Site(s)")
    site_list = gui.Listbox(select_left, width = 10, height = 3,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
    for site in ["All", "home", "away"]:
        site_list.insert(gui.END, site)

    cum_var = gui.IntVar()
    cum_button = gui.Checkbutton(selector, text="Show Cumulative Stats", 
                                 variable=cum_var)

    rate_var = gui.IntVar()
    rate_button = gui.Checkbutton(selector, text="Show Rate Stats",
                                  variable=rate_var)

    player_frame = gui.Frame(info)
    button_frame = gui.Frame(player_frame)
    game_info = gui.Listbox(player_frame, width = 150, height = 20,
                              font = ["courier new", 14])
    game_info.insert(gui.END, "Player stats")

    button1 = gui.Button(selector, text = 'Get Game Stats', width = 20,
        command = lambda: get_results(team_list, year_list, week_list, site_list,
                                      cum_var, rate_var, league_info, status))

    player_button = gui.Button(button_frame, text = 'Get Player Stats', width = 40,
                               command = lambda: game_stats(league_info,
                                                            status, game_info,
                                                            'player'))
    pbp_button = gui.Button(button_frame, text = 'Get Play-By-Play', width = 40,
                            command = lambda: game_stats(league_info,
                                                         status, game_info,
                                                         'pbp'))
    scores_button = gui.Button(button_frame, text = 'Get Scoring Plays', width = 40,
                               command = lambda: game_stats(league_info,
                                                            status, game_info,
                                                            'scores'))

    league_info.pack()
    player_button.pack(side = gui.LEFT)
    pbp_button.pack(side = gui.LEFT)
    scores_button.pack(side = gui.LEFT)
    info.pack()
    button_frame.pack()
    selector.pack(side = gui.LEFT)
    bottom.pack()
    select_left.pack(side = gui.LEFT)
    team_label.pack()
    team_list.pack()
    # year_frame.pack(side = gui.LEFT)
    year_label.pack()
    year_list.pack()
    select_right.pack(side = gui.LEFT)
    week_label.pack()
    week_list.pack()
    # site_frame.pack(side = gui.LEFT)
    site_label.pack()
    site_list.pack()
    cum_button.pack()
    rate_button.pack()
    button1.pack()
    player_frame.pack(side = gui.LEFT)
    game_info.pack()

    app.mainloop()

if __name__ == '__main__':
    runGUI()
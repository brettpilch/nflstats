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

TEAMS = ["All teams"] + [team[0] for team in ng.teams]
YEARS = ["All years"] + list(range(2009, 2016))
WEEKS = ["All weeks"] + list(range(1, 18))
SITES = ["All sites", "home", "away"]

class Status(object):
    def __init__(self):
        self.league = None

    def set_league(self, league):
        self.league = league


def get_results(team_list, year_list, week_list, site_list, cum, rate, widget, status):
    teams_index = map(int, team_list.curselection())
    teams = [TEAMS[index] for index in teams_index]
    if "All teams" in teams:
        thisteam = parse_seq(None, [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    else:
        team_str = ','.join(teams)
        thisteam = parse_seq(team_str, [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    week_index = map(int, week_list.curselection())
    weeks = [str(WEEKS[index]) for index in week_index]
    if "All weeks" in weeks:
        thisweek = parse_seq(None, list(range(1, 18)), list(range(1, 18)))
    else:
        week_str = ','.join(weeks)
        thisweek = parse_seq(week_str, list(range(1, 18)),
                             list(range(1, 18)))
    year_index = map(int, year_list.curselection())
    years = [str(YEARS[index]) for index in year_index]
    if "All years" in years:
        thisyear = parse_seq(None, [2013, 2014], list(range(2009, 2016)))
    else:
        year_str = ','.join(years)
        thisyear = parse_seq(year_str, [2013, 2014], list(range(2009, 2016)))
    site_index = map(int, site_list.curselection())
    sites = [SITES[index] for index in site_index]
    if "All sites" in sites:
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

def game_stats(game_list, status, widget):
    if status.league:
        all_games = str(status.league).splitlines()
        game_index = map(int, game_list.curselection())
        games = [all_games[index] for index in game_index]
        for game in games:
            team, year, week = game.split()[:3]
            game_obj = status.league.teams[team][int(year)][int(week)]['OWN']['game']
            player_stats = status.league.game_player_stats(team, int(year), int(week))
            widget.delete(0, gui.END)
            for row in player_stats:
                widget.insert(gui.END, str(row))

def runGUI():
    status = Status()
    app = gui.Tk()
    app.title("NFL Team Stats Query")
    app.geometry("1300x800+10+10")

    display_text = gui.Listbox(app, width = 200, height = 20,
                               font = ["courier new", 14],
                               selectmode = gui.MULTIPLE,
                               exportselection = 0)
    display_text.insert(gui.END, "Select parameters below.")

    info = gui.Frame(app)

    selector = gui.Frame(info)

    bottom = gui.Frame(selector)

    team_frame = gui.Frame(bottom)
    team_label = gui.Label(team_frame, text = "Select team(s)")
    team_list = gui.Listbox(team_frame, width = 25, height = 10,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
                            # exportselection = 0 allows for multiple listboxes
    team_list.insert(gui.END, "All teams")
    for team in ng.teams:
        team_list.insert(gui.END, team[3])

    year_frame = gui.Frame(bottom)
    year_label = gui.Label(year_frame, text = "Select year(s)")
    year_list = gui.Listbox(year_frame, width = 15, height = 10,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
    year_list.insert(gui.END, "All years")
    for year in range(2009, 2016):
        year_list.insert(gui.END, str(year))

    week_frame = gui.Frame(bottom)
    week_label = gui.Label(week_frame, text = "Select week(s)")
    week_list = gui.Listbox(week_frame, width = 15, height = 10,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
    week_list.insert(gui.END, "All weeks")
    for week in range(1, 18):
        week_list.insert(gui.END, str(week))

    site_frame = gui.Frame(bottom)
    site_label = gui.Label(site_frame, text = "Select site(s)")
    site_list = gui.Listbox(site_frame, width = 15, height = 10,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
    for site in ["All sites", "home", "away"]:
        site_list.insert(gui.END, site)

    cum_var = gui.IntVar()
    cum_button = gui.Checkbutton(selector, text="Show Cumulative Stats", 
                                 variable=cum_var)

    rate_var = gui.IntVar()
    rate_button = gui.Checkbutton(selector, text="Show Rate Stats",
                                  variable=rate_var)

    player_frame = gui.Frame(info)
    player_info = gui.Listbox(player_frame, width = 70, height = 20,
                              font = ["courier new", 14])
    player_info.insert(gui.END, "Player stats")

    button1 = gui.Button(selector, text = 'Get Game Stats', width = 40,
        command = lambda: get_results(team_list, year_list, week_list, site_list,
                                      cum_var, rate_var, display_text, status))

    player_button = gui.Button(app, text = 'Get Player Stats', width = 40,
                               command = lambda: game_stats(display_text,
                                                            status, player_info))

    display_text.pack()
    player_button.pack()
    info.pack()
    selector.pack(side = gui.LEFT)
    bottom.pack()
    team_frame.pack(side = gui.LEFT)
    team_label.pack()
    team_list.pack()
    year_frame.pack(side = gui.LEFT)
    year_label.pack()
    year_list.pack()
    week_frame.pack(side = gui.LEFT)
    week_label.pack()
    week_list.pack()
    site_frame.pack(side = gui.LEFT)
    site_label.pack()
    site_list.pack()
    cum_button.pack()
    rate_button.pack()
    button1.pack()
    player_frame.pack(side = gui.LEFT)
    player_info.pack()

    app.mainloop()

if __name__ == '__main__':
    runGUI()
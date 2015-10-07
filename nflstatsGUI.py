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

def get_results(team_list, year_list, week, site, cum, rate, widget):
    teams_index = map(int, team_list.curselection())
    teams = [TEAMS[index] for index in teams_index]
    if "All teams" in teams:
        thisteam = parse_seq(None, [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    else:
        team_str = ','.join(teams)
        thisteam = parse_seq(team_str, [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    if week.get() == "All weeks":
        thisweek = parse_seq(None, list(range(1, 18)), list(range(1, 18)))
    else:
        thisweek = parse_seq(week.get(), list(range(1, 18)),
                             list(range(1, 18)))
    year_index = map(int, year_list.curselection())
    years = [str(YEARS[index]) for index in year_index]
    if "All years" in years:
        thisyear = parse_seq(None, [2013, 2014], list(range(2009, 2016)))
    else:
        year_str = ','.join(years)
        thisyear = parse_seq(year_str, [2013, 2014], list(range(2009, 2016)))
    if site.get() == "All sites":
        thissite = parse_seq(None, ['home', 'away'], ['home', 'away'], False)
    else:
        thissite = parse_seq(site.get(), ['home', 'away'],
                             ['home', 'away'], False)
    league = League(thisyear, thisweek, thisteam, thissite, cum.get(), rate.get())
    league.compile()
    widget.delete(0, gui.END)
    for line in str(league).splitlines():
        widget.insert(gui.END, str(line))


def runGUI():
    app = gui.Tk()
    app.title("NFL Team Stats Query")
    app.geometry("1300x800+10+10")

    display_text = gui.Listbox(app, width = 200, height = 20,
                               font = ["courier new", 14])
    display_text.insert(gui.END, "Select parameters below.")
    display_text.pack()

    bottom = gui.Frame(app)
    bottom.pack()
    
    # team_var = gui.StringVar()
    # team_var.set("All teams")
    # team_entry = gui.Entry(bottom, textvariable = team_var)
    # team_entry.pack(side = gui.LEFT)
    team_frame = gui.Frame(bottom)
    team_frame.pack(side = gui.LEFT)
    team_label = gui.Label(team_frame, text = "Select team(s)")
    team_label.pack()
    team_list = gui.Listbox(team_frame, width = 40, height = 20,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
                            # exportselection = 0 allows for multiple listboxes
    team_list.insert(gui.END, "All teams")
    for team in ng.teams:
        team_list.insert(gui.END, team[3])
    team_list.pack()

    year_frame = gui.Frame(bottom)
    year_frame.pack(side = gui.LEFT)
    year_label = gui.Label(year_frame, text = "Select year(s)")
    year_label.pack()
    year_list = gui.Listbox(year_frame, width = 40, height = 20,
                            font = ["courier new", 14],
                            selectmode = gui.MULTIPLE,
                            exportselection = 0)
    year_list.insert(gui.END, "All years")
    for year in range(2009, 2016):
        year_list.insert(gui.END, str(year))
    year_list.pack()

    # year_var = gui.StringVar()
    # year_var.set("All years")
    # year_entry = gui.Entry(bottom, textvariable = year_var)
    # year_entry.pack(side = gui.LEFT)

    week_var = gui.StringVar()
    week_var.set("All weeks")
    week_entry = gui.Entry(bottom, textvariable = week_var)
    week_entry.pack(side = gui.LEFT)

    site_var = gui.StringVar()
    site_var.set("All sites")
    site_entry = gui.Entry(bottom, textvariable = site_var)
    site_entry.pack(side = gui.LEFT)

    cum_var = gui.IntVar()
    cum_button = gui.Checkbutton(bottom, text="Show Cumulative Stats", 
                                 variable=cum_var)
    cum_button.pack(side = gui.LEFT)

    rate_var = gui.IntVar()
    rate_button = gui.Checkbutton(bottom, text="Show Rate Stats",
                                  variable=rate_var)
    rate_button.pack(side = gui.LEFT)

    button1 = gui.Button(app, text = 'Get Stats', width = 40,
        command = lambda: get_results(team_list, year_list, week_var, site_var,
                                      cum_var, rate_var, display_text))
    button1.pack()

    app.mainloop()

if __name__ == '__main__':
    runGUI()
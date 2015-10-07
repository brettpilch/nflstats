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

def get_results(team, year, week, site, cum, rate, widget):
    if team.get() == "All teams":
        thisteam = parse_seq(None, [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    else:
        thisteam = parse_seq(team.get(), [team[0] for team in ng.teams],
                             [team[0] for team in ng.teams], False)
    if week.get() == "All weeks":
        thisweek = parse_seq(None, list(range(1, 18)), list(range(1, 18)))
    else:
        thisweek = parse_seq(week.get(), list(range(1, 18)),
                             list(range(1, 18)))
    if year.get() == "All years":
        thisyear = parse_seq(None, [2013, 2014], list(range(2009, 2015)))
    else:
        thisyear = parse_seq(year.get(), [2013, 2014], list(range(2009, 2015)))
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
    
    team_var = gui.StringVar()
    team_var.set("All teams")
    team_entry = gui.Entry(app, textvariable = team_var)
    team_entry.pack()

    year_var = gui.StringVar()
    year_var.set("All years")
    year_entry = gui.Entry(app, textvariable = year_var)
    year_entry.pack()

    week_var = gui.StringVar()
    week_var.set("All weeks")
    week_entry = gui.Entry(app, textvariable = week_var)
    week_entry.pack()

    site_var = gui.StringVar()
    site_var.set("All sites")
    site_entry = gui.Entry(app, textvariable = site_var)
    site_entry.pack()

    cum_var = gui.IntVar()
    cum_button = gui.Checkbutton(app, text="Show Cumulative Stats", 
                                 variable=cum_var)
    cum_button.pack()

    rate_var = gui.IntVar()
    rate_button = gui.Checkbutton(app, text="Show Rate Stats",
                                  variable=rate_var)
    rate_button.pack()

    button1 = gui.Button(app, text = 'Get Stats', width = 40,
        command = lambda: get_results(team_var, year_var, week_var, site_var,
                                      cum_var, rate_var, display_text))
    button1.pack()

    app.mainloop()

if __name__ == '__main__':
    runGUI()
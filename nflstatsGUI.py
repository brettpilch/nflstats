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

from nflstats import League, PASSING_STATS, RUSHING_STATS, RATE_STATS, default, parse_seq
import Tkinter as gui
import nflgame as ng

ALL_STATS = PASSING_STATS + RUSHING_STATS

def get_results(league, team, year, week, cum, rate, widget):
    if team.get() == "All teams":
        thisteam = ng.teams
    else:
        thisteam = default(parse_seq(team.get(), False), list(ng.teams))
    if week.get() == "All weeks":
        thisweek = default(parse_seq(None), list(range(1, 18)))
    else:
        thisweek = default(parse_seq(week.get()), list(range(1, 18)))
    if year.get() == "All years":
        thisyear = default(parse_seq(None), list(range(2009, 2015)))
    else:
        thisyear = default(parse_seq(year.get()), list(range(2009, 2015)))
    league.batch_init(thisyear, thisweek, thisteam, cum.get(), rate.get())
    league.compile()
    widget.delete(1.0, gui.END)
    widget.insert(gui.END, str(league))


def runGUI():
    league = League()
    app = gui.Tk()
    app.title("NFL Team Stats Query")
    app.geometry("1200x800+10+10")

    display_text = gui.Text(app, width=150)
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

    cum_var = gui.IntVar()
    cum_button = gui.Checkbutton(app, text="Show cumulative Stats", variable=cum_var)
    cum_button.pack()

    rate_var = gui.IntVar()
    rate_button = gui.Checkbutton(app, text="Show Rate Stats", variable=rate_var)
    rate_button.pack()

    button1 = gui.Button(app, text = 'Get Stats', width = 40,
        command = lambda: get_results(league, team_var, year_var, week_var, cum_var, rate_var, display_text))
    button1.pack()

    app.mainloop()

if __name__ == '__main__':
    runGUI()
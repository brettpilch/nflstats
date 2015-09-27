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

from nflstats import League, PASSING_STATS, RUSHING_STATS, RATE_STATS, weeklist, parse_seq
import Tkinter as gui
import nflgame as ng

ALL_STATS = PASSING_STATS + RUSHING_STATS

def get_results(league, team, year, week, cum, rate, widget):
    if team.get() == "All teams":
        thisteam = None
    else:
        thisteam = [team.get()]
    if week.get() == "All weeks":
        thisweek = parse_seq(None)
    else:
        thisweek = parse_seq(week.get())
    league.batch_init(year.get(), weeklist(thisweek), thisteam, cum.get(), rate.get())
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
    
    team_str = gui.StringVar()
    team_str.set("All teams")
    teams = ["All teams"] + [team[0] for team in ng.teams]
    team_drop_down = gui.OptionMenu(app, team_str, *teams)
    team_drop_down.pack()

    year_var = gui.IntVar()
    year_var.set(2014)
    years = list(range(2009, 2016))
    year_drop_down = gui.OptionMenu(app, year_var, *years)
    year_drop_down.pack()

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
        command = lambda: get_results(league, team_str, year_var, week_var, cum_var, rate_var, display_text))
    button1.pack()

    app.mainloop()

if __name__ == '__main__':
    runGUI()
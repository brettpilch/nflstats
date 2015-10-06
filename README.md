# NFL Stats Query

Query the NFL.com database to get weekly team-level stats for a given team(s) in a given season and week(s).

-----------------------------------------------------------------------------

## DEPENDENCIES

python 2.7  
nflgame (pip install nflgame) or [view repo](https://github.com/BurntSushi/nflgame)  

-----------------------------------------------------------------------------

## SCRIPTS

### nflstats.py  
- Call this script from the command-line to get all the weekly stats for every team in 2013 and 2014. Supply optional year, week, and team arguments to only show certain years, weeks, or teams. Use the 'site' argument to select only home or away games. The result is a display of standard passing and rushing stats along with the opponent's stats and the score for each game. Advanced usage allows you to display cumulative stats and rate stats instead of single-game totals.  

### nflstatsGUI.py  
- Run this script to open up a GUI interface in which you can select a year, team, and weeks to get stats from. The result is a display of standard passing and rushing stats along with the opponent's stats and the score for each game. Check the 'show cumulative stats' and 'show rate stats' buttons to show cumulative and rate stats.  

-----------------------------------------------------------------------------

## COMMAND-LINE DOCUMENTATION  

usage: nflstats.py [-h] [-y YEAR] [-w WEEK] [-t TEAM] [-s SITE] [-c] [-r]

Display NFL team stats for a given season, teams and weeks

###optional arguments  
  *-h, --help*            show this help message and exit
  *-y YEAR, --year YEAR*  Which year(s) do you want stats from? Acceptable years are between 2009 and 2015. Use '2009,2011-2013,...' for multiple years. Default value is 2013-2014  
  *-w WEEK, --week WEEK*  Which week(s) do you want to include? Acceptable weeks are between 1 and 17. Use '1-5,7,...' for multiple weeks. Defaults to include all weeks.  
  *-t TEAM, --team TEAM*  Which team(s) do you want to include? Accepts any of the common 2-3 letter abbreviations. Use 'IND,NE,...' for multiple teams. Defaults to include all teams.  
  *-s SITE, --site SITE*  Which sites do you want to include? Acceptable values are 'home' and 'away'. Defaults to include both sites  
  *-c, --cum*             Flag to show cumulative stats instead of single-game
                        stats.  
  *-r, --rate*            Flag to show rate stats instead of gross stats.  

-----------------------------------------------------------------------------

## COMMAND-LINE EXAMPLES  

$ python nflstats.py -h
- displays the help file (documentation for the command-line arguments).

$ python nflstats.py -y 2014 -s home
- displays all the weekly stats for every team for every week of the 2014 season when they played at home.

$ python nflstats.py -y 2013 -w 5 -t IND -r
- displays the Indianapolis Colts rate stats in 2013 week 5.

$ python nflstats.py -y 2010,2012-2014 -w 3,5-9,13 -cr
- displays cumulative rate stats for all teams in 2010, 2012, 2013, and 2014 for weeks 3, 5-9, and 13.
- use commas to select multiple years or weeks.
- use hyphens to include a range of consecutive years or weeks.

$ python nflstats.py -y 2011 -t TB,NYG
- displays stats for Tampa Bay, and New York Giants for all of 2011.
- use commas to separate team names
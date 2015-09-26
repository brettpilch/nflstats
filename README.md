# NFL Stats Query

Query the NFL.com database to get weekly team-level stats for a given team(s) in a given season and week(s). Call this script from the command-line with a year argument to get all the weekly stats for every team in that year. Supply optional week and team arguments to only show certain weeks or teams. The result is a display of standard passing and rushing stats along with the opponent's stats and the score for each game. Advanced usage allows you to display cumulative stats and rate stats instead of single-game totals.

-----------------------------------------------------------------------------

## DEPENDENCIES

python 2.7  
nflgame (pip install nflgame) or [view repo](https://github.com/BurntSushi/nflgame)  

-----------------------------------------------------------------------------

## COMMAND-LINE DOCUMENTATION

usage: nflstats.py [-h] [-w WEEK] [-t TEAM] [-c] [-r] {2009,2010,2011,2012,2013,2014,2015}

display NFL team stats for a given season, teams, and weeks

### positional arguments  
  {2009,2010,2011,2012,2013,2014,2015}  
- which year do you want stats from?

### optional arguments  
  -h, --help  
- show this help message and exit  
  -w WEEK, --week WEEK
- Which week(s) do you want to include?    
- Use '1-5,7,...' for multiple weeks.  
- Omit this argument to include all weeks.  
  -t TEAM, --team TEAM  
- Which team(s) do you want to include?  
- Use 'IND,NE,...' for multiple teams.  
- Omit this argument to include all teams.  
  -c, --cum  
- Flag to show cumulative stats instead of single-game stats.  
  -r, --rate  
- Flag to show rate stats instead of gross stats.  

(The only required argument is the year, which must be between 2009 and 2015.)  

-----------------------------------------------------------------------------

## COMMAND-LINE EXAMPLES:
$ python -h  
- displays the help file (documentation for the command-line arguments).

$ python nflstats.py 2014  
- displays all the weekly stats for every team for every week of the 2014 season.

$ python nflstats.py 2013 -w 5 -t IND  
- displays the Indianapolis Colts team stats in 2013 week 5.

$ python nflstats.py 2012 -w 3,5-9,13 -r
- displays rate stats for all teams in 2012 weeks 3, 5-9, and 13.  
- use commas to select multiple weeks.  
- use hyphens to include a range of consecutive weeks.

$ python nflstats.py 2011 -t TB,NYG,CAR -cr
- displays cumulative rate stats for Tampa Bay, New York Giants, and Carolina for all of 2011. 
- use commas to separate team names
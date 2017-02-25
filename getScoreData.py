import requests
from bs4 import BeautifulSoup

LEAGUEID = 29743

baseURL = 'http://games.espn.com/ffl/scoreboard?leagueId=LEAGUEID& \
seasonId=SEASONID&scoringPeriodId=SCORINGPERIOD'




def main():
    # blast off
    print(baseURL)

if __name__ == '__main__':
    main()

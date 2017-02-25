import requests
import json
from bs4 import BeautifulSoup
import numpy

YEARS = list(range(2008, 2017)) # TODO 2017

LEAGUEID = '29743'

baseURL = 'http://games.espn.com/ffl/tools/finalstandings?leagueId=LEAGUEID&seasonId=SEASONID'
baseURL = baseURL.replace('LEAGUEID', LEAGUEID)
RANKIDX = 0
PLAYERIDX = 2
RECORDIDX = 4
PFIDX = 5
PAIDX = 6


DIR = '/Users/ezra/Documents/GitHub/FFData/'

def fixPlayerName(player_name):
    # some names are slightly off, or can be corrected
    # Alex added a second user that was also him after he forgot his password
    if 'Alexander' in player_name:
        player_name = 'Alexander Shipp' 
    
    # Robby's name is Julius Ceasar on ESPN
    if 'Julius Ceasar' in player_name:
        player_name = player_name.replace('Julius Ceasar', 'Robby Kirk')
            
    # Josh's name is J M
    if 'J M' in player_name:
        player_name = 'Josh McCafferty, Isaac Goldenthal'
        
    if 'Friedman' in player_name:
        player_name = 'Ben Friedman'
    
    if ',' in player_name:
        player_name = player_name.replace(',', '|')
    
    return player_name
            

def getPlayers():

    players = set()
    
    for y in YEARS:
        rows = getRows(y)
        idx = 3
        
        while idx < len(rows):
            columns = rows[idx].find_all('td')
            player_name = columns[PLAYERIDX].text
            
            player_name = fixPlayerName(player_name)
            players.add(player_name)
        
            idx = idx + 1
        
    return list(players)
    
def getRows(y):
    year = str(y)
    url = baseURL.replace('SEASONID', year)
    r = requests.get(url)
        
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('tr')
    return rows
        
    
def getGamePlus(players):
    # Get the plus minus of each player for every season
    NaList = ['NA']*len(YEARS)
    GPL = [NaList]*len(players)
    GamePlusList = numpy.matrix(GPL)
    for y in YEARS:
        rows = getRows(y)
        idx = 3
        
        while idx < len(rows):
            columns = rows[idx].find_all('td')
            record = columns[RECORDIDX].text
            splits = record.split('-')
            gamePlus = int(splits[0]) - int(splits[1])
            player_name = columns[PLAYERIDX].text
            player_name = fixPlayerName(player_name)
            
            pidx = players.index(player_name)
            GamePlusList[pidx][y-YEARS[0]] = gamePlus

            idx = idx + 1
    return GamePlusList


def getStats(players, statIDX):
    # Get the plus minus of each player for every season
    NaList = ['NANANANANANANANANANANANANANANANANANANANANANA']*(len(YEARS)+1) # max out space
    LoL = [NaList]*(len(players)+1)
    OutputMatrix = numpy.array(LoL)
    
    idx = 1
    while idx < len(players)+1:
        OutputMatrix[idx][0] = players[idx-1]
        idx = idx + 1
    
    OutputMatrix[0][0] = 'Owner(s)'
    
    idx = 1
    
    while idx < len(YEARS)+1:
        OutputMatrix[0][idx] = str(YEARS[idx-1])
        idx = idx + 1
    
    for y in YEARS:
        rows = getRows(y)
        idx = 3
        
        while idx < len(rows):
            columns = rows[idx].find_all('td')
            stat = getStat(columns, statIDX)
            player_name = columns[PLAYERIDX].text
            player_name = fixPlayerName(player_name)
            
            pidx = players.index(player_name)
            OutputMatrix[pidx+1][y-YEARS[0]+1] = stat

            idx = idx + 1
    OutputMatrix[OutputMatrix == 'NANANANANANANANANANANANANANANANANANANANANANA'] = 'NA'
    return OutputMatrix            

def getStat(columns, statIDX):
    
    if statIDX == RANKIDX:
        return int(columns[statIDX].text)
    elif statIDX == PLAYERIDX:
        return fixPlayerName(columns[statIDX].text)
    elif statIDX == RECORDIDX:
        record = columns[RECORDIDX].text
        splits = record.split('-')
        return int(splits[0]) - int(splits[1])
    elif statIDX == PFIDX:
        return float(columns[PFIDX].text)
    elif statIDX == PAIDX:
        return float(columns[PAIDX].text)
    else:
       return 'NA'
              
    
def getResults(players):
    for y in YEARS:
        rows = getRows(y)
        idx = 3
        
        while idx < len(rows):
            columns = rows[idx].find_all('td')
            rank = int(columns[0].text)
            player_name = columns[2].text
            record = columns[4].text
            points_for = float(columns[5].text)
            points_against = float(columns[6].text)
            
            
            players[player_name].recorddict.append(year +': '+ record)
            players[player_name].PFdict[year] = points_for
            players[player_name].PAdict[year] = points_against
            
            idx = idx + 1
            
    f = open(DIR+'record_dict.txt', 'w')
                
    for p in players:
        f.write('\n'+p)
        f.write(str(players[p].recorddict))
        #f.write(str(sorted(players[p].PFdict.items())))
        #f.write(str(sorted(players[p].PAdict.items())))
    f.close()
     

def main():
    # blast off
    players = getPlayers()
    GPL = getStats(players, RECORDIDX)
    PF = getStats(players, PFIDX)
    PA = getStats(players, PAIDX)
    Rank = getStats(players, RANKIDX)
    
    print(players)
    numpy.savetxt('games_above.csv', GPL, delimiter=',', newline='\n', fmt='%s')
    numpy.savetxt('points_for.csv', PF, delimiter=',', newline='\n', fmt='%s')
    numpy.savetxt('points_against.csv', PA, delimiter=',', newline='\n', fmt='%s')
    numpy.savetxt('rank.csv', Rank, delimiter=',', newline='\n', fmt='%s')
    

if __name__ == '__main__':
    main()

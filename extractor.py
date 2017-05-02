# Python 3.6.0 |Anaconda 4.3.1 (64-bit)|

from importer import pd, bs, os, re
from loader import from_url_to_bs4


def get_fixture_links_for_league(bs4, league):

    '''
    Returns a list of fixture links for given league from bs4 object
    
    '''
    links = []
    fixture_link_prefix = 'https://uk.sports.yahoo.com'
    
    part_league_link = '/football/' + league

    for tag in bs4.findAll('a', href=True):
        if (part_league_link in tag['href']) & ('yahoo.com' not in tag['href']):
            links.append(fixture_link_prefix + tag['href'])

    return links



def get_all_fixture_links_for_league(league, number_of_weeks = None):
    
    """
    Returns dictionary with all links for a given league
    
    Attributes:
        league (str): league available in uk.sports.yahoo.com/football, i.e. "premier-league"
        number_of_weeks (int) : number of weeks for a league, default value is 38
    """
    
    if number_of_weeks == None:
        weeks = 38
    else:
        weeks = number_of_weeks
        
    league_link = 'https://uk.sports.yahoo.com/football/' + league + '/fixtures/?schedState=2&dateRange='
    league_fixtures_dict = {}
    
    for week in range(1, weeks + 1): 

        html = from_url_to_bs4(league_link + str(week))
        league_fixtures_dict[week] = get_fixture_links_for_league(html, league)
        
    return league_fixtures_dict



def get_player_name(player_string):
    
    """
    Returns player name from bs4 string
    """
    
    name = re.search("title=\"(\w+. \w+)(.*)", player_string)
    
    return name.group(1)
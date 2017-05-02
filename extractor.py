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



def get_stats_for_player(player_string):
    
    """
    Returns player statistics from bs4 string
    """
    
    stats = re.findall(">(\d*)<", player_string)
    stats_list = [stat for stat in stats if stat != ""]
    
    return stats_list



def get_players_by_position(html, position, is_away = None):
    
    """
    Returns a dictionary with players stats in a format dict = {position: {player: [stats]}}, 
    given bs4 object and position
    
    Attributess:
        html(bs4): beautifulsoup object representing html
        position(str): player's position
                       values: forwards, midfielders, defenders, goalkeeper, substitutes
    """
    
    stats_dict = {}
    splitter = "href=\"/football/players"    
    
    if is_away == None:
        away = False
    else:
        away = True
    
    if position == "forwards":
        players_str = re.search("Forwards(.*?)>Midfielders", str(html)).group(1)
    elif position == "midfielders":
        players_str = re.search("Midfielders(.*?)>Defenders", str(html)).group(1)
    elif position == "defenders":
        players_str = re.search("Defenders(.*?)Goalkeepers", str(html)).group(1)
    elif position == 'goalkeepers':
        players_str = re.search("Goalkeepers(.*?)>Substitutes", str(html)).group(1)
    elif position == 'substitutes':
        if away == True:
            players_str = re.search("Substitutes(.*?)html", str(html)).group(1)
        else:
            players_str = re.search("Substitutes(.*?)>Forwards", str(html)).group(1)
    else:
        raise NameError("Typo in position variable")
        
    players = str(players_str).split(splitter)[1:]
    
    for player in players:
        player_name = get_player_name(player)
        player_stats = get_stats_for_player(player)
        
        stats_dict[player_name] = player_stats
        
    return stats_dict



def get_away_part_html(html):
    
    """
    Returns a part of htmt that represents away team as a string
    """
    
    html_splitter = "-->Substitutes<!-- /react-text --></th>"
    split_point = str(html).find(html_splitter)

    home_html = str(html)[:split_point]
    away_html = str(html)[split_point + len("-->Substitutes<!"):]
    
    return away_html



def get_fixture_stats_dict(html):
    
    """
    Returns a dictionary with all players statistics given bs4 object.
    Dictionary does not have stats keys, but ordered the same way as it is on the website.
    """

    away_html = get_away_part_html(html)

    fixture_stats_dict = {}
    home_stats_dict = {}
    away_stats_dict = {}

    positions = ['forwards', 'midfielders', 'defenders', 'goalkeepers', 'substitutes']
    fields = ['home', 'away']

    for field in fields:
        for position in positions:
            if field == 'home':
                home_stats_dict[position] = get_players_by_position(html, position)
            else:
                if position == 'substitutes':
                    #away_stats.append(get_players_by_position(away_html, position, is_away = True))
                    away_stats_dict[position] = get_players_by_position(away_html, position, is_away = True)
                else:
                    #away_stats.append(get_players_by_position(away_html, position))
                    away_stats_dict[position] = get_players_by_position(away_html, position)

    fixture_stats_dict['home'] = home_stats_dict
    fixture_stats_dict['away'] = away_stats_dict

    return fixture_stats_dict
# Python 3.6.0 |Anaconda 4.3.1 (64-bit)|

from importer import pd, bs, os, re
from loader import from_url_to_bs4


def get_kick_off(html):
    
    """
    Returns kick-off date of fixture, given bs4 object
    """
    
    pattern = "(.*?)\| (\d\d\d\d-\d\d-\d\d) \|(.*?)"
    date = re.search(pattern, str(html)).group(2)
    
    return date



def get_attendance(html):
    
    """
    Returns attendance for fixture, given bs4 object
    """
    
    pattern = '\"attendance\":\"(\d*)\"'
    attendance = re.search(pattern, str(html)).group(1)
    
    return attendance



def is_fixture_nil_nil(html):
    
    """
    Returns True if a fixture ends with 0-0 score otherwise False, given bs4 object
    """
    
    number_of_goals =  str(html).find('Goal!')

    if number_of_goals > 0:
        return False
    else:
        return True



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
                    away_stats_dict[position] = get_players_by_position(away_html, position, is_away = True)
                else:
                    away_stats_dict[position] = get_players_by_position(away_html, position)

    fixture_stats_dict['home'] = home_stats_dict
    fixture_stats_dict['away'] = away_stats_dict

    return fixture_stats_dict



def get_shirts(html):
    
    """
    Returns a dict with players' shirt number, given bs4
    Format {player : 'shirt'}
    """

    divs = html.find_all('div', class_ = 'D(ib)')
    text = []

    for div in divs:
        text.append(div.get_text())

    pattern = "#(\d+)(.*)"
    players_dict = {}

    for string in text:

        match = re.search(pattern, string)
        if match:
            shirt = match.group(1)
            player = match.group(2).strip()
            players_dict[player] = shirt
            
    return players_dict



def get_goal_info(scoring_summary, kickoff):
    
    """
    Returns a tuple with a goal info, given scoring summary string.
    Tuple format (team, scorer, minute)
    """

    pattern = "(\d{1,2})\'(.*?)\. (.*?) \((.*?)\)"

    minute = re.search(pattern, scoring_summary).group(1)
    scorer = re.search(pattern, scoring_summary).group(3)
    team = re.search(pattern, scoring_summary).group(4)
    
    return (team, scorer, minute, kickoff)



def get_goals_info_list(html):
    
    """
    Returns a list of tuples with a all goals for fixture, given bs4 object.
    """

    scoring_summary = re.search("Scoring Summary(.*?)>Forwards", str(html)).group(1)

    exit = True
    goals = []
    
    kickoff = get_kick_off(html)

    while exit:
        try:
            goal_info = get_goal_info(scoring_summary, kickoff)
            
            # remove
            print (goal_info)
            
            goals.append(goal_info)
            first_player_index = scoring_summary.find(goal_info[1]) + 1
            scoring_summary = scoring_summary[first_player_index:]
        except AttributeError:
            exit = False
            break
            
    return goals
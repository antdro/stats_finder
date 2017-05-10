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
    number_of_own_goals = str(html).find("Own Goal by")

    if number_of_goals > 0:
        return False
    else:
        if number_of_own_goals > 0:
            return False
        else:
            try:
                injury_time_goal_pattern = "(\d{1,2})\+(\d{1,2})\'(.*?)Goal (.*?)<(.*?)"
                minute = re.search(injury_time_goal_pattern, str(html)).group(1)
                return False
            except AttributeError:
                return True
    
    
    
def get_teams(html):
    
    """
    Returns tuple with home and away team names given bs4 object.
    tuple[0] - home team
    tuple[1] - away team
    """
    pattern = "pageData\":{\"title\":\"(.*?) vs (.*?) \| \d\d\d\d-\d\d-\d\d \|"

    away_team = re.search(pattern, str(html)).group(2)
    home_team = re.search(pattern, str(html)).group(1)
    
    return (home_team, away_team)    



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



def get_all_fixture_links_for_league(league, current_week, weeks):
    
    """
    Returns dictionary with all links for a given league
    
    Attributes:
        league (str): league available on uk.sports.yahoo.com/football, i.e. "premier-league"
        current_week: latest week to collect data for
        weeks (int) : number of recent weeks to collect data for
    """
        
    league_link = 'https://uk.sports.yahoo.com/football/' + league + '/fixtures/?schedState=2&dateRange='
    league_fixtures_dict = {}
    
    start_week = current_week - weeks + 1
    
    for week in range(start_week, current_week + 1): 

        html = from_url_to_bs4(league_link + str(week))
        league_fixtures_dict[week] = get_fixture_links_for_league(html, league)
        
    return league_fixtures_dict



def get_player_name(player_string):
    
    """
    Returns player name from bs4 string
    """
    
    name = re.search("title=\"(.*?)\"\>\<(.*)", player_string).group(1)
    
    return name



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



def validate_fixture_stats_dict(d):

    """
    Remove data list if its size doesn't match required format.
    Returns updated dictionary 
    """
    
    dict_checked = {}

    for field in d.keys():

        dict_checked[field] = {}
        for role in d[field]:

            dict_checked[field][role] = {}
            for player in d[field][role]:

                if (role == "substitutes") & (len(d[field][role][player]) == 7):
                    dict_checked[field][role][player] = d[field][role][player]

                if (role == "forwards") & (len(d[field][role][player]) == 12):
                    dict_checked[field][role][player] = d[field][role][player]

                if (role == "defenders") & (len(d[field][role][player]) == 12):
                    dict_checked[field][role][player] = d[field][role][player]

                if (role == "midfielders") & (len(d[field][role][player]) == 12):
                    dict_checked[field][role][player] = d[field][role][player]

                if (role == "goalkeepers") & (len(d[field][role][player]) == 10):
                    dict_checked[field][role][player] = d[field][role][player]
    
    return dict_checked



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



def collect_stats_for_fixture(d, html):

    """
    Returns df with stats for all players for fixture
    """

    fixture = pd.DataFrame()

    stats_per_position = {
        'substitutes' : ['G','FC','FS','Y','R','PEN','MINS'],
        'goalkeepers' : ['G','SAV','GC','GK','FC','FS','Y','R','PEN','MINS'],
        'defenders'   : ['G','GA','S','TA','CLR','COR','FC','FS','Y','R','PEN','MINS'],
        'midfielders' : ['G','GA','S','PAS','FK','COR','FC','FS','Y','R','PEN','MINS'],
        'forwards'    : ['G','GA','S','PAS','FK','COR','FC','FS','Y','R','PEN','MINS']
    }
    
    home,away = get_teams(html)
    teams = {
        "home" : home,
        "away" : away
    }
    
    for field in d:

        subs_df = pd.DataFrame(d[field]['substitutes']).T
        subs_df.columns = stats_per_position['substitutes']

        goal_df = pd.DataFrame(d[field]['goalkeepers']).T
        goal_df.columns = stats_per_position['goalkeepers']

        def_df = pd.DataFrame(d[field]['defenders']).T
        def_df.columns = stats_per_position['defenders']

        mid_df = pd.DataFrame(d[field]['midfielders']).T
        mid_df.columns = stats_per_position['midfielders']

        forw_df = pd.DataFrame(d[field]['forwards']).T
        forw_df.columns = stats_per_position['forwards']

        df = pd.concat([subs_df, goal_df, def_df, mid_df, forw_df])
        df.drop_duplicates(inplace = True)
        df = df.reset_index()
        df.rename(columns = {"index": "player"}, inplace = True)
        df = df.fillna(0)
        df = df[df.MINS != '0']

        n_rows = df.shape[0]
        df['team'] = [teams[field]] * n_rows
        df['field'] = [field] * n_rows

        fixture = pd.concat([fixture, df])

    kickoff = get_kick_off(html)
    attendance = get_attendance(html)
    n_rows = fixture.shape[0]
    fixture['kickoff'] = [kickoff] * n_rows
    fixture['attendance'] = [attendance] * n_rows

    return fixture

    

def get_goal_info(scoring_summary, html):
    
    """
    Returns a tuple with a goal info, given scoring summary string.
    """
        
    kickoff = get_kick_off(html)
    
    own_goal = scoring_summary.find("Own Goal by")
    goal = scoring_summary.find("Goal!")
    
    if own_goal < goal:
        try:
            own_goal_pattern = "(\d{1,2})\'(.*?)Own Goal by (.*?)\, (.*?)\."
            minute = re.search(own_goal_pattern, scoring_summary).group(1)
            scorer = re.search(own_goal_pattern, scoring_summary).group(3)
            team = re.search(own_goal_pattern, scoring_summary).group(4)
            goal = "Own Goal"
        except AttributeError:
            try:
                goal_pattern = "(\d{1,2})\'(.*?)Goal!(.*?)\.(.*?) \((.*?)\)"
                minute = re.search(goal_pattern, scoring_summary).group(1)
                scorer = re.search(goal_pattern, scoring_summary).group(4).strip()
                team = re.search(goal_pattern, scoring_summary).group(5)
                goal = "Goal"
            except AttributeError:
                injury_time_goal_pattern = "(\d{1,2})\+(\d{1,2})\'(.*?)Goal (.*?)<(.*?)"
                minute = re.search(injury_time_goal_pattern, scoring_summary).group(1)
                scorer = re.search(injury_time_goal_pattern, scoring_summary).group(4)
                team = 'NaN'
                goal = "Goal"
    else:        
        try:
            goal_pattern = "(\d{1,2})\'(.*?)Goal!(.*?)\.(.*?) \((.*?)\)"
            minute = re.search(goal_pattern, scoring_summary).group(1)
            scorer = re.search(goal_pattern, scoring_summary).group(4).strip()
            team = re.search(goal_pattern, scoring_summary).group(5)
            goal = "Goal"
        except AttributeError:
            try:
                own_goal_pattern = "(\d{1,2})\'(.*?)Own Goal by (.*?)\, (.*?)\."
                minute = re.search(own_goal_pattern, scoring_summary).group(1)
                scorer = re.search(own_goal_pattern, scoring_summary).group(3)
                team = re.search(own_goal_pattern, scoring_summary).group(4)
                goal = "Own Goal"
            except AttributeError:
                injury_time_goal_pattern = "(\d{1,2})\+(\d{1,2})\'(.*?)Goal (.*?)<(.*?)"
                minute = re.search(injury_time_goal_pattern, scoring_summary).group(1)
                scorer = re.search(injury_time_goal_pattern, scoring_summary).group(4)
                team = 'NaN'
                goal = "Own Goal"
                
    home = get_teams(html)[0]
    away = get_teams(html)[1]
    
    if team != "NaN":
        opponent = list(set([home, away]) - set([team]))[0]
    else:
        opponent = "NaN"
                    
    return [team, scorer, minute, kickoff, opponent, goal]



def get_goals_for_fixture_list(html):
    
    """
    Returns a list of tuples with all goals for fixture, given bs4 object.
    """
    
    scoring_summary = re.search("Scoring Summary(.*?)>Forwards", str(html)).group(1)
    
    exit = True
    goals = []

    while exit:
        try:
            goal_info = get_goal_info(scoring_summary, html)
            
            print (goal_info) # progress tracking
            
            goals.append(goal_info)
            first_player_index = scoring_summary.find(goal_info[1]) + 1
            scoring_summary = scoring_summary[first_player_index:]
        
        except AttributeError:
            exit = False
            break
            
    return goals



def update_missing_goals(html, goals_list):
    
    """
    Returns goals' list updated with missing goals, given bs4 and initial goals_list
    Format for missing goal tuple ("NaN", "NaN", minute, kickoff)
    """
    
    scoring_summary = re.search("Scoring Summary(.*?)>Forwards", str(html)).group(1)

    pattern = "(\>\d{1,2}\'|\>\d{1,2}\<)"
    minutes_list = re.findall(pattern, scoring_summary)
    minutes_check_list = [minute.replace(">", "").replace("\'", "").replace("<", "") for minute in minutes_list]

    minutes_in_goals_list = [list_[2] for list_ in goals_list]
    missing_minutes = list(set(minutes_check_list) - set(minutes_in_goals_list))
    
    kickoff = goals_list[0][3]
    
    for minute in missing_minutes:
        
        missing_goal = ["NaN", "NaN", minute, kickoff, "NaN", "Nan"]
        goals_list.append(missing_goal)
        
    return goals_list



def get_goals_for_league_df(links):
    
    """
    Returns df with all goals info for the league given a list of links
    """
    
    goals_df = pd.DataFrame()

    for week in links:

        print (week)  # progress tracking

        for fixture_link in links[week]:
            
            print (fixture_link) # progress tracking
            html = from_url_to_bs4(fixture_link)

            if is_fixture_nil_nil(html):

                print ("0-0 score") # progress tracking
                continue
            else:
                goals_list = get_goals_for_fixture_list(html)

            # check if minutes are missing
            goals_list = update_missing_goals(html, goals_list)

            # update df
            df_temp = pd.DataFrame(goals_list, columns = ["team", "player", "minute", "kickoff", "opponent", "goal"])
            df_temp["week"] = [week] * df_temp.shape[0]

            goals_df = pd.concat([goals_df, df_temp]) 

    goals_df = goals_df[["week", "kickoff", "team", "player", "minute", "opponent", "goal"]]
    goals_df.reset_index(drop = True, inplace = True)
    
    return goals_df



def collect_goals(leagues):
    
    """
    Collects goals for leagues passed and saves them as csv files for each league
    """
    
    for league in leagues:

        league_name = league[0]
        current_week = league[1]
        weeks = league[2]

        print ('\n' + league_name + '\n')

        links = get_all_fixture_links_for_league(league_name, current_week, weeks)
        links = encode_all_non_ascii_urls(links)

        df = get_goals_for_league_df(links)

        df.to_csv("data/" + league_name + ".csv")

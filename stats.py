# Python 3.6.0 |Anaconda 4.3.1 (64-bit)|

import pandas as pd


def get_team_goals(df, team):
    
    """
    Given df and team name, returns number of goals scored by a team
    """
    
    goals_df = df[(df.team == team) & (df.goal != "Own Goal")]
    owns_by_opponent_df = df[(df.opponent == team) & (df.goal == "Own Goal")]
    
    team_goals = goals_df.shape[0] + owns_by_opponent_df.shape[0]

    return team_goals

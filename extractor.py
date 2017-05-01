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



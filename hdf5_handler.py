from importer import h5py, pd, HDFStore
from extractor import *
from loader import *
from helper import *


def create_football_h5():
    
    """
    Given a dict with leagues, create and return hdf5 file
    """
    
    h5 = h5py.File('db.h5', 'w')
    football = h5.create_group('football')
    h5.close()
            
    return h5

        
        
def add_league_to_football_h5(leagues):    
    
    """
    Adds leagues from {country: league} dict to football h5 file; returns updated h5
    """
    
    h5 = h5py.File('db.h5', 'r+')
    
    football = h5['football']
    
    for country in leagues.keys():
        for league in leagues[country]:
            football.create_group(country + '/' + league)
    
    h5.close()
    
    return h5

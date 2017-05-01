# Python 3.6.0 |Anaconda 4.3.1 (64-bit)|

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import pandas as pd

from bs4 import BeautifulSoup as bs

from datetime import datetime, timedelta
from pandas import HDFStore

import os
import re

import h5py
from pandas import HDFStore

import warnings
warnings.filterwarnings('ignore',category=pd.io.pytables.PerformanceWarning)
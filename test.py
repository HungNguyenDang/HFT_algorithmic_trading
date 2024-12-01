# TEST GETTING DATA FROM MONGODB
import pandas as pd
from pymongo import MongoClient
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import tkinter as tk

from helpers import *

data_m15 = collection_from_mongodb('AUDUSD_M15')
print(data_m15.head())
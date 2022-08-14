import certifi
import pandas as pd
from pymongo import MongoClient
from lib.utils.config import settings

mongo = MongoClient(settings.mongo_uri, tlsCAFile=certifi.where())
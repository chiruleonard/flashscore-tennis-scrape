import pymongo
import json
from datetime import datetime

def mongodb_import(j_file, season, grand_slam, tour):
    # Open json file
    file = r'C:\Users\luntr\Desktop\python_venv_projects\flashscore_tennis\processed\\' + j_file +'.json'
    with open(file, 'r') as f:
        data = json.load(f)
        
    for i in data:
        i['date'] = datetime.strptime(i['date'], '%Y-%m-%dT%H:%M:%S')
        i['season'] = season
        i['tour'] = tour
        
    # connect to MongoDB
    client = pymongo.MongoClient("mongodb://192.168.1.100:27017/")
    db = client.tennisdb
    
    # Insert into TennisDB
    for i in data:    
        db[grand_slam].insert_one(i)
        
    return print("Import successfully")
	
#mongodb_import('ATP Wimbledon 2021', 2022, 'Australian Open', 'ATP Men')
mongodb_import('WTA Australian Open 2022', 2022, 'Australian Open', 'WTA Women')
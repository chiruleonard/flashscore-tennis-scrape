#!/usr/bin/env python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

import time
import re
import json
import os
import random
import datetime

# Create an empty list to store all match_ids
match_ids = []

# Path to where is stored match_ids
path = os.getcwd() + r'\prerequisite\json.txt'

# Open .txt file in read mode and create a list with all match_ids
with open(path, 'r') as match_ids_results:
    for line in match_ids_results.readlines():
        match_ids.append(line.strip())

# Create an empty list to store all dict matches
data_processed = []

# Create a dictionary to store each data
def data_function():
    global data
    data = {}

    data['match_id'] = None
    data['location'] = None
    data['tournament'] = None
    data['date'] = None
    data['round'] = None
    data['surface'] = None
    data['player_1'] = {'name':None,
                        'nationality': None,
                        'rankings':None}
    data['player_2'] = {'name':None,
                        'nationality': None,
                        'rankings':None}
    data['status'] = None
    data['EndTime'] = None
    data['score'] = {'fullTime':{
                        'player_1':None,
                        'player_2':None},
                     'sets':[]
                    }
    data['odds'] = {'player_1':None,
                    'player_2':None}
    data['match'] = {
        'player_1':{
            'Service':{
                'Aces': None,
                'Double Faults': None,
                '1st Serve Percentage': None,
                '1st Serve Points Won': None,
                '2nd Serve Points Won': None,
                'Break Points Saved': None},
            'Return':{
                '1st Return Points Won': None,
                '2nd Return Points Won': None,
                'Break Points Converted': None},
            'Points':{
                'Winners': None,
                'Unforced Errors': None,
                'Net Points Won': None,
                'Max Points In Row': None,
                'Service Points Won': None,
                'Return Points Won': None,
                'Total Points Won': None},
            'Games':{
                'Max Games In Row': None,
                'Service Games Won': None,
                'Return Games Won': None,
                'Total Games Won': None}
        },
        'player_2':{
            'Service':{
                'Aces': None,
                'Double Faults': None,
                '1st Serve Percentage': None,
                '1st Serve Points Won': None,
                '2nd Serve Points Won': None,
                'Break Points Saved': None},
            'Return':{
                '1st Return Points Won': None,
                '2nd Return Points Won': None,
                'Break Points Converted': None},
            'Points':{
                'Winners': None,
                'Unforced Errors': None,
                'Net Points Won': None,
                'Max Points In Row': None,
                'Service Points Won': None,
                'Return Points Won': None,
                'Total Points Won': None},
            'Games':{
                'Max Games In Row': None,
                'Service Games Won': None,
                'Return Games Won': None,
                'Total Games Won': None}
        }
    }
    return data

def match_summary():
    soup = BeautifulSoup(driver.page_source, features="lxml")

    # Store match_info data
    match_info = soup.find('span', attrs={'class': 'tournamentHeader__country'}).text

    # Location
    try:
        location = soup.find('div', attrs={'class':'mi__data'})
        data['location'] = location.text.split(": ")[1]
    except:
        pattern = "(\(.*\))"
        location = re.search(pattern, match_info).group(0)
        data['location'] = location.replace('(', '').replace(')', '')
    
    # Tournament
    pattern = "(:\s.*\()"
    tournament = re.search(pattern, match_info).group(0)
    data['tournament'] = tournament.replace(': ', '').replace(' (', '')
    
    # Surface
    try:
        pattern = "(,\s.*\s-)"
        surface = re.search(pattern, match_info).group(0)
        data['surface'] = surface.replace(', ', '').replace(' -', '')
    except:
        pass
    
    # Round
    data['round'] = match_info.split(' - ')[-1]
    
    # Date
    date_v = soup.find('div', attrs={'class':'duelParticipant__startTime'}).text
    data['date'] = datetime.datetime.strptime(date_v, '%d.%m.%Y %H:%M').isoformat()
    
    # Players
    try:
        p1 = soup.find_all('div', attrs={'class': 'participant__participantName participant__overflow'})[0].a['href']
        data['player_1']['name'] = p1.split('/')[2].replace('-',' ').title()
        
        p2 = soup.find_all('div', attrs={'class': 'participant__participantName participant__overflow'})[-1].a['href']
        data['player_2']['name'] = p2.split('/')[2].replace('-',' ').title()
    except:
        group_p1 = soup.find_all('div', attrs={'class': 'participant__participantNameWrapper'})[0].find_all('a')
        data['player_1']['name'] = group_p1[0]['href'].split('/')[2].replace('-',' ').title() + ' / ' + group_p1[-1]['href'].split('/')[2].replace('-',' ').title()
        
        group_p2 = soup.find_all('div', attrs={'class': 'participant__participantNameWrapper'})[-1].find_all('a')
        data['player_2']['name'] = group_p2[0]['href'].split('/')[2].replace('-',' ').title() + ' / ' + group_p2[-1]['href'].split('/')[2].replace('-',' ').title()

    # Rankings
    try:
        data['player_1']['rankings'] = soup.find_all('div', attrs={'class': 'participant__participantRank'})[0].text.replace('.','')
        data['player_2']['rankings'] = soup.find_all('div', attrs={'class': 'participant__participantRank'})[-1].text.replace('.','')
    except:
        pass

    # Nationality
    try:
        nat_v = soup.find_all('div', attrs={'class': re.compile('^smh__participantName')})
        pattern = "(\([a-zA-Z]*\))"

        nationality = re.search(pattern, nat_v[0].text).group(0)
        data['player_1']['nationality'] = nationality.replace('(', '').replace(')', '')

        nationality = re.search(pattern, nat_v[1].text).group(0)
        data['player_2']['nationality'] = nationality.replace('(', '').replace(')', '')
    except:
        pass
    
    data['status'] = soup.find('span', attrs={'class':'fixedHeaderDuel__detailStatus'}).text
    
    try:
        endtime_v = soup.find('div', attrs={'class': 'smh__time smh__time--overall'}).text
        data['EndTime'] = endtime_v.replace(':', ' h ') + ' m'
    except:
        pass
    
    try:
        data['score']['fullTime']['player_1'] = int(soup.find_all('div', attrs={'class': re.compile('^smh__part smh__score')})[0].text)
        data['score']['fullTime']['player_2'] = int(soup.find_all('div', attrs={'class': re.compile('^smh__part smh__score')})[-1].text)
    except:
        pass
    
    # Set scores
    p1_score = soup.find_all('div', attrs={'class': re.compile('^smh__part smh__home smh__part')})
    p2_score = soup.find_all('div', attrs={'class': re.compile('^smh__part smh__away smh__part')})

    set_nr = 1
    for p1, p2 in zip(p1_score, p2_score):
        if (p1.text != '') & (p2.text != ''):
            event = {'set_' + str(set_nr): {'player_1': None, 'player_2': None} }

            event['set_' + str(set_nr)]['player_1'] = int(p1.text)
            event['set_' + str(set_nr)]['player_2'] = int(p2.text)        
            try:
                event['set_' + str(set_nr)]['time'] = soup.find_all('div', attrs={'class': 'smh__time'})[set_nr].text.replace(':', ' h ') + ' m'
            except:
                pass

            data['score']['sets'].append(event)

            set_nr += 1
            
    # Odds
    try:
        data['odds']['player_1'] = float(soup.find_all('span', attrs={'class':re.compile('^oddsValue')})[0].text)
        data['odds']['player_2'] = float(soup.find_all('span', attrs={'class':re.compile('^oddsValue')})[-1].text)
    except:
        pass

def statistics(p,t):
    soup = BeautifulSoup(driver.page_source, features="lxml")

    # Service
    for i in soup.find_all('div', attrs={'class':'statRow'}):
        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Aces':
                data[p]['player_1']['Service']['Aces'] = int(i.find('div', attrs={'class':'statHomeValue'}).text)
                data[p]['player_2']['Service']['Aces'] = int(i.find('div', attrs={'class':'statAwayValue'}).text)
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Double Faults':
                data[p]['player_1']['Service']['Double Faults'] = int(i.find('div', attrs={'class':'statHomeValue'}).text)
                data[p]['player_2']['Service']['Double Faults'] = int(i.find('div', attrs={'class':'statAwayValue'}).text)
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == '1st Serve Percentage':
                data[p]['player_1']['Service']['1st Serve Percentage'] = float(i.find('div', attrs={'class':'statHomeValue'}).text.replace('%','')) / 100
                data[p]['player_2']['Service']['1st Serve Percentage'] = float(i.find('div', attrs={'class':'statAwayValue'}).text.replace('%','')) / 100
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == '1st Serve Points Won':
                data[p]['player_1']['Service']['1st Serve Points Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Service']['1st Serve Points Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == '2nd Serve Points Won':
                data[p]['player_1']['Service']['2nd Serve Points Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Service']['2nd Serve Points Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Break Points Saved':
                data[p]['player_1']['Service']['Break Points Saved'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Service']['Break Points Saved'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

    # Return
    for i in soup.find_all('div', attrs={'class':'statRow'}):
        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == '1st Return Points Won':
                data[p]['player_1']['Return']['1st Return Points Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Return']['1st Return Points Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == '2nd Return Points Won':
                data[p]['player_1']['Return']['2nd Return Points Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Return']['2nd Return Points Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Break Points Converted':
                data[p]['player_1']['Return']['Break Points Converted'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Return']['Break Points Converted'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

    # Points
    for i in soup.find_all('div', attrs={'class':'statRow'}):
        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Winners':
                data[p]['player_1']['Points']['Winners'] = int(i.find('div', attrs={'class':'statHomeValue'}).text)
                data[p]['player_2']['Points']['Winners'] = int(i.find('div', attrs={'class':'statAwayValue'}).text)
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Unforced Errors':
                data[p]['player_1']['Points']['Unforced Errors'] = int(i.find('div', attrs={'class':'statHomeValue'}).text)
                data[p]['player_2']['Points']['Unforced Errors'] = int(i.find('div', attrs={'class':'statAwayValue'}).text)
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Net Points Won':
                data[p]['player_1']['Points']['Net Points Won'] = int(i.find('div', attrs={'class':'statHomeValue'}).text)
                data[p]['player_2']['Points']['Net Points Won'] = int(i.find('div', attrs={'class':'statAwayValue'}).text)
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Max Points In Row':
                data[p]['player_1']['Points']['Max Points In Row'] = int(i.find('div', attrs={'class':'statHomeValue'}).text)
                data[p]['player_2']['Points']['Max Points In Row'] = int(i.find('div', attrs={'class':'statAwayValue'}).text)
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Service Points Won':
                data[p]['player_1']['Points']['Service Points Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Points']['Service Points Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Return Points Won':
                data[p]['player_1']['Points']['Return Points Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Points']['Return Points Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Total Points Won':
                data[p]['player_1']['Points']['Total Points Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Points']['Total Points Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

    # Games
    for i in soup.find_all('div', attrs={'class':'statRow'}):
        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Max Games In Row':
                data[p]['player_1']['Games']['Max Games In Row'] = int(i.find('div', attrs={'class':'statHomeValue'}).text)
                data[p]['player_2']['Games']['Max Games In Row'] = int(i.find('div', attrs={'class':'statAwayValue'}).text)
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Service Games Won':
                data[p]['player_1']['Games']['Service Games Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Games']['Service Games Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Return Games Won':
                data[p]['player_1']['Games']['Return Games Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Games']['Return Games Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

        try:
            if i.find('div', attrs={'class':'statCategoryName'}).text == 'Total Games Won':
                data[p]['player_1']['Games']['Total Games Won'] = i.find('div', attrs={'class':'statHomeValue'}).text
                data[p]['player_2']['Games']['Total Games Won'] = i.find('div', attrs={'class':'statAwayValue'}).text
        except:
            pass

def add_sets():
    soup = BeautifulSoup(driver.page_source, features="lxml")

    nr_of_sets = len(soup.find_all('a', attrs={'class':'subTabs__tab'}))

    for s in range(1, nr_of_sets):
        data['set_' + str(s)] = {
            'player_1': {
                'Service': {
                    'Aces': None,
                    'Double Faults': None,
                    '1st Serve Percentage': None,
                    '1st Serve Points Won': None,
                    '2nd Serve Points Won': None,
                    'Break Points Saved': None},
                'Return': {
                    '1st Return Points Won': None,
                    '2nd Return Points Won': None,
                    'Break Points Converted': None},
                'Points': {
                    'Winners': None,
                    'Unforced Errors': None,
                    'Net Points Won': None,
                    'Max Points In Row': None,
                    'Service Points Won': None,
                    'Return Points Won': None,
                    'Total Points Won': None},
                'Games': {
                    'Max Games In Row': None,
                    'Service Games Won': None,
                    'Return Games Won': None,
                    'Total Games Won': None}
            },
            'player_2': {
                'Service': {
                    'Aces': None,
                    'Double Faults': None,
                    '1st Serve Percentage': None,
                    '1st Serve Points Won': None,
                    '2nd Serve Points Won': None,
                    'Break Points Saved': None},
                'Return': {
                    '1st Return Points Won': None,
                    '2nd Return Points Won': None,
                    'Break Points Converted': None},
                'Points': {
                    'Winners': None,
                    'Unforced Errors': None,
                    'Net Points Won': None,
                    'Max Points In Row': None,
                    'Service Points Won': None,
                    'Return Points Won': None,
                    'Total Points Won': None},
                'Games': {
                    'Max Games In Row': None,
                    'Service Games Won': None,
                    'Return Games Won': None,
                    'Total Games Won': None}
            }
        }

def set_statistics():
    soup = BeautifulSoup(driver.page_source, features="lxml")

    nr_of_sets = len(soup.find_all('a', attrs={'class':'subTabs__tab'}))

    for s in range(1, nr_of_sets):
        BASE = f"//a[@href='#match-summary/match-statistics/{s}']"
        driver.find_element(by='xpath', value=BASE).click()
        time.sleep(3)
        bs_data = BeautifulSoup(driver.page_source, features="lxml")
        statistics('set_' + str(s), bs_data)

def point_by_point_statistics():
    soup = BeautifulSoup(driver.page_source, features="lxml")
    
    temp_list = []
    
    raws_score = soup.find_all('div', attrs={'class': 'matchHistoryRow'})
    raws_history = soup.find_all('div', attrs={'class': 'matchHistoryRow__fifteens'})
    
    for i in range(len(raws_score)):
        event = {'player_1_score': None, 'player_2_score': None, 'servis': None, 'game_history': None}
        
        event['player_1_score'] = raws_score[i].text.replace('LOST SERVE', '').split('-')[0].replace('SP', '').replace('77', '7').replace('65', '6').replace('64', '6')
        event['player_2_score'] = raws_score[i].text.replace('LOST SERVE', '').split('-')[-1].replace('SP', '').replace('77', '7').replace('65', '6').replace('64', '6')
        
        # Player which server
        servis = raws_score[i].find_all('div', attrs={'class': re.compile('^matchHistoryRow__servis')})
        try:
            if servis[0].div.svg['class'][0] == 'tennis-ico':
                event['servis'] = 'player_1'
        except:
            pass
        try:
            if servis[1].div.svg['class'][0] == 'tennis-ico':
                event['servis'] = 'player_2'
        except:
            pass        
        
        # Game history
        try:
            event['game_history'] = raws_history[i].text.replace('BP', '').replace('MP', '').replace('SP', '')
        except:
            pass
        
        temp_list.append(event)
        
    return temp_list

def add_point_by_point():
    soup = BeautifulSoup(driver.page_source, features="lxml")

    # Get number of sets played
    nr_of_sets = len(soup.find_all('a', attrs={'class':'subTabs__tab'}))

    # Add new 'point_by_point' root tree
    data['point_by_point'] = {}
    for s in range(1, nr_of_sets):
        data['point_by_point']['set_' + str(s)] = []

# Open Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
options.add_argument('--log-level=3') # Remove information from console

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

x = 0
for match_id in match_ids:
    print('\n')
    print('Current match: ' + str(match_id))
    print('Remaining: ' + str(len(match_ids) - 1 - x))

    url = 'https://www.flashscore.com/match/' + match_id + "/#match-summary"

    driver.get(url)
    time.sleep(1)

    # Accept GDPR
    try:
        driver.find_element(by='id', value='onetrust-accept-btn-handler').click()
        time.sleep(1)
    except:
        pass

    # Create empty dictionary to store data
    data_function()

    data['match_id'] = match_id

    # Match summary
    time.sleep(3)
    match_summary()

    # Match statistics
    try:
        driver.find_element(by='xpath', value="//a[@href='#match-summary/match-statistics']").click()
        time.sleep(3)
        match = BeautifulSoup(driver.page_source, features="lxml")
        statistics('match', match)
        
        add_sets()

        time.sleep(1)
        set_statistics()
    except:
        pass

    # Add "Point by Point" root tree
    time.sleep(1)
    add_point_by_point()
    
    # Click on "Point by Point" tab
    driver.find_elements_by_xpath("//a[@class='tabs__tab']")[-1].click()
    time.sleep(3)

    # Fill Set_1 (Point by Point)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    data['point_by_point']['set_1'] = point_by_point_statistics()

    # Fill rest of the Set_x (Point by Point)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    nr_of_sets = len(soup.find_all('a', attrs={'class':'subTabs__tab'}))

    for s in range(1, nr_of_sets):
        BASE = f"//a[@href='#match-summary/point-by-point/{s}']"
        driver.find_element(by='xpath', value=BASE).click()
        data['point_by_point']['set_' + str(s + 1)] = point_by_point_statistics()
        time.sleep(3)

    data_processed.append(data)

    x += 1

driver.close()

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

with open(os.getcwd() + r'\processed' + '\\' + str(yesterday.date()) + '.json', 'w') as json_file:
    json.dump(data_processed, json_file)
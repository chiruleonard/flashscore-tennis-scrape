from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import argparse

import datetime
import pandas as pd
import os.path
import re
import time

parser = argparse.ArgumentParser(description='Script to get all match IDs for a given day')

parser.add_argument('--days', '-d', type=int, required=True, help='Number of days before')
parser.add_argument('--email', '-e', type=str, required=True, help='Email for login')
parser.add_argument('--password', '-p', type=str, required=True, help='Password for login')
parser.add_argument('--format', '-f', type=str, required=True, help='Format data')

args = parser.parse_args()
print(args.days, args.email, args.password)

# Open Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
options.add_argument('--log-level=3') # Remove information from console

driver = webdriver.Chrome(ChromeDriverManager().install(), keep_alive=False, options=options)

url = 'https://www.flashscore.com/tennis/'
driver.get(url)
time.sleep(5)

# Accept GDPR
driver.find_element_by_id('onetrust-accept-btn-handler').click()

# Find Login button and make a click action
# Input username and password
# Make a click action
driver.find_element_by_id('signIn').click()
time.sleep(5)
#driver.find_element_by_id('onetrust-accept-btn-handler').click()
driver.find_element_by_id('email').send_keys(args.email)
driver.find_element_by_id('passwd').send_keys(args.password)
driver.find_element_by_id('login').click()
time.sleep(10)

# Make a click to X days back
for d in range(args.days):
    driver.find_element_by_xpath('//*[@id="live-table"]/div[1]/div[2]/div[1]/div').click()
    time.sleep(5)

# Store code page
page_source_overview = driver.page_source

# Loading page source info
soup = BeautifulSoup(page_source_overview, 'lxml')

# Store all the maches
matches = soup.find_all('div', attrs={'id':re.compile('^g_2')})

# Create empty lists to store data
data = {'status':[],
        'Player_1':[],
        'Player_2':[],
        'match_ID':[]}

# Loop through each match
for m in matches:
    try:
        data['status'].append(m.find('div', attrs={'class':re.compile('^event__stage')}).text)
    except:
        data['status'].append(m.find('div', attrs={'class':re.compile('^event__time')}).text)
    data['Player_1'].append(m.find('div', attrs={'class':re.compile('^event__participant event__participant--home')}).text)
    data['Player_2'].append(m.find('div', attrs={'class':re.compile('^event__participant event__participant--away')}).text)
    data['match_ID'].append(m['id'].split('_')[-1])

# Path to save the file
# current_date = datetime.datetime.now()
# path = os.path.expanduser("~") + '\Desktop\\' + str(current_date.strftime('%Y-%m-%d')) + args.format +'.csv'

x_days = datetime.datetime.now() - datetime.timedelta(days=args.days)
path = '/mnt/ftp/public/' + x_days.strftime('%Y-%m-%d') + '_' + args.format

df = pd.DataFrame(data)
df.to_csv(path)

# Close browser session
driver.close()
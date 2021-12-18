# Python script to scrape Flashscore match

Python v3.9

## Scrape match IDs
run ```python .\00-tennis_ids.py --day 1 --email "example@email.com" --password "PASSWORD" --format "csv"```

## Scrape
1. Matches that will be scrapped will be copy/paste in **\prerequisite\json.text**
  Each match ID **l4DvtYcA** will be placed on a separate line.
2. run ```python .\01-main-v1.0.py```
3. Data will be saved in **\\processed\\** in JSON format **<YYYY-MM-DD>**
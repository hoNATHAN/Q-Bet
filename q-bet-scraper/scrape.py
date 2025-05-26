from match_data_scraper import get_match_data
from odds_data_scraper import get_odds_data
import time 
import random
import json
import os

delay = random.uniform(1, 5) # Randomly choose delay between 1-10 seconds
#match_url = "https://bo3.gg/matches/astralis-vs-spirit-18-05-2025"
#odds_url = "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-pgl-astana/astralis-counter-strike-team-spirit-counter-strike-z3MtGpbS/"
odds_file = "alex_odds.json"
match_file = "alex_match.json"
odds_path = "./data/odds/"
match_path = "./data/match/"

if __name__ == "__main__":
    os.makedirs(match_path, exist_ok=True)
    os.makedirs(odds_path, exist_ok=True)
    with open(odds_file, 'r') as f:
        odds_data = json.load(f)

    with open(match_file, 'r') as f:
        match_data = json.load(f)

    '''Scrape Match Data'''
    #print("Scraping Match Data")
    #for tournament in match_data.keys():
        #print(tournament + "\n")
        #matches = match_data[tournament]["matches"]
        #for match in matches:
         #   match_url = match["match_url"]
          #  delay = random.uniform(1, 10) # Randomly choose delay between 1-10 seconds
           # success = get_match_data(match_url, match_path)
            #retry_count = 0
            #while not success and retry_count < 3:
             #   retry_count += 1
              #  print(f"Retrying {match_url}: {retry_count}")
               # success = get_match_data(match_url, match_path)

    print("Done Scraping Match Data")

    '''Scrape Odds Data'''
    print("Scraping Odds Data")
    for tournament, tourney_data in odds_data.items():
        for m in tourney_data.get("matches", []):
            # if m is a dict, pull out the URL; if it's already a string, use it directly
            if isinstance(m, dict):
                odds_url = m.get("match_url") or m.get("url")
            else:
                odds_url = m

            if not odds_url:
                print(f"  skipping malformed entry: {m!r}")
                continue

            print(f"{tournament}: {odds_url}")
            time.sleep(delay)

            success = get_odds_data(odds_url, odds_path)
            retry_count = 0
            while not success and retry_count < 3:
                retry_count += 1
                print(f"Retrying {odds_url}: {retry_count}")
                success = get_odds_data(odds_url, odds_path)

    print("Done Scraping Odds Data")



from match_data_scraper import get_match_data
from odds_data_scraper import get_odds_data
import time 
import random
import json
import os

delay = random.uniform(1, 5) # Randomly choose delay between 1-10 seconds
#match_url = "https://bo3.gg/matches/astralis-vs-spirit-18-05-2025"
#odds_url = "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-pgl-astana/astralis-counter-strike-team-spirit-counter-strike-z3MtGpbS/"
#odds_file = "matt_odds.json"
match_file = "full_matt_match.json"
odds_path = "./data/odds/"
match_path = "./data/match/"

# ── UTIL ───────────────────────────────────
def shard_filter(idx): 
    return idx % args.shards == args.shard

# ── MAIN ───────────────────────────────────
if __name__ == "__main__":
    os.makedirs(match_path, exist_ok=True)
    os.makedirs(odds_path,  exist_ok=True)

    # load your JSON files
    with open(match_file) as f: match_data = json.load(f)
    with open(odds_file)  as f: odds_data  = json.load(f)

    '''Scrape Match Data'''
    print("Scraping Match Data")
    for tournament in match_data.keys():
        print(tournament + "\n")
        matches = match_data[tournament]["matches"]
        #match_files = [f for f in os.listdir(match_path) if os.path.isfile(os.path.join(match_path, f))]
        for match in matches:
            match_url = match["match_url"]
            '''
            match_name = "match_" + match["match_name"] + ".json"
            if match_name not in match_files:
                print(match_name)
            '''
            delay = random.uniform(1, 10) # Randomly choose delay between 1-10 seconds
            success = get_match_data(match_url, match_path)
            retry_count = 0
            while not success and retry_count < 3:
                retry_count += 1
                print(f"Retrying {match_url}: {retry_count}")
                success = get_match_data(match_url, match_path)

    print(f"→ running shard {args.shard}/{args.shards} over {len(match_tasks)} matches")
    for idx, (tourney, name, url) in enumerate(match_tasks):
        if not shard_filter(idx):
            continue

    '''Scrape Odds Data'''
    print("Scraping Odds Data")
    for tournament in odds_data.keys():
        print(tournament + "\n")
        for match in matches:
            odds_url = match 
            print(odds_url)
            time.sleep(delay) # Randomly wait to make it seem like human behavior
            try:
                success = get_odds_data(odds_url,  odds_path)
            except:
                success = False

            retry_count = 0 
            while not success and retry_count < 3:
                retry_count += 1
                print(f"Retrying {odds_url}: {retry_count}")
                success = get_odds_data(odds_url, odds_path)
    print("Done Scraping Odds Data")

        print(f"[{idx}] {tourney} → {name}")
        time.sleep(delay())
        success = get_match_data(url, match_path)
        retries = 0
        while not success and retries < 3:
            retries += 1
            print(f"  retry {retries}")
            success = get_match_data(url, match_path)

    # ══ ODDS TASKS ════════════════════════════
    #odds_tasks = []
    #for tourney, data in odds_data.items():
     #   if args.tournaments and tourney not in args.tournaments:
      #      continue
       # for m in data.get("matches", []):
        #    url = m.get("match_url") or m.get("url") if isinstance(m, dict) else m
         #   odds_tasks.append((tourney, url))

    #print(f"→ running shard {args.shard}/{args.shards} over {len(odds_tasks)} odds URLs")
    #for idx, (tourney, url) in enumerate(odds_tasks):
     #   if not shard_filter(idx): 
      #      continue
       # print(f"[{idx}] {tourney} → {url}")
        #time.sleep(delay())
        #success = get_odds_data(url, odds_path)
        #retries = 0
        #while not success and retries < 3:
        #    retries += 1
         #   print(f"  retry {retries}")
          #  success = get_odds_data(url, odds_path)

    print("✅ Done")

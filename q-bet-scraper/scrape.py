from match_data_scraper import get_match_data
from odds_data_scraper   import get_odds_data
import argparse, json, os, random, time

# ── ARGS ───────────────────────────────────
parser = argparse.ArgumentParser(description="Parallel scraper")
parser.add_argument("--shards", type=int, default=1,
    help="Total parallel processes")
parser.add_argument("--shard",  type=int, default=0,
    help="This process’s index (0..shards-1)")
parser.add_argument("-t","--tournaments", nargs="*",
    help="Optional list of tournament names to include")
args = parser.parse_args()

# ── CONFIG ─────────────────────────────────
delay      = (lambda: random.uniform(1,10))
odds_file  = "alex_odds.json"
match_file = "alex_match.json"
odds_path  = "./data/odds/"
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

    # ══ MATCH TASKS ═══════════════════════════
    # flatten (tournament, match_url)
    match_tasks = []
    for tourney, data in match_data.items():
        if args.tournaments and tourney not in args.tournaments:
            continue
        for m in data.get("matches", []):
            # extract both name and URL
            if isinstance(m, dict):
                name = m["match_name"]
                url  = m["match_url"]
            else:
                # if old style just URL, derive a slug
                url  = m
                name = url.rstrip("/").split("/")[-1]
            match_tasks.append((tourney, name, url))

    print(f"→ running shard {args.shard}/{args.shards} over {len(match_tasks)} matches")
    for idx, (tourney, name, url) in enumerate(match_tasks):
        if not shard_filter(idx):
            continue

        # skip by match_name
        fname = f"match_{name}.json"
        full  = os.path.join(match_path, fname)
        if os.path.exists(full):
            print(f"  ↩︎ already have {fname}, skipping")
            continue

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
from match_data_scraper import get_match_data
from odds_data_scraper import get_odds_data

#match_url = "https://bo3.gg/matches/astralis-vs-spirit-18-05-2025"
#odds_url = "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-pgl-astana/astralis-counter-strike-team-spirit-counter-strike-z3MtGpbS/"
odds_file = "matt_odds.json"
match_file = "matt_match.json"
odds_path = "./data/odds/"
match_path = "./data/match/"

if __name__ == "main":
    with open(odds_file, 'r') as f:
        odds_data = json.load(f)

    with open(match_file, 'r') as f:
        match_data = json.load(f)

    '''Scrape Match Data'''
    print("Scraping Match Data")
    for tournament in match_data.keys():
        match_url = match_data[tournament]["matches"]["match_url"]
        get_match_data(match_url, match_path)
    print("Done Scraping Match Data")

    '''Scrape Odds Data'''
    print("Scraping Odds Data")
    for tournament in match_data.keys():
        odds_url = odds_data[tournament]["matches"]
        get_odds_data(odds_url,  odds_path)
    print("Done Scraping Odds Data")



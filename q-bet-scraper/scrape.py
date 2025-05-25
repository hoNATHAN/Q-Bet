from match_data_scraper import get_match_data
from odds_data_scraper import get_odds_data

match_url = "https://bo3.gg/matches/astralis-vs-spirit-18-05-2025"
odds_url = "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-pgl-astana/astralis-counter-strike-team-spirit-counter-strike-z3MtGpbS/"
path = "./"

print("Gathering match data")
#get_match_data(match_url, path)
print("Gathering odds data")
get_odds_data(odds_url,  path)
print("Done")

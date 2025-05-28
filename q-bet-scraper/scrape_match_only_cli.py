import argparse
import time
import random
import json
from match_data_scraper import get_match_data


def main(match_file):
    match_path = "./data/match/"

    with open(match_file, "r") as f:
        match_data = json.load(f)

    """Scrape Match Data"""
    print("Scraping Match Data")
    for tournament in match_data.keys():
        print(tournament + "\n")
        matches = match_data[tournament]["matches"]
        for match in matches:
            match_url = match["match_url"]
            delay = random.uniform(1, 10)  # Random delay
            time.sleep(delay)
            success = get_match_data(match_url, match_path)
            retry_count = 0
            while not success and retry_count < 3:
                retry_count += 1
                print(f"Retrying {match_url}: {retry_count}")
                success = get_match_data(match_url, match_path)
    print("Done Scraping Match Data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape match data.")
    parser.add_argument(
        "--match_file", required=True, help="Path to the match JSON file."
    )
    args = parser.parse_args()
    main(args.match_file)

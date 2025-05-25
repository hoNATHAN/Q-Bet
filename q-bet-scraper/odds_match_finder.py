from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time 
import random
import json

url = "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-the-perfect-world-shanghai-major/results/"
base_url = "https://www.oddsportal.com"
tournaments = {
    "PGL Astana 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-pgl-astana/results/",
    "BLAST Rivals Spring 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-blast-rivals/results/",
    "Intel Extreme Masters Melbourne 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-iem-melbourne/results/",
    "PGL Bucharest 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-pgl-bucharest/results/",
    "BLAST Open Spring 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-blast-open/results/",
    "ESL Pro League Season 21": "https://www.oddsportal.com/esports/counter-strike/counter-strike-esl-pro-league-season-21/results/",
    "ESL Pro League Season 21 Play-in": "https://www.oddsportal.com/esports/counter-strike/counter-strike-esl-pro-league-season-21/results/",
    "PGL Cluj-Napoca 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-pgl-cluj-napoca/results/",
    "Intel Extreme Masters Katowice 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-intel-extreme-masters-katowice/results/",
    "Intel Extreme Masters Katowice 2025 Play-In": "https://www.oddsportal.com/esports/counter-strike/counter-strike-intel-extreme-masters-katowice/results/",
    "BLAST Bounty Spring 2025": "https://www.oddsportal.com/esports/counter-strike/counter-strike-blast-bounty/results/",
    "Perfect World Shanghai Major 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-the-perfect-world-shanghai-major/results/",
    "Perfect World Shanghai Major 2024 Opening": "https://www.oddsportal.com/esports/counter-strike/counter-strike-the-perfect-world-shanghai-major/results/",
    "Thunderpick World Championship 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-thunderpick-world-championship/results/",
    "BLAST Premier: World Final 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-blast-premier-global-final/results/",
    "Thunderpick World Championship 2024 Play-in": "https://www.oddsportal.com/esports/counter-strike/counter-strike-thunderpick-world-championship/results/",
    "IEM Rio 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-iem-rio/results/",
    "BLAST Premier: Fall Final 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-blast-premier-fall/results/",
    "ESL Pro League Season 20": "https://www.oddsportal.com/esports/counter-strike/counter-strike-esl-pro-league-season-20/results/",
    "BetBoom Dacha Belgrade 2024 #2": "https://www.oddsportal.com/esports/counter-strike/counter-strike-betboom-dacha-belgrade-2/results/",
    "BetBoom Dacha Belgrade 2024 #2 Play-in": "https://www.oddsportal.com/esports/counter-strike/counter-strike-betboom-dacha-belgrade-2/results/",
    "IEM Cologne 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-intel-extreme-masters-cologne/results/",
    "IEM Cologne 2024 Play-in": "https://www.oddsportal.com/esports/counter-strike/counter-strike-intel-extreme-masters-cologne/results/",
    "BLAST Premier: Fall Groups 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-blast-premier-fall/results/",
    "Skyesports Championship 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-skyesports-championship/results/",
    "Esports World Cup 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-world-cup/results/",
    "BLAST Premier: Spring Final 2024": "https://www.oddsportal.com/esports/counter-strike/counter-strike-blast-premier-spring/results/",
    "YaLLa Compass 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-yalla-compass/results/",
    "IEM Dallas 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-iem-dallas/results/",
    "CCT Global Finals 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-cct-season-1-global-finals/results/",
    "BetBoom Dacha Belgrade 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-betboom-dacha-belgrade/results/",
    "ESL Pro League Season 19": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-esl-pro-league-season-19/results/",
    "IEM Chengdu 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-iem-chengdu/results/",
    "PGL Major Copenhagen 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-pgl-major-copenhagen/results/",
    "IEM Katowice 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-intel-extreme-masters-katowice-2024/results/",
    "IEM Katowice 2024 Play-in": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-intel-extreme-masters-katowice-2024/results/",
    "BLAST Premier: Spring Groups 2024": "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-blast-premier-spring/results/"
}



with sync_playwright() as p:
    for key in tournaments.keys():
        print(key)
        url = tournaments[key]
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        try:
            page.wait_for_selector('#react-button-go-top', state="attached", timeout=10000)
            page.wait_for_selector(".flex.w-full.items-center", timeout=10000)

        except Exception as e:
            print("Timeout waiting", e)
            browser.close()
            exit()

        time.sleep(5)
        html = page.content() 

        soup = BeautifulSoup(html, "html.parser")
        num_pages = len(soup.find_all('a', class_='pagination-link')[:-1])
        match_data = []
        if num_pages == 0:
            matches = soup.find_all('div', class_='eventRow flex w-full flex-col text-xs')
            for match in matches:
                links = match.find_all('a', class_='next-m:flex next-m:!mt-0 ml-2 mt-2 min-h-[32px] w-full hover:cursor-pointer')
                link = ""
                if len(links) > 1:
                    link = links[-1].get('href')
                else:
                    link = links[0].get('href')
                match_url = f"{base_url}{link}"
                match_data.append(f"{base_url}{link}")
        else:
            for x in range(num_pages):
                if x != 0:
                    page_num = x+1
                    page.goto(f"{url}#/page/{page_num}/")
                    try:
                        page.wait_for_selector('#react-button-go-top', state="attached", timeout=10000)
                        page.wait_for_selector(".flex.w-full.items-center", timeout=10000)

                    except Exception as e:
                        print("Timeout waiting", e)
                        browser.close()
                        exit()

                #Process all macthes
                matches = soup.find_all('div', class_='eventRow flex w-full flex-col text-xs')
                for match in matches:
                    links = match.find_all('a', class_='next-m:flex next-m:!mt-0 ml-2 mt-2 min-h-[32px] w-full hover:cursor-pointer')
                    link = ""
                    if len(links) > 1:
                        link = links[-1].get('href')
                    else:
                        link = links[0].get('href')
                    match_url = f"{base_url}{link}"
                    match_data.append(f"{base_url}{link}")
        tournaments[key] = {"url": url, "matches": match_data}

    with open('odds_tournament_data.json', 'w') as f:  
        json.dump(tournaments, f, indent=2)  

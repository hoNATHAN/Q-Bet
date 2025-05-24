from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time 
import random
import json

url = "https://bo3.gg/tournaments/finished?tiers=s&period=all_time"
base_url = "https://bo3.gg"
tournaments = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)

    try:
        page.wait_for_selector('p.tournament-name', state="attached", timeout=10000)
    except Exception as e:
        print("Timeout waiting", e)
        browser.close()
        exit()

    html = page.content() 

    soup = BeautifulSoup(html, "html.parser")

    date_list = soup.find_all('div', class_='table-group')

    for d in date_list:
        date = d.find('div', class_='table-group__head').text

        tournament_list = d.find_all('div', class_='table-row')
        for t in tournament_list:
            a_tag = t.find('a')
            if not a_tag:
                continue
            path  = a_tag.get('href')
            name = a_tag.find('p', class_='tournament-name').text
            tournaments[name] = {"url": f"{base_url}{path}/results", "matches": []}


        if date == "January 2024":
            break


    for key in tournaments.keys():
        t_url = tournaments[key]["url"]
        print(t_url)
        page = browser.new_page()
        page.goto(t_url)

        try:
            page.wait_for_selector('p.system', state="attached", timeout=10000)
        except Exception as e:
            print("Timeout waiting", e)
            browser.close()
            exit()

        html = page.content() 

        soup = BeautifulSoup(html, "html.parser")

        match_list = soup.find_all('div', class_='table-row table-row--finished data-advantage')
        for match in match_list:
            a_tag = match.find('a')
            match_path = a_tag.get('href')
            match_name = match_path.removeprefix("/matches/")
            match_data = {'match_name': match_name, 'match_url': f"{base_url}{match_path}"}
            tournaments[key]["matches"].append(match_data)

    with open('tournament_data.json', 'w') as f:  
        json.dump(tournaments, f, indent=2)  

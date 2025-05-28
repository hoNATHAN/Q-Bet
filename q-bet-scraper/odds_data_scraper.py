from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time 
import random
import json
from datetime import datetime

test_url = "https://www.oddsportal.com/pl/esports/counter-strike/counter-strike-pgl-astana/astralis-counter-strike-team-spirit-counter-strike-z3MtGpbS/"
a_odds_by_time = {}
b_odds_by_time = {}
team_1 = ""
team_2 = ""
reverse_team_name_map = {
    "team spirit": "spirit",
    "aurora": "aurora-gaming",
    "ninjas in pyjamas": "nip",
    "navi": "natus-vincere",
    "the mongolz": "the-mongolz",
    "virtus.pro": "virtus-pro",
    "g2 esports": "g2",
    "pain": "pain-gaming",
    "m80": "m80-cs-go",
    "falcons": "falcons-esports",
    "team vitality": "vitality",
    "mouz": "mousesports",
    "wildcard gaming": "wildcard-gaming",
    "team liquid": "liquid",
    "complexity gaming": "complexity",
    "apogee": "betclic-apogee-esports",
    "rare atom": "rare-atom",
    "legacy": "legacy-br",
    "the huns": "the-huns-esports",
    "tyloo": "tyloo-cs-go",
    "nemiga gaming": "nemiga",
    "nrg esports": "nrg",
    "lynn vision": "lynn-vision",
    "imperial k": "imperial-female",
    "beatboom team": "betboom-team",
    "passion ua": "passion-ua",
    "9z team": "9z",
    "red canids": "red-canids-cs-go",
    "sangal esports": "sangal",
    "alternate attax": "alternate-attax-cs-go",
    "amkal esports": "amkal",
    "bleed esports": "bleed-esports-cs",
    "true rippers": "true-rippers",
    "dms": "future",
    "revenant esports": "revenant-cs",
    "sashi": "sashi-esport",
    "betboom team": "betboom",
    "gamin gladiators": "gaimingladiators",
    "steel helmet": "steel-helmet",
    "9 pandas": "9-pandas"
}



def remap_name(team_name):
    if team_name in reverse_team_name_map:
        return reverse_team_name_map[team_name]
    else:
        name = team_name.strip()
        return name.replace(" ", "-").lower()

def get_odds_data(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")  

        try:
            page.wait_for_selector('div.flex.flex-col', state="attached", timeout=10000)
            page.wait_for_selector('#react-event-header', state="attached", timeout=10000)
        except Exception as e:
            print("Timeout waiting", e)
            browser.close()
            return False

        odd_container_divs = page.query_selector_all('[data-testid="odd-container"]')
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        teams = soup.find_all('p', 'text-[22px] self-center truncate')
        team_1 =  remap_name(teams[0].text)
        team_2 =  remap_name(teams[1].text)
        date_parts = soup.find('div', class_='item-center flex gap-1 font-main text-xs font-normal text-gray-dark').find_all('p')
        date_str = ""
        date_parts = date_parts[1:]
        for part in date_parts:
            date_str += f"{part.text} "

        date_str = date_str.strip()
        dt = datetime.strptime(date_str, "%d %b %Y, %H:%M")
        final_date = dt.strftime("%d-%m-%Y")
        final_year = dt.year

        a = True
        for div in odd_container_divs:
            div.hover()
            time.sleep(0.05)  # let DOM update
            html_of_hovered_element = div.inner_html()
            soup = BeautifulSoup(html_of_hovered_element, "html.parser")
            divs = soup.find_all('div', class_="flex flex-col gap-1")
            date_divs = divs[1].find_all('div', class_="text-[10px] font-normal")
            timestamps = []
            for d in date_divs:
                date_str = d.text.strip()
                timestamps.append(datetime.strptime(date_str, "%d %b, %H:%M").replace(year=final_year))

            odds = []
            odds_divs = divs[2].find_all('div')
            for o in odds_divs:
                odds.append(o.text.strip())

            for dt, odd in zip(timestamps, odds):
                if a:
                    a_odds_by_time.setdefault(dt, []).append(odd)
                else:
                    b_odds_by_time.setdefault(dt, []).append(odd)
            a = not a


        for key in a_odds_by_time.keys():
            if len(a_odds_by_time[key]) > 1:
                total = 0
                for string in a_odds_by_time[key]:
                    total += int(string)
                avg = total / len(a_odds_by_time[key])
                sign = "+"
                if avg < 0:
                    sign = "-"
                a_odds_by_time[key] = [f"{sign}{avg}"]

        for key in b_odds_by_time.keys():
            if len(b_odds_by_time[key]) > 1:
                total = 0
                for string in b_odds_by_time[key]:
                    total += int(string)
                avg = total / len(b_odds_by_time[key])
                sign = "+"
                if avg < 0:
                    sign = "-"
                b_odds_by_time[key] = [f"{sign}{avg}"]

        odds_by_time = {team_1: a_odds_by_time, team_2: b_odds_by_time}

        json_ready = {
            team: {dt.strftime("%Y-%m-%d %H:%M"): odds for dt, odds in odds_dict.items()}
            for team, odds_dict in odds_by_time.items()
        }

        json_str = json.dumps(json_ready, indent=4)
        with open(f'{output_path}odds_{team_1}-vs-{team_2}-{final_date}.json', 'w') as f:  
            json.dump(json_ready, f, indent=2)  
        return True

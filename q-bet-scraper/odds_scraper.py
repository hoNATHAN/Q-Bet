from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time 
import random
import json
from datetime import datetime

url = "https://www.oddsportal.com/esports/league-of-legends/league-of-legends-lck/gen-g-league-of-legends-t1-league-of-legends-2NqeG5Gd/"
a_odds_by_time = {}
b_odds_by_time = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)

    try:
        page.wait_for_selector('div.flex.flex-col', state="attached", timeout=10000)
    except Exception as e:
        print("Timeout waiting", e)
        browser.close()
        exit()
    odd_container_divs = page.query_selector_all('[data-testid="odd-container"]')

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
            timestamps.append(datetime.strptime(date_str, "%d %b, %H:%M").replace(year=2025))

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



    odds_by_time = {"a": a_odds_by_time, "b": b_odds_by_time}
    #print(odds_by_time)

    json_ready = {
        outer_key: {
            dt_key.strftime("%Y-%m-%d %H:%M:%S"): value
            for dt_key, value in inner_dict.items()
        }
        for outer_key, inner_dict in odds_by_time.items()
    }
    #json_ready = {dt.strftime("%Y-%m-%d %H:%M:%S"): odds for dt, odds in odds_by_time.items()}
    json_str = json.dumps(json_ready, indent=4)
    print(json_str)


    #match_list = soup.find_all('ul', class_='flex content-start w-full text-xs border-l max-sm:flex-col min-sm:flex-wrap border-black-borders')[0]

import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time 
import random

url = "https://bo3.gg/matches/furia-vs-mibr-12-05-2025"


match_data = {}
delay =

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)

    try:
        page.wait_for_selector('a.tournament', state="attached", timeout=10000)
        page.wait_for_selector('div.name', state="attached", timeout=10000)
    except Exception as e:
        print("Timeout waiting", e)
        browser.close()
        exit()

    html = page.content()

    soup = BeautifulSoup(html, "html.parser")

    tournament_tag = soup.find('a', class_='tournament')
    tournament_name = tournament_tag.find_all('span')[-1].text
    match_data["tournament"] = tournament_name

    teams = soup.find_all('div', class_="name") 
    match_data["team_a"] = teams[0].text
    match_data["team_b"] = teams[1].text

    status = soup.find('span', class_='status').text
    match_data["status"] = status


    dt = soup.find('div', class_="o-profile-sidebar__item").find_all('li', class_="o-list-bare__item")[0].find('p').text
    match_data["start_time"] = dt #TODO: convert to datetime object utc

    match_data["link"] = url
    match_data["match_id"] = url.split('/')[-1]

    games = soup.find_all('div', class_="c-nav-match-menu-item c-nav-match-menu-item--game c-nav-match-menu-item--finished")
    game_count = len(games)
    match_data["game_count"] = game_count


    game_idx = 0
    for game in games:
        map = game.find("div", class_="map-name").text.lower().strip()
        new_url = url + "/" + map
        page.goto(new_url)

        try:
            page.wait_for_selector('a.tournament', state="attached", timeout=10000)
            page.wait_for_selector('div.name', state="attached", timeout=10000)
            page.wait_for_selector('span.round__number', state="attached", timeout=15000)
        except Exception as e:
            print("Timeout waiting", e)
            browser.close()
            exit()

        game_html = page.content()
        soup = BeautifulSoup(game_html, "html.parser")
        game_idx += 1
        round_count = len(soup.find_all("span", class_="round__number"))
        match_data["game" + game_idx]["rounds"] = round_count
        match_data["game" + game_idx]["map"] = map

    print(match_data)

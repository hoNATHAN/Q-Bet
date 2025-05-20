from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time 
import random
import json

url = "https://bo3.gg/matches/furia-vs-mibr-12-05-2025"


match_data = {}
#delay =

def get_econ(table):
    team_econ_cells = table.find('div', class_="table-group").find_all("div", class_="table-cell money")
    team_econ = 0
    for row in team_econ_cells:
        money_str = row.find('p').text.replace('$', '').replace('\u00a0', '').strip()
        multiplier = 1 
        if money_str.endswith('K'):
            multiplier = 1000
            money_str = money_str[:-1]

        team_econ += int(float(money_str) * multiplier)
    return team_econ

def end_buy_phase(page):
    target_time="0:30"
    # Wait for the slider handle to appear
    slider = page.locator('div.c-field-slider__dot')

    # Get bounding box
    slider_box = slider.bounding_box()
    container = page.locator('div.c-field-slider__container')
    container_box = container.bounding_box()

    # Start from current position
    x = slider_box["x"] + slider_box["width"] / 2
    y = slider_box["y"] + slider_box["height"] / 2

    page.mouse.move(x, y)
    page.mouse.down()

    # Drag slowly to the right, checking after each step
    for offset in range(0, int(container_box["width"]), 5):
        page.mouse.move(x + offset, y)
        time.sleep(0.05)  # let DOM update
        current_time = slider.text_content()
        if current_time.strip() == target_time:
            break

    page.mouse.up()



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
        game_map = game.find("div", class_="map-name").text.lower().strip()
        new_url = url + "/" + game_map
        page.goto(new_url)

        try:
            page.wait_for_selector('a.tournament', state="attached", timeout=10000)
            page.wait_for_selector('div.name', state="attached", timeout=10000)
            page.wait_for_selector('span.round__number', state="attached", timeout=15000)
            page.wait_for_selector('div.o-table__body', state="attached", timeout=15000)
        except Exception as e:
            print("Timeout waiting", e)
            browser.close()
            exit()

        game_html = page.content()
        soup = BeautifulSoup(game_html, "html.parser")
        game_idx += 1
        match_data["game" + str(game_idx)] = {}
        round_count = len(soup.find_all("span", class_="round__number"))
        match_data["game" + str(game_idx)]["rounds"] = round_count
        match_data["game" + str(game_idx)]["map"] = game_map

        for i in range(round_count):
            round_url = new_url + "/round-" + str(i+1)
            page.goto(round_url)

            try:
                page.wait_for_selector('a.tournament', state="attached", timeout=10000)
                page.wait_for_selector('div.name', state="attached", timeout=10000)
                page.wait_for_selector('span.round__number', state="attached", timeout=15000)
                page.wait_for_selector('div.o-table__body', state="attached", timeout=15000)
                page.wait_for_selector('button.timeline__button', state="attached", timeout=15000)
            except Exception as e:
                print("Timeout waiting", e)
                browser.close()
                exit()

            game_html = page.content()
            soup = BeautifulSoup(game_html, "html.parser")

            tables = soup.find_all("div", class_="o-table__body")
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)] = {}
            team_a_table = tables[0]
            team_b_table = tables[1]

            team_a_kill_cells = team_a_table.find('div', class_="table-group").find_all("div", class_="table-cell kills")
            team_a_kills = 0
            for row in team_a_kill_cells:
                num = int(row.find('p').text)
                team_a_kills += num


            team_b_kill_cells = team_b_table.find('div', class_="table-group").find_all("div", class_="table-cell kills")
            team_b_kills = 0
            for row in team_b_kill_cells:
                num = int(row.find('p').text)
                team_b_kills += num

            final_team_a_econ = get_econ(team_a_table)
            final_team_b_econ = get_econ(team_b_table)

            #CLICK BUTTON
            page.click('button.timeline__button')

            time.sleep(0.5)
            page.click('button.timeline__button')

            #Scrape the initial econ
            game_html = page.content()
            soup = BeautifulSoup(game_html, "html.parser")
            tables = soup.find_all("div", class_="o-table__body")
            team_a_table = tables[0]
            team_b_table = tables[1]
            initial_team_a_econ = get_econ(team_a_table)
            initial_team_b_econ = get_econ(team_b_table)

            end_buy_phase(page)

            #Scrape the econ after buy phase
            game_html = page.content()
            soup = BeautifulSoup(game_html, "html.parser")
            tables = soup.find_all("div", class_="o-table__body")
            team_a_table = tables[0]
            team_b_table = tables[1]
            buy_team_a_econ = get_econ(team_a_table)
            buy_team_b_econ = get_econ(team_b_table)


            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["initial_team_a_econ"] = initial_team_a_econ
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["initial_team_b_econ"] = initial_team_b_econ
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["buy_team_a_econ"] = buy_team_a_econ
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["buy_team_b_econ"] = buy_team_b_econ
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["final_team_a_econ"] = final_team_a_econ
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["final_team_b_econ"] = final_team_b_econ

            if team_a_table.find('span', class_='winner-mark'):
                match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["winner"] = "Team A"
            elif team_b_table.find('span', class_='winner-mark'):
                match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["winner"] = "Team B"

            rounds = soup.find_all("a", class_="round")
            icon = rounds[i].find("i").get("class")[1]

            win_type = ""
            if icon == "o-icon--skull-2":
                win_type = "ace"
            elif icon == "o-icon--defuser":
                win_type = "defuse"
            elif icon == "o-icon--damage":
                win_type = "explode"
            elif icon == "o-icon--timer":
                win_type = "timeout"
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["win_type"] = win_type

            timestamps = soup.find_all("div", class_="timeline-label")
            duration = timestamps[-1].text.strip()
            minutes, seconds = map(int, duration.split(':'))
            total_seconds = minutes * 60 + seconds
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["duration"] = total_seconds

            team_a_diff = initial_team_a_econ - buy_team_a_econ
            team_a_buy_type = ""
            if team_a_diff >= 0 and team_a_diff <= 5000:
                team_a_buy_type = "Eco"
            elif team_a_diff > 5000 and team_a_diff <= 10000:
                team_a_buy_type = "Force"
            elif team_a_diff > 10000 and team_a_diff <= 20000:
                team_a_buy_type = "Semi"
            elif team_a_diff > 10000 and team_a_diff <= 20000:
                team_a_buy_type = "Full"
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["team_a_buy_type"] = team_a_buy_type

            team_b_diff = initial_team_b_econ - buy_team_b_econ
            team_b_buy_type = ""
            if team_b_diff >= 0 and team_b_diff <= 5000:
                team_b_buy_type = "Eco"
            elif team_b_diff > 5000 and team_b_diff <= 10000:
                team_b_buy_type = "Force"
            elif team_b_diff > 10000 and team_b_diff <= 20000:
                team_b_buy_type = "Semi"
            elif team_b_diff > 10000 and team_b_diff <= 20000:
                team_b_buy_type = "Full"
            match_data["game" + str(game_idx)]["round"+"_"+str(i+1)]["team_b_buy_type"] = team_b_buy_type


            break
        break

    print(json.dumps(match_data, indent=2))

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

def count_weapons(table):
    # find all weapon cells in the end‐of‐round table
    cells = table.find('div', class_='table-group') \
                 .find_all('div', class_='table-cell weapon')
    counts = {'AK': 0, 'M4': 0, 'AWP': 0}
    for cell in cells:
        icon = cell.find('i')
        if not icon:
            continue
        classes = icon.get('class', [])
        for cls in classes:
            cls_lower = cls.lower()
            # adjust these substrings to your site’s actual icon names
            if 'ak-47' in cls_lower or 'ak' in cls_lower:
                counts['AK'] += 1
                break
            elif 'm4a4' in cls_lower or 'm4a1' in cls_lower or 'm4' in cls_lower:
                counts['M4'] += 1
                break
            elif 'awp' in cls_lower:
                counts['AWP'] += 1
                break
    return counts

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
    tournament_name = tournament_tag.find_all('span')[-1].text # type: ignore
    match_data["tournament"] = tournament_name

    teams = soup.find_all('div', class_="name") 
    match_data["team_a"] = teams[0].text
    match_data["team_b"] = teams[1].text

    status = soup.find('span', class_='status').text # type: ignore
    match_data["status"] = status


    dt = soup.find('div', class_="o-profile-sidebar__item").find_all('li', class_="o-list-bare__item")[0].find('p').text # type: ignore
    match_data["start_time"] = dt #TODO: convert to datetime object utc

    match_data["link"] = url
    match_data["match_id"] = url.split('/')[-1]

    games = soup.find_all('div', class_='c-nav-match-menu-item c-nav-match-menu-item--game c-nav-match-menu-item--finished')  
    match_data['game_count'] = len(games)  

    for game_idx, game in enumerate(games, start=1):  
        game_map = game.find('div', class_='map-name').text.lower().strip()  
        new_url = f"{url}/{game_map}"  
        page.goto(new_url)  
        match_data[f'game{game_idx}'] = {'rounds': None, 'map': game_map}  
        game_score = {'a': 0, 'b': 0}  
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
        soup = BeautifulSoup(game_html, 'html.parser')  
        round_count = len(soup.find_all('span', class_='round__number'))  
        match_data[f'game{game_idx}']['rounds'] = round_count  
        match_data[f'game{game_idx}']['map'] = game_map  

        for i in range(round_count):  
            page.goto(f"{new_url}/round-{i+1}")  
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
            soup = BeautifulSoup(game_html, 'html.parser')  

            tables = soup.find_all('div', class_='o-table__body')  
            team_a_table, team_b_table = tables  

            final_a = get_econ(team_a_table)  
            final_b = get_econ(team_b_table)  

            page.click('button.timeline__button')  
            time.sleep(0.5)  
            page.click('button.timeline__button')  
            game_html = page.content()  
            soup = BeautifulSoup(game_html, 'html.parser')  
            tables = soup.find_all('div', class_='o-table__body')  
            init_a = get_econ(tables[0])  
            init_b = get_econ(tables[1])  

            end_buy_phase(page)  
            game_html = page.content()  
            soup = BeautifulSoup(game_html, 'html.parser')  
            tables = soup.find_all('div', class_='o-table__body')  
            buy_a = get_econ(tables[0])  
            buy_b = get_econ(tables[1])  

            if team_a_table.find('span', class_='winner-mark'):  
                winner = 'Team A'  
                game_score['a'] += 1  
            elif team_b_table.find('span', class_='winner-mark'):  
                winner = 'Team B'  
                game_score['b'] += 1  
            else:  
                winner = None  

            alive_a = len(team_a_table.select('.player--alive'))  
            alive_b = len(team_b_table.select('.player--alive'))  
            weap_a = count_weapons(team_a_table)  
            weap_b = count_weapons(team_b_table)  

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

            timestamps = soup.find_all("div", class_="timeline-label")
            duration = timestamps[-1].text.strip()
            minutes, seconds = map(int, duration.split(':'))
            total_seconds = minutes * 60 + seconds

            team_a_diff = init_a - buy_a
            team_a_buy_type = ""
            if team_a_diff >= 0 and team_a_diff <= 5000:
                team_a_buy_type = "Eco"
            elif team_a_diff > 5000 and team_a_diff <= 10000:
                team_a_buy_type = "Force"
            elif team_a_diff > 10000 and team_a_diff <= 20000:
                team_a_buy_type = "Semi"
            elif team_a_diff > 10000 and team_a_diff <= 20000:
                team_a_buy_type = "Full"

            team_b_diff = init_b - buy_b
            team_b_buy_type = ""
            if team_b_diff >= 0 and team_b_diff <= 5000:
                team_b_buy_type = "Eco"
            elif team_b_diff > 5000 and team_b_diff <= 10000:
                team_b_buy_type = "Force"
            elif team_b_diff > 10000 and team_b_diff <= 20000:
                team_b_buy_type = "Semi"
            elif team_b_diff > 10000 and team_b_diff <= 20000:
                team_b_buy_type = "Full"

            # count kills at end of round
            team_a_kill_cells = team_a_table.find('div', class_='table-group').find_all('div', class_='table-cell kills')
            team_a_kills = sum(int(cell.find('p').text) for cell in team_a_kill_cells)
            team_b_kill_cells = team_b_table.find('div', class_='table-group').find_all('div', class_='table-cell kills')
            team_b_kills = sum(int(cell.find('p').text) for cell in team_b_kill_cells)



            rd = {
                'initial_team_a_econ': init_a,
                'initial_team_b_econ': init_b,
                'final_team_a_econ': final_a,
                'final_team_b_econ': final_b,
                'winner': winner,
                'win_type': win_type,
                'duration': total_seconds,
                'team_a_buy_type': team_a_buy_type,
                'team_b_buy_type': team_b_buy_type,
                'score': f"{game_score['a']}-{game_score['b']}",
                'kills_end': {'team_a': team_a_kills, 'team_b': team_b_kills},
            }
            match_data[f'game{game_idx}'][f'round_{i+1}'] = rd  

        break

    print(json.dumps(match_data, indent=2))  
    with open('match_data.json', 'w') as f:  
        json.dump(match_data, f, indent=2)  

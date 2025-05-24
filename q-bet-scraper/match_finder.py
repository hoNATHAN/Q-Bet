from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time 
import random
import json

url = "https://www.oddsportal.com/esports/results/"
base_url = "https://www.oddsportal.com"
cs2_matches = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)

    try:
        page.wait_for_selector('div.flex', state="attached", timeout=10000)
    except Exception as e:
        print("Timeout waiting", e)
        browser.close()
        exit()

    html = page.content()

    soup = BeautifulSoup(html, "html.parser")

    match_list = soup.find_all('ul', class_='flex content-start w-full text-xs border-l max-sm:flex-col min-sm:flex-wrap border-black-borders')[0]
    a_tags = match_list.find_all('a')
    match_links = []

    for tag in a_tags:
        match_links.append(base_url + tag.get('href'))

    for link in match_links:
        page.goto(link)
        '''
        try:
            page.wait_for_selector('a.tournament', state="attached", timeout=10000)
            page.wait_for_selector('div.name', state="attached", timeout=10000)
            page.wait_for_selector('span.round__number', state="attached", timeout=15000)
            page.wait_for_selector('div.o-table__body', state="attached", timeout=15000)
        except Exception as e:
            print("Timeout waiting", e)
            browser.close()
            exit()
        '''
        html = page.content()
        match_data = BeautifulSoup(html, "html.parser")
        year_string = match_data.find('a', 'flex items-center justify-center h-8 px-3 bg-gray-medium cursor-pointer active-item-calendar').text
        try:
            year = int(year_string)
            if year >= 2024:
                cs2_matches.append(link)
        except ValueError:
            print("Error: " + year_string)
    print(cs2_matches)

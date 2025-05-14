import requests
from bs4 import BeautifulSoup

url = "https://bo3.gg/matches/furia-vs-mibr-12-05-2025"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup)

else:
    print("Status code not 200")

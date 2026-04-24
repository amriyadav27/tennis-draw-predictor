import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

url = "https://tennisabstract.com/reports/atp_elo_ratings.html"

conn = sqlite3.connect("/Users/amri/databases/tennis_data.db")
cursor = conn.cursor()
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table", {"class": "tablesorter"})
print(table)
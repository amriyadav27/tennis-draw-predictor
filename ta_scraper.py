import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from io import StringIO

url = "https://tennisabstract.com/reports/atp_elo_ratings.html"

conn = sqlite3.connect("/Users/amri/databases/tennis_data.db")
cursor = conn.cursor()
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", id="reportable")
df = pd.read_html(StringIO(str(table)))[0]

unnamed_columns_ls = [col for col in df.columns if "Unnamed" in col]
df = df.drop(columns=unnamed_columns_ls)

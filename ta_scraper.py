import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.tennisabstract.com/cgi-bin/leaders.cgi"

response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

table = soup.find("table")
df = pd.read_html(str(table))[0]

print(df.head())

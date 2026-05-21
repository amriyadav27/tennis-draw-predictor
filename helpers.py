import pdfplumber
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from io import StringIO
import sqlite3
from datetime import date

def parse_atp_draw(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()


def scrape_elo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="reportable")
    df = pd.read_html(StringIO(str(table)))[0]
    # Drop empty spacer columns
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, ~df.columns.str.strip().eq('')]
    df['snapshot_date'] = date.today().isoformat()
    df['tour'] = 'ATP' if 'atp' in url else 'WTA'
    return df

def save_to_db(df, db_path="tennis_elo.db"):
    conn = sqlite3.connect(db_path)
    df.to_sql("elo_ratings", conn, if_exists="append", index=False)
    conn.close()
    print(f"Saved {len(df)} rows for {df['snapshot_date'].iloc[0]}")

# Run for both tours
atp = scrape_elo("https://tennisabstract.com/reports/atp_elo_ratings.html")
wta = scrape_elo("https://tennisabstract.com/reports/wta_elo_ratings.html")

save_to_db(atp)
save_to_db(wta)
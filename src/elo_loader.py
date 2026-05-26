"""
Load and process Elo ratings from Tennis Abstract.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
from .utils import clean_name, get_last_name


ELO_COLS = {
    'overall': 'elo',
    'clay': 'celo',
    'hard': 'helo',
    'grass': 'gelo',
}


def load_elo(tour: str = 'atp') -> pd.DataFrame:
    """
    Scrape and process Elo ratings from Tennis Abstract.
    
    Args:
        tour: 'atp' or 'wta'
        
    Returns:
        DataFrame with player Elo ratings and metadata
    """
    url = f"https://tennisabstract.com/reports/{tour}_elo_ratings.html"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    table = soup.find("table", id="reportable")
    df = pd.read_html(StringIO(str(table)))[0]
    
    # Clean columns
    unnamed_columns_ls = [col for col in df.columns if "Unnamed" in col]
    df = df.drop(columns=unnamed_columns_ls)
    df.columns = df.columns.str.strip().str.lower().str.replace(r'[\s\xa0]+', '_', regex=True)
    
    # Convert types
    df['atp_rank'] = pd.to_numeric(df['atp_rank'], errors='coerce').astype('Int64')
    
    # Clean player names
    df['player_clean'] = df['player'].apply(clean_name)
    df['last_name'] = df['player_clean'].apply(get_last_name)
    
    # Process dates and form
    df['peak_month'] = pd.to_datetime(df['peak_month'])
    df["peak_delta"] = df["peak_month"].apply(
        lambda x: (pd.to_datetime("today").month - x.month) 
                  if pd.to_datetime("today").year == x.year
                  else (pd.to_datetime("today").year - x.year) * 12 + 
                        (pd.to_datetime("today").month - x.month)
    )
    
    from .utils import calculate_in_form
    df["in_form"] = df["peak_delta"].apply(calculate_in_form)
    
    return df

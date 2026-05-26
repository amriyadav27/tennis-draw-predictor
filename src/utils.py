"""
Utility functions for name cleaning and form calculations.
"""

import re


QUALIFIERS = {'WC', 'LL', 'Q', 'PR'}

COUNTRY_CODES = {
    'AFG','ALB','ALG','AND','ANG','ANT','ARG','ARM','AUS','AUT','AZE','BAH','BAN',
    'BAR','BLR','BEL','BEN','BER','BHU','BOL','BIH','BOT','BRA','BRN','BRU','BUL',
    'BUR','CAF','CAM','CAN','CAY','CGO','CHA','CHI','CHN','CIV','CMR','COD','COK',
    'COL','COM','CPV','CRC','CRO','CUB','CYP','CZE','DEN','DJI','DOM','ECU','EGY',
    'ERI','ESP','EST','ETH','FIJ','FIN','FRA','FSM','GAB','GAM','GBR','GEO','GEQ',
    'GER','GHA','GRE','GRN','GUA','GUI','GUM','GUY','HAI','HKG','HON','HUN','INA',
    'IND','IRI','IRL','IRQ','ISL','ISR','ISV','ITA','IVB','JAM','JOR','JPN','KAZ',
    'KEN','KGZ','KIR','KOR','KSA','KUW','LAO','LAT','LBA','LBN','LBR','LCA','LES',
    'LIE','LTU','LUX','MAD','MAR','MAS','MAW','MDA','MDV','MEX','MGL','MKD','MLI',
    'MLT','MNE','MON','MOZ','MRI','MTN','MYA','NAM','NCA','NED','NEP','NGR','NIG',
    'NOR','NRU','NZL','OMA','PAK','PAN','PAR','PER','PHI','PLE','PLW','PNG','POL',
    'POR','PRK','PUR','QAT','ROU','RSA','RUS','RWA','SAM','SEN','SEY','SGP','SKN',
    'SLE','SLO','SMR','SOL','SOM','SRB','SRI','SSD','STP','SUD','SUI','SUR','SVK',
    'SWZ','SYR','TAN','TGA','THA','TJK','TKM','TLS','TOG','TPE','TTO','TUN','TUR',
    'TUV','UAE','UGA','UKR','URU','USA','UZB','VEN','VIE','VIN','YEM','ZAM','ZIM',
}


def clean_name(name: str) -> str:
    """
    Clean player name by removing special characters and normalizing whitespace.
    
    Args:
        name: Player name string
        
    Returns:
        Cleaned name in lowercase
    """
    name = name.replace('\xa0', ' ')  # non-breaking space
    name = re.sub(r'[^\w\s]', '', name)  # remove punctuation
    name = re.sub(r'\s+', ' ', name)     # collapse multiple spaces
    return name.strip().lower()


def calculate_in_form(peak_delta: int) -> int:
    """
    Calculate in-form score based on months since peak Elo rating.
    
    Args:
        peak_delta: Number of months since peak Elo rating
        
    Returns:
        Form score from 1 (poor form) to 10 (excellent form)
    """
    if peak_delta <= 3:
        return 10
    elif peak_delta <= 6:
        return 8
    elif peak_delta <= 12:
        return 6
    elif peak_delta <= 18:
        return 4
    elif peak_delta <= 24:
        return 2
    else:
        return 1


def get_last_name(name: str) -> str:
    """
    Extract last name from player name.
    Handles both 'SINNER, Jannik' and 'Jannik Sinner' formats.
    
    Args:
        name: Player name string
        
    Returns:
        Last name in lowercase
    """
    name = clean_name(name)
    if ',' in name:
        return name.split(',')[0].strip()
    return name.split()[-1].strip()


def normalise_name(name: str) -> str:
    """
    Normalize player name to 'FirstName LastName' format.
    Converts 'SINNER, Jannik' to 'Jannik Sinner'.
    
    Args:
        name: Player name string
        
    Returns:
        Normalized name
    """
    name = name.strip()
    if ',' in name:
        parts = name.split(',', 1)
        name = parts[1].strip() + ' ' + parts[0].strip().title()
    return name.title()


def clean_player_name(name: str) -> str:
    """
    Remove extraneous characters from player name (coaches, birthdates, etc).
    
    Args:
        name: Player name string
        
    Returns:
        Cleaned player name
    """
    name = re.sub(r'\s+[A-Z]\.\s+\S+.*$', '', name)
    return name.rstrip('…').rstrip(',').strip()

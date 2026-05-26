"""
Match players from draws to Elo ratings using fuzzy matching.
"""

import pandas as pd
from rapidfuzz import process, fuzz
from .utils import clean_name, normalise_name, get_last_name


def match_player(draw_name: str, elo_df: pd.DataFrame) -> str | None:
    """
    Match a player name from the draw to an Elo rating record using fuzzy matching.
    
    Strategy:
    1. Try exact match on last name
    2. If multiple matches, use fuzzy matching on full name
    3. Fall back to full-name fuzzy matching across all players
    
    Args:
        draw_name: Player name from tournament draw
        elo_df: DataFrame of Elo ratings with 'last_name' and 'player_clean' columns
        
    Returns:
        Matched player name (player_clean), or None if no good match found
    """
    if draw_name.lower() == 'bye':
        return None
    
    last = get_last_name(draw_name)
    
    # Try last name match
    candidates = elo_df[elo_df['last_name'] == last]['player_clean'].tolist()
    
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        # Multiple players with same last name - fuzzy match full name
        normalised = clean_name(normalise_name(draw_name))
        match, score, _ = process.extractOne(normalised, candidates, scorer=fuzz.partial_ratio)
        return match if score >= 60 else None
    
    # No last name match - fall back to full name fuzzy matching
    normalised = clean_name(normalise_name(draw_name))
    match, score, _ = process.extractOne(
        normalised,
        elo_df['player_clean'].tolist(),
        scorer=fuzz.partial_ratio
    )
    return match if score >= 70 else None

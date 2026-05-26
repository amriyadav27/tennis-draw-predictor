"""
PDF draw parser for extracting tournament bracket information.
"""

import re
import pandas as pd
import pdfplumber
from .utils import QUALIFIERS, COUNTRY_CODES, clean_player_name


def get_draw_size(lines: list[str]) -> int:
    """
    Determine draw size from PDF lines.
    
    Args:
        lines: List of text lines from PDF
        
    Returns:
        Draw size (64, 128, 256, etc.)
    """
    positions = []
    for line in lines:
        m = re.match(r'^(\d{1,3})[\s]', line)
        if m:
            pos = int(m.group(1))
            if 1 <= pos <= 256:
                positions.append(pos)
    return max(positions) if positions else 64


def parse_line(line: str, draw_size: int) -> dict | None:
    """
    Parse a single line from the draw PDF into player information.
    
    Args:
        line: Text line from PDF
        draw_size: Size of the tournament draw
        
    Returns:
        Dictionary with draw_position, seed, qualifier, player, country, or None
    """
    if not line.strip():
        return None
    
    m = re.match(r'^(\d{1,3})(WC|LL|Q|PR|\s)', line)
    if not m:
        return None
    
    # Skip date lines and other non-player lines
    if re.search(r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)', line):
        return None
    if re.match(r'^\d{2}/\d{2}/\d{4}', line):
        return None

    line = re.sub(r'^(\d{1,3})(WC|LL|PR)', r'\1 \2', line)
    line = re.sub(r'^(\d{1,3})(Q)(\s)', r'\1 \2\3', line)

    tokens = line.split()
    try:
        pos = int(tokens[0])
    except ValueError:
        return None
    
    if pos < 1 or pos > draw_size or len(tokens) <= 2:
        return None
    
    if tokens[1] == 'Bye':
        return {
            'draw_position': pos,
            'seed': None,
            'qualifier': None,
            'player': 'Bye',
            'country': None
        }

    idx = 1
    seed, qualifier, country = None, None, None
    
    # Parse qualifier/wildcard status
    if idx < len(tokens) and tokens[idx] in QUALIFIERS:
        qualifier = tokens[idx]
        idx += 1
    
    # Parse seed
    if idx < len(tokens) and re.match(r'^\d{1,2}$', tokens[idx]):
        seed = int(tokens[idx])
        idx += 1

    # Parse player name and country
    name_tokens = []
    while idx < len(tokens):
        tok = tokens[idx]
        if re.match(r'^\d{2,3}$', tok) or tok == 'RET':
            break
        if tok in COUNTRY_CODES:
            country = tok
            idx += 1
            break
        name_tokens.append(tok)
        idx += 1

    if not name_tokens:
        return None
    
    player = clean_player_name(' '.join(name_tokens))
    return {
        'draw_position': pos,
        'seed': seed,
        'qualifier': qualifier,
        'player': player,
        'country': country
    } if player else None


def extract_draw(pdf_path: str) -> tuple[pd.DataFrame, int]:
    """
    Extract tournament draw from a PDF file.
    
    Args:
        pdf_path: Path to the draw PDF file
        
    Returns:
        Tuple of (DataFrame with player information, draw_size)
    """
    with pdfplumber.open(pdf_path) as pdf:
        all_lines = [line for page in pdf.pages for line in page.extract_text().split('\n')]
    
    draw_size = get_draw_size(all_lines)
    seen, entries = set(), []
    
    for line in all_lines:
        result = parse_line(line, draw_size)
        if result and result['draw_position'] not in seen:
            seen.add(result['draw_position'])
            entries.append(result)
    
    return pd.DataFrame(entries).sort_values('draw_position').reset_index(drop=True), draw_size

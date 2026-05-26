"""
Monte Carlo tournament simulation engine.
"""

import math
import numpy as np
import pandas as pd


def get_round_names(draw_size: int) -> list[str]:
    """
    Generate round names for a draw of given size.
    
    Args:
        draw_size: Number of players in draw (64, 128, 256, etc.)
        
    Returns:
        List of round names (e.g., ['R256', 'R128', 'R64', 'R32', 'R16', 'QF', 'SF', 'F', 'W'])
    """
    n_rounds = int(math.log2(draw_size))
    round_names = []
    
    for i in range(1, n_rounds + 1):
        remaining = draw_size // (2 ** (i - 1))
        if remaining == 2:
            round_names.append('F')
        elif remaining == 4:
            round_names.append('SF')
        elif remaining == 8:
            round_names.append('QF')
        else:
            round_names.append(f'R{remaining}')
    
    round_names.append('W')
    return round_names


def elo_win_prob(elo_a: float, elo_b: float) -> float:
    """
    Calculate probability that player A beats player B using Elo formula.
    
    Args:
        elo_a: Elo rating of player A
        elo_b: Elo rating of player B
        
    Returns:
        Probability (0-1) that player A wins
    """
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def simulate_tournament(
    df_draw: pd.DataFrame,
    elo_col: str = 'celo',
    n_simulations: int = 10000
) -> pd.DataFrame:
    """
    Run Monte Carlo simulation of tournament to calculate win probabilities.
    
    Args:
        df_draw: DataFrame with draw_position, player, country, and Elo rating columns
        elo_col: Name of Elo rating column to use (e.g., 'celo' for clay)
        n_simulations: Number of simulation iterations
        
    Returns:
        DataFrame with player and probability of reaching each round
    """
    # Get draw info
    draw_size = df_draw['draw_position'].max()
    players = df_draw.set_index('draw_position').to_dict('index')
    
    # Initialize results tracking
    round_names = get_round_names(draw_size)
    results = {pos: {round_name: 0 for round_name in round_names} for pos in players}
    
    # Run simulations
    for _ in range(n_simulations):
        alive = {pos: data for pos, data in players.items()}
        current_positions = list(range(1, draw_size + 1))
        
        for round_num in range(1, len(round_names)):
            round_name = round_names[round_num - 1]
            next_positions = []
            
            for i in range(0, len(current_positions), 2):
                pos_a = current_positions[i]
                pos_b = current_positions[i + 1]
                player_a = alive.get(pos_a)
                player_b = alive.get(pos_b)
                
                # Handle byes
                if player_a and player_a['player'] == 'Bye':
                    winner_pos, loser_pos = pos_b, pos_a
                elif player_b and player_b['player'] == 'Bye':
                    winner_pos, loser_pos = pos_a, pos_b
                else:
                    # Simulate match
                    elo_a = player_a[elo_col] if player_a and pd.notna(player_a[elo_col]) else 1500
                    elo_b = player_b[elo_col] if player_b and pd.notna(player_b[elo_col]) else 1500
                    prob_a = elo_win_prob(elo_a, elo_b)
                    
                    if np.random.random() < prob_a:
                        winner_pos, loser_pos = pos_a, pos_b
                    else:
                        winner_pos, loser_pos = pos_b, pos_a
                
                results[loser_pos][round_name] += 1
                next_positions.append(winner_pos)
            
            current_positions = next_positions
        
        # Winner of tournament
        results[current_positions[0]]['W'] += 1
    
    # Convert to probabilities
    output = []
    for pos, data in players.items():
        if data['player'] == 'Bye':
            continue
        
        row = {
            'player': data['player'],
            'seed': data['seed'],
            elo_col: data[elo_col],
        }
        
        for round_name in round_names:
            row[round_name] = results[pos].get(round_name, 0) / n_simulations
        
        output.append(row)
    
    return pd.DataFrame(output).sort_values('W', ascending=False).reset_index(drop=True)

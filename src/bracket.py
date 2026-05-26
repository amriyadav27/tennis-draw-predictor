"""
Generate optimal tournament bracket predictions from simulation results.
"""

import pandas as pd
from .simulator import get_round_names


def optimal_bracket(
    df_draw: pd.DataFrame,
    sim_results: pd.DataFrame,
    elo_col: str = 'celo'
) -> dict[str, pd.DataFrame]:
    """
    Generate optimal bracket by picking highest-probability winner of each match.
    
    Args:
        df_draw: Original draw DataFrame with draw_position and player columns
        sim_results: Simulation results DataFrame with win probabilities for each round
        elo_col: Name of Elo column (for round naming consistency)
        
    Returns:
        Dictionary mapping round names to DataFrames of matches and predicted winners
    """
    draw_size = df_draw['draw_position'].max()
    round_names = get_round_names(draw_size)
    
    # Build lookup of player -> win probability for each round
    prob_lookup = sim_results.set_index('player')[round_names].to_dict('index')
    
    # Initialize players
    players = df_draw.set_index('draw_position').to_dict('index')
    current_positions = [pos for pos in range(1, draw_size + 1)]
    
    bracket = {}
    
    # Process each round except final 'W'
    for round_num, round_name in enumerate(round_names[:-1]):
        round_matches = []
        next_positions = []
        
        for i in range(0, len(current_positions), 2):
            pos_a = current_positions[i]
            pos_b = current_positions[i + 1]
            player_a = players[pos_a]['player']
            player_b = players[pos_b]['player']
            
            # Handle byes
            if player_a == 'Bye':
                winner = player_b
                winner_pos = pos_b
            elif player_b == 'Bye':
                winner = player_a
                winner_pos = pos_a
            else:
                # Pick player with higher reach probability for next round
                next_round = round_names[round_num + 1]
                prob_a = prob_lookup.get(player_a, {}).get(next_round, 0)
                prob_b = prob_lookup.get(player_b, {}).get(next_round, 0)
                
                if prob_a >= prob_b:
                    winner, winner_pos = player_a, pos_a
                else:
                    winner, winner_pos = player_b, pos_b
                
                round_matches.append({
                    'match': f'{player_a} vs {player_b}',
                    'predicted_winner': winner,
                    'prob_a': round(prob_a * 100, 1),
                    'prob_b': round(prob_b * 100, 1),
                })
            
            # Update for next round
            players[pos_a] = players[winner_pos]
            next_positions.append(pos_a)
        
        bracket[round_name] = pd.DataFrame(round_matches)
        current_positions = next_positions
    
    return bracket


def bracket_to_csv(bracket: dict[str, pd.DataFrame], output_path: str = 'optimal_bracket.csv') -> pd.DataFrame:
    """
    Export bracket predictions to CSV file.
    
    Args:
        bracket: Dictionary of bracket DataFrames
        output_path: Path to write CSV file
        
    Returns:
        Combined DataFrame of all bracket predictions
    """
    dfs = []
    for round_name, matches in bracket.items():
        matches = matches.copy()
        matches['round'] = round_name
        dfs.append(matches)
    
    df_bracket = pd.concat(dfs, ignore_index=True)
    df_bracket = df_bracket[['round', 'match', 'predicted_winner', 'prob_a', 'prob_b']]
    df_bracket.to_csv(output_path, index=False)
    print(f"Saved bracket predictions to {output_path}")
    
    return df_bracket

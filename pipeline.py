#!/usr/bin/env python3
"""
Complete tournament prediction pipeline.

This script demonstrates how to use all modules together to:
1. Parse a tournament draw from a PDF
2. Load Elo ratings
3. Match players to ratings
4. Run Monte Carlo simulations
5. Generate optimal bracket predictions
"""

from src.draw_parser import extract_draw
from src.elo_loader import load_elo, ELO_COLS
from src.player_matcher import match_player
from src.simulator import simulate_tournament
from src.bracket import optimal_bracket, bracket_to_csv

def main():
    # Configuration
    draw_pdf = "draws/atp_draw_sample.pdf"
    tour = "atp"
    elo_surface = "clay"
    n_simulations = 10000
    
    # Step 1: Parse the draw
    print("Step 1: Parsing tournament draw...")
    df_draw, draw_size = extract_draw(draw_pdf)
    print(f"   ✓ Found {len(df_draw)} players in a {draw_size}-player draw")
    
    # Step 2: Load Elo ratings
    print("\nStep 2: Loading Elo ratings from Tennis Abstract...")
    elo_df = load_elo(tour)
    elo_col = ELO_COLS[elo_surface]
    print(f"   ✓ Loaded {len(elo_df)} player ratings")
    
    # Step 3: Match players
    print("\nStep 3: Matching players to ratings...")
    df_draw['matched_player'] = df_draw['player'].apply(lambda x: match_player(x, elo_df))
    matched = df_draw['matched_player'].notna().sum()
    print(f"   ✓ Matched {matched}/{len(df_draw)} players")
    
    # Merge draw with Elo data
    df_merged = df_draw.merge(
        elo_df[['player_clean', elo_col]],
        left_on='matched_player',
        right_on='player_clean',
        how='left'
    )
    df_merged = df_merged[[
        'draw_position', 'seed', 'qualifier', 'player', 'country', elo_col
    ]]
    
    # Step 4: Run simulations
    print(f"\nStep 4: Running {n_simulations:,} Monte Carlo simulations...")
    sim_results = simulate_tournament(df_merged, elo_col=elo_col, n_simulations=n_simulations)
    print(f"   ✓ Simulations complete")
    
    # Step 5: Generate optimal bracket
    print(f"\nStep 5: Generating optimal bracket predictions...")
    bracket = optimal_bracket(df_merged, sim_results, elo_col=elo_col)
    print(f"   ✓ Generated predictions for all rounds")
    
    # Save results
    print(f"\nSaving results...")
    sim_results.to_csv("sim_results.csv", index=False)
    bracket_to_csv(bracket, "optimal_bracket.csv")
    print(f"   ✓ Results saved to CSV files")
    
    # Display results
    print(f"\nComplete!")
    print(f"\nTop 5 contenders:")
    print(sim_results[['player', 'seed', elo_col, 'W']].head().to_string(index=False))
    
    if 'F' in bracket and not bracket['F'].empty:
        print(f"\nFinals Prediction:")
        print(bracket['F'][['match', 'predicted_winner', 'prob_a', 'prob_b']].to_string(index=False))

if __name__ == "__main__":
    main()

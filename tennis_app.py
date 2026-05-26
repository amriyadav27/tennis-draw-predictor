import streamlit as st
import pandas as pd
from src.draw_parser import extract_draw
from src.elo_loader import load_elo, ELO_COLS
from src.player_matcher import match_player
from src.simulator import simulate_tournament
from src.bracket import optimal_bracket, bracket_to_csv

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Tennis Draw Predictor",
    page_icon="🎾",
    layout="wide"
)

# ── Streamlit UI ─────────────────────────────────────────────
st.title("🎾 Tennis Draw Predictor")
st.caption("Upload a draw PDF and run a Monte Carlo simulation to predict match outcomes")

# Sidebar
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload draw PDF", type="pdf")
    tour = st.selectbox("Tour", ["ATP", "WTA"])
    elo_surface = st.selectbox("Elo surface", list(ELO_COLS.keys()))
    n_sims = st.select_slider("Simulations", options=[1000, 5000, 10000, 25000], value=10000)
    run_btn = st.button("Run simulation", type="primary", use_container_width=True)

if not uploaded_file:
    st.info("Upload a draw PDF in the sidebar to get started.")
    st.stop()

if run_btn:
    elo_col = ELO_COLS[elo_surface]

    with st.spinner("Parsing draw PDF..."):
        df_draw, _ = extract_draw(uploaded_file)

    with st.spinner("Loading Elo ratings from Tennis Abstract..."):
        elo_df = load_elo(tour.lower())

    with st.spinner("Matching players to Elo ratings..."):
        df_draw['matched_player'] = df_draw['player'].apply(lambda x: match_player(x, elo_df))
        df_merged = df_draw.merge(
            elo_df[['player_clean', elo_col]],
            left_on='matched_player', right_on='player_clean', how='left'
        )
        df_merged = df_merged[['draw_position', 'seed', 'qualifier', 'player', 'country', elo_col]]

    with st.spinner(f"Running {n_sims:,} simulations..."):
        sim_results = simulate_tournament(df_merged, elo_col=elo_col, n_simulations=n_sims)
        bracket = optimal_bracket(df_merged, sim_results, elo_col=elo_col)

    st.session_state['sim_results'] = sim_results
    st.session_state['bracket'] = bracket
    st.session_state['ran'] = True

if st.session_state.get('ran'):
    sim_results = st.session_state['sim_results']
    bracket = st.session_state['bracket']

    tab1, tab2 = st.tabs(["📊 Simulation Results", "🏆 Optimal Bracket"])

    with tab1:
        st.subheader("Player Win Probabilities")
        round_cols = [c for c in sim_results.columns if c not in ['player', 'seed', 'celo']]

        # Format as percentages
        display = sim_results.copy()
        for col in round_cols:
            display[col] = (display[col] * 100).round(1).astype(str) + '%'
        display['seed'] = display['seed'].fillna('-')

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "player": st.column_config.TextColumn("Player", width="medium"),
                "seed": st.column_config.TextColumn("Seed", width="small"),
                "celo": st.column_config.NumberColumn("Clay Elo", width="small"),
            }
        )

        st.download_button(
            "📥 Download CSV",
            sim_results.to_csv(index=False),
            "sim_results.csv",
            "text/csv"
        )

    with tab2:
        st.subheader("Optimal Bracket Picks")
        round_names = list(bracket.keys())

        for round_name in round_names:
            df_round = bracket[round_name]
            if df_round.empty:
                continue

            with st.expander(f"**{round_name}** — {len(df_round)} matches", expanded=(round_name in ['F', 'SF'])):
                st.dataframe(
                    df_round,
                    use_container_width=True,
                    hide_index=True,
                )

        # Full bracket CSV download
        all_rounds = []
        for round_name, df_round in bracket.items():
            if not df_round.empty:
                df_round_copy = df_round.copy()
                df_round_copy['round'] = round_name
                all_rounds.append(df_round_copy)

        if all_rounds:
            df_bracket = pd.concat(all_rounds, ignore_index=True)
            st.download_button(
                "📥 Download Full Bracket CSV",
                df_bracket.to_csv(index=False),
                "optimal_bracket.csv",
                "text/csv"
            )
# 🎾 Tennis Draw Predictor

Monte Carlo simulation for predicting tennis tournament outcomes using Elo ratings.

## Quick Start

### 1. Web App (Interactive)
```bash
streamlit run tennis_app.py
```
Upload a tournament draw PDF (or use the sample `draws/atp_draw_sample.pdf`) and run simulations in your browser.

### 2. Command Line (Automated)
```bash
python pipeline.py
```
Runs a complete prediction pipeline using the sample draw.

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Sample Data

A sample ATP draw is included in `draws/atp_draw_sample.pdf` for testing.

To use with other tournaments, download PDFs from:
- [ATP Tour](https://www.atptour.com) - ATP tournaments
- [WTA Tour](https://www.wtatennis.com) - WTA tournaments

Place PDFs in the `draws/` folder and run the app.

## Project Structure

```
src/                      # Core modules
├── utils.py              # Utilities & constants
├── draw_parser.py        # PDF parsing
├── elo_loader.py         # Elo rating loading
├── player_matcher.py     # Fuzzy name matching
├── simulator.py          # Monte Carlo engine
└── bracket.py            # Bracket generation

tennis_app.py             # Streamlit web app
pipeline.py               # CLI example script
playground_modular.ipynb  # Reference notebook
```

## Module API

### `src.draw_parser` - Parse PDFs
```python
from src.draw_parser import extract_draw

df_draw, draw_size = extract_draw(pdf_path: str)
```
**Returns:** DataFrame with `draw_position`, `seed`, `qualifier`, `player`, `country`

### `src.elo_loader` - Load Ratings
```python
from src.elo_loader import load_elo, ELO_COLS

elo_df = load_elo(tour: str = 'atp')
```
**Surfaces:** `'overall'` (elo), `'clay'` (celo), `'hard'` (helo), `'grass'` (gelo)

**Returns:** DataFrame with player ratings and metadata

### `src.player_matcher` - Match Players
```python
from src.player_matcher import match_player

matched_name = match_player(draw_name: str, elo_df: DataFrame)
```
**Strategy:** Last-name match → Full-name fuzzy match → Partial fuzzy match

### `src.simulator` - Run Simulations
```python
from src.simulator import simulate_tournament, get_round_names

results = simulate_tournament(
    df_draw: DataFrame,
    elo_col: str = 'celo',
    n_simulations: int = 10000
)
```
**Returns:** DataFrame with player names and probability of reaching each round

Example output:
```
player        | seed | celo | R64  | R32  | R16  | QF   | SF   | F    | W
Jannik Sinner | 1    | 2104 | 0.99 | 0.97 | 0.94 | 0.87 | 0.76 | 0.62 | 0.45
```

### `src.bracket` - Generate Predictions
```python
from src.bracket import optimal_bracket, bracket_to_csv

bracket = optimal_bracket(
    df_draw: DataFrame,
    sim_results: DataFrame,
    elo_col: str = 'celo'
)

bracket_to_csv(bracket, output_path: str)
```
**Returns:** Dictionary mapping round names to match DataFrames

### `src.utils` - Utilities
```python
from src.utils import (
    clean_name,
    normalise_name,
    get_last_name,
    calculate_in_form,
    COUNTRY_CODES,
    QUALIFIERS
)

# Examples
clean_name("Jannik SINNER")           # → "jannik sinner"
normalise_name("SINNER, Jannik")      # → "Jannik Sinner"
get_last_name("Jannik Sinner")        # → "sinner"
calculate_in_form(peak_delta=2)       # → 10 (excellent form)
```

## Configuration

### Elo Surface Selection
| Surface | Column | Tournaments |
|---------|--------|-------------|
| Clay | `celo` | Roland Garros, Monte Carlo, Buenos Aires |
| Hard | `helo` | Australian Open, US Open, Cincinnati |
| Grass | `gelo` | Wimbledon |
| Overall | `elo` | Mixed or unknown |

### Simulation Count
- **1,000 simulations** - Quick test (~2 seconds)
- **5,000 simulations** - Good balance (~10 seconds)
- **10,000 simulations** - Standard (~20 seconds)
- **25,000 simulations** - High accuracy (~50 seconds)

## Data Formats

### Input: Tournament Draw
```
draw_position | seed | qualifier | player        | country
1             | 1    | None      | Jannik Sinner | ITA
2             | None | Q         | Some Player   | USA
```

### Output: Simulation Results
```
player        | seed | celo | R64  | R32  | R16  | QF   | SF   | F    | W
Jannik Sinner | 1    | 2104 | 0.99 | 0.97 | 0.94 | 0.87 | 0.76 | 0.62 | 0.45
```

### Output: Bracket
```
round | match                           | predicted_winner  | prob_a | prob_b
R64   | Jannik Sinner vs Competitor     | Jannik Sinner     | 65.3   | 34.7
F     | Jannik Sinner vs Carlos Alcaraz| Carlos Alcaraz    | 45.2   | 54.8
```

## Dependencies

- pandas - Data manipulation
- requests - HTTP requests
- beautifulsoup4 - HTML parsing
- pdfplumber - PDF text extraction
- rapidfuzz - Fuzzy string matching
- streamlit - Web interface
- numpy - Numerical computing

## Features

✅ **PDF Draw Parsing** - Extract brackets from PDFs  
✅ **Real Elo Ratings** - From Tennis Abstract  
✅ **Monte Carlo Simulation** - 10,000+ runs  
✅ **Smart Matching** - Fuzzy name logic  
✅ **Surface-Specific** - Clay/hard/grass Elo  
✅ **Win Probabilities** - Per round per player  
✅ **Bracket Predictions** - Optimal match picks  
✅ **Export Results** - CSV downloads  
✅ **Web Interface** - Streamlit app  
✅ **Jupyter Support** - Interactive notebooks  

## License

See [LICENSE](LICENSE)

## Next Steps

1. **Start the app:** `streamlit run tennis_app.py`
2. **Run the pipeline:** `python pipeline.py` (for CLI usage)
3. **Upload a draw:** Use `draws/atp_draw_sample.pdf` or your own tournament PDF
4. **Explore the code:** Check out the `src/` modules for implementation details

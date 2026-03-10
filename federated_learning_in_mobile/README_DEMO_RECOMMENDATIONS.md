# Demo Recommendations Flow

This mobile app now includes a presentation-ready recommendation demo:

- Dashboard remains unchanged for training metrics and experiment controls.
- A separate `Movie Recommendations` screen shows ranked recommendations.
- `Demo Mode: Train and Show Recommendations` runs one round and navigates automatically.

## Data Source for Titles

Movie names are loaded from:

- `assets/movielens_titles.csv`

This file maps model `item_id` (0-based) to MovieLens titles.

## Quick Demo Steps

1. Connect to server in the dashboard.
2. Press `Demo Mode: Train and Show Recommendations`.
3. Show:
   - Dashboard logs and metrics
   - Recommendations screen with title, score explanation, seen/unseen status

## Rebuild title asset (optional)

Helper script:

- `tooling/build_movie_titles_asset.py`


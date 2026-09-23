import pandas as pd

print("Loading movies.csv...")
movies = pd.read_csv('data/processed/movies.csv')
movie_ids = set(movies['id'])

print("Loading cast_clean.csv...")
cast = pd.read_csv('data/processed/cast_clean.csv')

print(f"Before: {len(cast):,} rows")

# Keep only valid movie_ids
cast_valid = cast[cast['movie_id'].isin(movie_ids)]

print(f"After: {len(cast_valid):,} rows")
print(f"Removed: {len(cast) - len(cast_valid)} invalid rows")

print("Saving cast_final.csv...")
cast_valid.to_csv('data/processed/cast_final.csv', index=False)

print("✓ DONE! cast_final.csv created")
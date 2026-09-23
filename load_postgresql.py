import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

password = "Daddo09@"
password_encoded = quote_plus(password)
engine = create_engine(f'postgresql://postgres:{password_encoded}@localhost:5432/cinegraph')

print("="*80)
print("LOADING DATA - FINAL VERSION")
print("="*80)

# Clear tables
print("\nClearing tables...")
with engine.connect() as conn:
    conn.execute(text('TRUNCATE TABLE movie_genres CASCADE'))
    conn.execute(text('TRUNCATE TABLE "cast" CASCADE'))
    conn.execute(text('TRUNCATE TABLE movies CASCADE'))
    conn.execute(text('TRUNCATE TABLE actors CASCADE'))
    conn.execute(text('TRUNCATE TABLE genres CASCADE'))
    conn.commit()
print("✓ Tables cleared")

# Load movies
print("\nLoading movies...")
movies = pd.read_csv('data/processed/movies.csv')
with engine.connect() as conn:
    for _, row in movies.iterrows():
        date_val = None if pd.isna(row['release_date']) else row['release_date']
        budget_val = None if pd.isna(row['budget']) else row['budget']
        revenue_val = None if pd.isna(row['revenue']) else row['revenue']
        conn.execute(
            text('INSERT INTO movies (id, title, release_date, budget, revenue) VALUES (:id, :title, :date, :budget, :revenue)'),
            {'id': int(row['id']), 'title': row['title'], 'date': date_val, 'budget': budget_val, 'revenue': revenue_val}
        )
    conn.commit()
print(f"✓ Loaded {len(movies):,} movies")

# Load actors
print("\nLoading actors...")
actors = pd.read_csv('data/processed/actors.csv')
with engine.connect() as conn:
    for _, row in actors.iterrows():
        conn.execute(
            text('INSERT INTO actors (actor_id, actor_name) VALUES (:aid, :name)'),
            {'aid': int(row['actor_id']), 'name': row['actor_name']}
        )
    conn.commit()
print(f"✓ Loaded {len(actors):,} actors")

# Load genres
print("\nLoading genres...")
genres = pd.read_csv('data/processed/genres.csv')
with engine.connect() as conn:
    for _, row in genres.iterrows():
        conn.execute(
            text('INSERT INTO genres (genre_name) VALUES (:name)'),
            {'name': row['genre_name']}
        )
    conn.commit()
print(f"✓ Loaded {len(genres):,} genres")

# Load cast
print("\nLoading cast...")
cast = pd.read_csv('data/processed/cast.csv')
with engine.connect() as conn:
    for _, row in cast.iterrows():
        conn.execute(
            text('INSERT INTO "cast" (actor_id, movie_id, character) VALUES (:aid, :mid, :char)'),
            {'aid': int(row['actor_id']), 'mid': int(row['movie_id']), 'char': row['character']}
        )
    conn.commit()
print(f"✓ Loaded {len(cast):,} cast")

# Load movie_genres
print("\nLoading movie_genres...")
mg = pd.read_csv('data/processed/movie_genres.csv')
with engine.connect() as conn:
    for _, row in mg.iterrows():
        conn.execute(
            text('INSERT INTO movie_genres (movie_id, genre_name) VALUES (:mid, :genre)'),
            {'mid': int(row['movie_id']), 'genre': row['genre_name']}
        )
    conn.commit()
print(f"✓ Loaded {len(mg):,} movie_genres")

# Verify
print("\n" + "="*80)
print("VERIFICATION:")
print("="*80)
with engine.connect() as conn:
    for table in ['movies', 'actors', 'genres', '"cast"', 'movie_genres']:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
        count = result.scalar()
        print(f"✓ {table}: {count:,} rows")

print("\n✅ ALL DATA LOADED SUCCESSFULLY!")
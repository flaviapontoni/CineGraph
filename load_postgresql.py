import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

password = "Daddo09@"
password_encoded = quote_plus(password)
engine = create_engine(f'postgresql://postgres:{password_encoded}@localhost:5432/cinegraph')

print("\n" + "="*80)
print("LOADING ALL DATA INTO POSTGRESQL")
print("="*80)

print("\n[CLEANUP] Truncating all tables...")
with engine.connect() as conn:
    conn.execute(text('TRUNCATE TABLE movie_genres CASCADE'))
    conn.execute(text('TRUNCATE TABLE "cast" CASCADE'))
    conn.execute(text('TRUNCATE TABLE movies CASCADE'))
    conn.execute(text('TRUNCATE TABLE actors CASCADE'))
    conn.execute(text('TRUNCATE TABLE genres CASCADE'))
    conn.commit()
print("✓ Tables cleared")

files = [
    ('data/processed/movies.csv', 'movies'),
    ('data/processed/actors.csv', 'actors'),
    ('data/processed/genres.csv', 'genres'),
    ('data/processed/cast.csv', '"cast"'),
    ('data/processed/movie_genres.csv', 'movie_genres')
]

print("\n[LOADING] Inserting data...")
for filepath, table in files:
    df = pd.read_csv(filepath)
    with engine.connect() as conn:
        df.to_sql(table, conn, if_exists='append', index=False)
        conn.commit()
    print(f"✓ {filepath.split('/')[-1]} → {table} ({len(df):,} rows)")

print("\n" + "="*80)
print("ALL DATA LOADED SUCCESSFULLY!")
print("="*80 + "\n")

# Verify
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM "cast"'))
    count = result.scalar()
    print(f"VERIFICATION: cast table has {count:,} rows")
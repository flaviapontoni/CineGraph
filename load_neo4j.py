import pandas as pd
from neo4j import GraphDatabase

print("\n" + "="*80)
print("LOADING DATA INTO NEO4J (DIRECT PYTHON METHOD)")
print("="*80)

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Daddo09@"))

print("\n[1/5] Loading Actor nodes...")
df_actors = pd.read_csv('data/processed/actors.csv')
with driver.session(database="neo4j") as session:
    for _, row in df_actors.iterrows():
        session.run(
            "CREATE (:Actor {actor_id: $aid, name: $name})",
            aid=int(row['actor_id']),
            name=row['actor_name']
        )
print(f"✓ Created {len(df_actors):,} Actor nodes")

print("\n[2/5] Loading Movie nodes...")
df_movies = pd.read_csv('data/processed/movies.csv')
with driver.session(database="neo4j") as session:
    for _, row in df_movies.iterrows():
        session.run(
            "CREATE (:Movie {movie_id: $mid, title: $title})",
            mid=int(row['id']),
            title=row['title']
        )
print(f"✓ Created {len(df_movies):,} Movie nodes")

print("\n[3/5] Loading Genre nodes...")
df_genres = pd.read_csv('data/processed/genres.csv')
with driver.session(database="neo4j") as session:
    for _, row in df_genres.iterrows():
        session.run(
            "CREATE (:Genre {name: $gname})",
            gname=row['genre_name']
        )
print(f"✓ Created {len(df_genres):,} Genre nodes")

print("\n[4/5] Creating ACTED_IN relationships...")
df_cast = pd.read_csv('data/processed/cast.csv')
with driver.session(database="neo4j") as session:
    for _, row in df_cast.iterrows():
        session.run(
            "MATCH (a:Actor {actor_id: $aid}) MATCH (m:Movie {movie_id: $mid}) CREATE (a)-[:ACTED_IN {character: $char}]->(m)",
            aid=int(row['actor_id']),
            mid=int(row['movie_id']),
            char=row['character']
        )
print(f"✓ Created {len(df_cast):,} ACTED_IN relationships")

print("\n[5/5] Creating HAS_GENRE relationships...")
df_movie_genres = pd.read_csv('data/processed/movie_genres.csv')
with driver.session(database="neo4j") as session:
    for _, row in df_movie_genres.iterrows():
        session.run(
            "MATCH (m:Movie {movie_id: $mid}) MATCH (g:Genre {name: $gname}) CREATE (m)-[:HAS_GENRE]->(g)",
            mid=int(row['movie_id']),
            gname=row['genre_name']
        )
print(f"✓ Created {len(df_movie_genres):,} HAS_GENRE relationships")

driver.close()

print("\n" + "="*80)
print("NEO4J LOADING COMPLETE!")
print("="*80 + "\n")
# CineGraph: Analyzing Cinema Collaboration Networks
A comprehensive comparison of PostgreSQL (relational database) vs Neo4j (graph database) for analyzing actor collaboration networks.
Author: Maria Flavia Pontoni (Matricola: 2075265)
Course: Data Management 2025/2026 - Sapienza University of Rome
---
## Overview
This project compares two database paradigms for storing and querying network data: PostgreSQL 17 (Normalized relational tables with JOIN operations) and Neo4j (Native graph database with relationship-first storage). Using real movie dataset with 45K+ films and 122K+ actors, we benchmark 7 different query patterns to identify which database is better suited for different use cases.
Key Finding: PostgreSQL wins 6 out of 7 queries. Neo4j dominates only on unbounded-depth path traversal (shortest path: 726ms vs PostgreSQL: >15 minutes).
---
## Dataset
The Movies Dataset (Kaggle) - After cleaning and validation:
45,430 movies (id, title, release_date, budget, revenue)
122,437 actors (actor_id, actor_name)
347,115 cast credits (actor_id, movie_id, character)
20 genres
91,006 movie-genre relationships
---
## Data Models
### Relational Model (PostgreSQL)
movies (45,430 rows): id, title, release_date, budget, revenue
actors (122,437 rows): actor_id, actor_name
cast (347,115 rows): actor_id, movie_id, character [junction table]
genres (20 rows): genre_name
movie_genres (91,006 rows): movie_id, genre_name [junction table]
### Graph Model (Neo4j)
Nodes: Actor (122,437), Movie (45,430), Genre (20)
Relationships: ACTED_IN (347,115), HAS_GENRE (91,006)
Total: 167,887 nodes, 438,121 relationships
---
## Setup & Execution
### Prerequisites
Python 3.8+, PostgreSQL 17, Neo4j Desktop 2.1.4
Libraries: pandas, sqlalchemy, neo4j
### 1. Load Data into PostgreSQL
```bash
python load_postgresql.py
```
This script clears all existing tables, loads CSV files row-by-row with proper NULL handling, and verifies row counts. Uses row-by-row insertion with pd.isna() checks to avoid timestamp parsing errors on NULL dates.
### 2. Load Data into Neo4j
```bash
python load_neo4j.py
```
This script creates Actor, Movie, and Genre nodes, creates ACTED_IN and HAS_GENRE relationships, and loads all 347K+ relationships.
### 3. Run Queries
Execute queries from queries_postgresql.sql (pgAdmin Query Tool) and queries_neo4j.cypher (Neo4j Browser at http://localhost:7474)
---
## Query Benchmarks
| Query | PostgreSQL | Neo4j | Winner |
|-------|-----------|-------|--------|
| Genre distribution | ~460ms | 548ms | PostgreSQL |
| Actor collaboration pairs | ~2,420ms | 3,603ms | PostgreSQL |
| Actor productivity | 563ms | 1,474ms | PostgreSQL |
| Shortest path | >15 min (DNF) | 726ms | Neo4j |
| Centrality | 5,959ms | 6,221ms | PostgreSQL |
| Community detection | 2,051ms | 8,298ms | PostgreSQL |
| Recommendation | 1,100ms | 2,196ms | PostgreSQL |
Score: PostgreSQL 6/7, Neo4j 1/7
---
## Query Descriptions
### 1. Genre Distribution
Find the number of movies in each genre. PostgreSQL: 460ms | Neo4j: 548ms
```sql
SELECT g.genre_name, COUNT(DISTINCT mg.movie_id) as num_films FROM genres g LEFT JOIN movie_genres mg ON g.genre_name = mg.genre_name GROUP BY g.genre_name ORDER BY num_films DESC;
```
### 2. Actor Collaboration Pairs
Find the 20 most frequent co-starring pairs. PostgreSQL: 2,420ms | Neo4j: 3,603ms
```sql
SELECT a1.actor_name as actor1, a2.actor_name as actor2, COUNT(DISTINCT c1.movie_id) as movies_together FROM "cast" c1 JOIN "cast" c2 ON c1.movie_id = c2.movie_id JOIN actors a1 ON c1.actor_id = a1.actor_id JOIN actors a2 ON c2.actor_id = a2.actor_id WHERE c1.actor_id < c2.actor_id GROUP BY a1.actor_id, a1.actor_name, a2.actor_id, a2.actor_name ORDER BY movies_together DESC LIMIT 20;
```
### 3. Actor Productivity
Find the 20 most prolific actors (appeared in most films). PostgreSQL: 563ms | Neo4j: 1,474ms
```sql
SELECT a.actor_name, COUNT(DISTINCT c.movie_id) as films FROM actors a JOIN "cast" c ON a.actor_id = c.actor_id GROUP BY a.actor_id, a.actor_name ORDER BY films DESC LIMIT 20;
```
### 4. Shortest Path (GRAPH ADVANTAGE)
Find minimum degrees of separation between two actors (Shawn Dou → Christian Bale). PostgreSQL: >15 min (DNF) | Neo4j: 726ms
```sql
WITH RECURSIVE bfs AS (SELECT c.actor_id, ARRAY[c.actor_id] AS path, 0 AS depth FROM "cast" c WHERE c.actor_id = 145093 UNION SELECT c2.actor_id, bfs.path || c2.actor_id, bfs.depth + 1 FROM bfs JOIN "cast" c1 ON c1.actor_id = bfs.actor_id JOIN "cast" c2 ON c2.movie_id = c1.movie_id AND c2.actor_id <> c1.actor_id WHERE bfs.depth < 8 AND NOT c2.actor_id = ANY(bfs.path)) SELECT MIN(depth) FROM bfs WHERE actor_id = 14736;
```
Why PostgreSQL fails: Recursive CTE enumerates all simple paths combinatorially. No early-stop mechanism.
Why Neo4j wins: Native pointer traversal, shortest path returns immediately, cost scales with path length, not graph size.
### 5. Centrality (Degree Centrality)
Find the actor with the most distinct co-stars. PostgreSQL: 5,959ms | Neo4j: 6,221ms
```sql
SELECT a.actor_name, COUNT(DISTINCT c2.actor_id) AS centralita FROM "cast" c1 JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id <> c2.actor_id JOIN actors a ON a.actor_id = c1.actor_id GROUP BY a.actor_id, a.actor_name ORDER BY centralita DESC LIMIT 20;
```
Result (both engines agree): Christopher Lee with 873 distinct co-stars
### 6. Community Detection
Find tightly-connected actor triangles (≥5 shared films per pair). PostgreSQL: 2,051ms | Neo4j: 8,298ms
```sql
WITH strong_pairs AS (SELECT c1.actor_id AS a1, c2.actor_id AS a2, COUNT(DISTINCT c1.movie_id) AS shared FROM "cast" c1 JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id < c2.actor_id GROUP BY c1.actor_id, c2.actor_id HAVING COUNT(DISTINCT c1.movie_id) >= 5), triangles AS (SELECT sp1.a1, sp1.a2, sp2.a2 AS a3 FROM strong_pairs sp1 JOIN strong_pairs sp2 ON sp1.a2 = sp2.a1 JOIN strong_pairs sp3 ON sp1.a1 = sp3.a1 AND sp2.a2 = sp3.a2) SELECT n1.actor_name AS actor1, n2.actor_name AS actor2, n3.actor_name AS actor3 FROM triangles t JOIN actors n1 ON n1.actor_id = t.a1 JOIN actors n2 ON n2.actor_id = t.a2 JOIN actors n3 ON n3.actor_id = t.a3 LIMIT 20;
```
Example result: Mark Hamill, Harrison Ford, Carrie Fisher (Star Wars trio)
### 7. Recommendation
Suggest actors not yet worked with, via shared collaborators (collaborative filtering). PostgreSQL: 1,100ms | Neo4j: 2,196ms
```sql
WITH direct_collabs AS (SELECT DISTINCT c2.actor_id FROM "cast" c1 JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id <> c2.actor_id WHERE c1.actor_id = 145093), candidates AS (SELECT c2.actor_id AS rec_id, COUNT(DISTINCT c1.actor_id) AS score FROM "cast" c1 JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id <> c2.actor_id WHERE c1.actor_id IN (SELECT actor_id FROM direct_collabs) AND c2.actor_id NOT IN (SELECT actor_id FROM direct_collabs) AND c2.actor_id <> 145093 GROUP BY c2.actor_id) SELECT a.actor_name, c.score FROM candidates c JOIN actors a ON a.actor_id = c.rec_id ORDER BY c.score DESC LIMIT 20;
```
Top result: Andy Lau (score: 11 via shared collaborators)
---
## Key Insights
### PostgreSQL Wins When:
- Query depth is known and fixed (all 7 queries tested)
- Intermediate results can be pre-filtered and reused (community detection: 2,051ms vs 8,298ms)
- Relationships are reconstructed via fast JOINs on normalized keys
### Neo4j Wins When:
- Path length is unknown (shortest path: 726ms vs >15 minutes)
- Early-stop is critical (returns first shortest path immediately)
- Native traversal costs scale with path found, not graph size
### The Catch:
X Neo4j's advantage is specific, not general
X Being "graph-shaped" doesn't guarantee Neo4j wins (3 of 4 network queries favored PostgreSQL)
X Every query trades off: Neo4j skips JOINs but re-traverses from scratch at each hop
---
## Project Structure
CineGraph/
├── README.md (this file)
├── .gitignore
├── load_postgresql.py (ETL → PostgreSQL)
├── load_neo4j.py (ETL → Neo4j)
├── queries_postgresql.sql (7 benchmark queries)
├── queries_neo4j.cypher (7 queries in Cypher)
├── data/processed/
│   ├── actors.csv (122,437 rows)
│   ├── cast.csv (347,115 rows - cleaned)
│   ├── genres.csv (20 rows)
│   ├── movie_genres.csv (91,006 rows)
│   └── movies.csv (45,430 rows)
└── utilities/ (debugging & cleanup scripts)
    ├── clean_neo4j_complete.py
    ├── create_cast_final.py
    ├── fix_character_column.py
    └── cleanup_project.py
---
## Technical Notes
### PostgreSQL Issues Encountered & Solutions:
1. NaN values in release_date parsed as float → Fixed with pd.isna() checks, converting to None before INSERT
2. cast is a reserved keyword → Quoted as "cast" in all queries
3. character column too short (VARCHAR 255) → Changed to TEXT for unlimited length
### Neo4j Loading:
One-at-a-time node/relationship creation (slow but reliable). Total load time: ~1-2 hours for 167K nodes + 438K relationships. All data successfully loaded after cleanup script.
---
## Conclusions
The right database choice depends on the query pattern, not whether the data "looks like" a network.
Use PostgreSQL for: Analytics, fixed-depth queries, pre-filtered aggregations, and when your data is already normalized.
Use Neo4j for: Recommendation engines, shortest paths, variable-depth traversals, and when relationships are as important as nodes.
This project proves that a native graph database's advantage is narrow but decisive — it shines only when you actually need that advantage.
---
## References
Dataset: The Movies Dataset (Kaggle) - https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
PostgreSQL 17 Documentation
Neo4j Cypher Query Language Documentation
---

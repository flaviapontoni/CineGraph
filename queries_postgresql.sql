##Create Tables
-- Create Movies table
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    release_date DATE,
    budget NUMERIC,
    revenue NUMERIC
);

-- Create Actors table
CREATE TABLE actors (
    actor_id INTEGER PRIMARY KEY,
    actor_name VARCHAR(255) NOT NULL
);

-- Create Cast table (WITH QUOTES!)
CREATE TABLE "cast" (
    actor_id INTEGER REFERENCES actors(actor_id),
    movie_id INTEGER REFERENCES movies(id),
    character VARCHAR(255),
    PRIMARY KEY (actor_id, movie_id)
);

-- Create Genres table
CREATE TABLE genres (
    genre_name VARCHAR(100) PRIMARY KEY
);

-- Create Movie_Genres table
CREATE TABLE movie_genres (
    movie_id INTEGER REFERENCES movies(id),
    genre_name VARCHAR(100) REFERENCES genres(genre_name),
    PRIMARY KEY (movie_id, genre_name)
);

## Genre distribution
SELECT 
  g.genre_name,
  COUNT(DISTINCT mg.movie_id) as num_films
FROM genres g
LEFT JOIN movie_genres mg ON g.genre_name = mg.genre_name
GROUP BY g.genre_name
ORDER BY num_films DESC;

##actor productivity
SELECT 
  a.actor_name,
  COUNT(DISTINCT c.movie_id) as films
FROM actors a
JOIN "cast" c ON a.actor_id = c.actor_id
GROUP BY a.actor_id, a.actor_name
ORDER BY films DESC
LIMIT 20;

## Actor collaboration pairs
SELECT 
  a1.actor_name as actor1,
  a2.actor_name as actor2,
  COUNT(DISTINCT c1.movie_id) as movies_together
FROM "cast" c1
JOIN "cast" c2 ON c1.movie_id = c2.movie_id
JOIN actors a1 ON c1.actor_id = a1.actor_id
JOIN actors a2 ON c2.actor_id = a2.actor_id
WHERE c1.actor_id < c2.actor_id
GROUP BY a1.actor_id, a1.actor_name, a2.actor_id, a2.actor_name
ORDER BY movies_together DESC
LIMIT 20;

##shortest path

WITH RECURSIVE bfs AS (
  SELECT c.actor_id, ARRAY[c.actor_id] AS path, 0 AS depth
  FROM "cast" c WHERE c.actor_id = 145093
  UNION
  SELECT c2.actor_id, bfs.path || c2.actor_id, bfs.depth + 1
  FROM bfs
  JOIN "cast" c1 ON c1.actor_id = bfs.actor_id
  JOIN "cast" c2 ON c2.movie_id = c1.movie_id AND c2.actor_id <> c1.actor_id
  WHERE bfs.depth < 8 AND NOT c2.actor_id = ANY(bfs.path)
)
SELECT MIN(depth) FROM bfs WHERE actor_id = 14736;


## centrality 
SELECT a.actor_name, COUNT(DISTINCT c2.actor_id) AS centralita
FROM "cast" c1
JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id <> c2.actor_id
JOIN actors a ON a.actor_id = c1.actor_id
GROUP BY a.actor_id, a.actor_name
ORDER BY centralita DESC
LIMIT 20;

## raccomandation 
WITH direct_collabs AS (
  SELECT DISTINCT c2.actor_id
  FROM "cast" c1
  JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id <> c2.actor_id
  WHERE c1.actor_id = 145093
),
candidates AS (
  SELECT c2.actor_id AS rec_id, COUNT(DISTINCT c1.actor_id) AS score
  FROM "cast" c1
  JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id <> c2.actor_id
  WHERE c1.actor_id IN (SELECT actor_id FROM direct_collabs)
    AND c2.actor_id NOT IN (SELECT actor_id FROM direct_collabs)
    AND c2.actor_id <> 145093
  GROUP BY c2.actor_id
)
SELECT a.actor_name, c.score
FROM candidates c
JOIN actors a ON a.actor_id = c.rec_id
ORDER BY c.score DESC
LIMIT 20;

##community detection
WITH strong_pairs AS (
  SELECT c1.actor_id AS a1, c2.actor_id AS a2, COUNT(DISTINCT c1.movie_id) AS shared
  FROM "cast" c1
  JOIN "cast" c2 ON c1.movie_id = c2.movie_id AND c1.actor_id < c2.actor_id
  GROUP BY c1.actor_id, c2.actor_id
  HAVING COUNT(DISTINCT c1.movie_id) >= 5
),
triangles AS (
  SELECT sp1.a1, sp1.a2, sp2.a2 AS a3
  FROM strong_pairs sp1
  JOIN strong_pairs sp2 ON sp1.a2 = sp2.a1
  JOIN strong_pairs sp3 ON sp1.a1 = sp3.a1 AND sp2.a2 = sp3.a2
)
SELECT n1.actor_name AS actor1, n2.actor_name AS actor2, n3.actor_name AS actor3
FROM triangles t
JOIN actors n1 ON n1.actor_id = t.a1
JOIN actors n2 ON n2.actor_id = t.a2
JOIN actors n3 ON n3.actor_id = t.a3
LIMIT 20;
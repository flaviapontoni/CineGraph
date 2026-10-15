##Genre distribution
MATCH (g:Genre)<-[:HAS_GENRE]-(m:Movie)
WITH g, COUNT(DISTINCT m) as num_films
RETURN g.name, num_films
ORDER BY num_films DESC;


##actor productivity
MATCH (a:Actor)-[:ACTED_IN]->(m:Movie) 
WITH a, COUNT(DISTINCT m) as films 
RETURN a.name, films 
ORDER BY films DESC 
LIMIT 20


## Actor collaboration pairs
MATCH (a1:Actor)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(a2:Actor)
WHERE a1.actor_id < a2.actor_id
WITH a1, a2, COUNT(DISTINCT m) as movies_together
RETURN a1.name as actor1, a2.name as actor2, movies_together
ORDER BY movies_together DESC
LIMIT 20;


## Shortest path
MATCH (a1:Actor {actor_id: 145093}), (a2:Actor {actor_id: 14736})
MATCH p = shortestPath((a1)-[:ACTED_IN*..8]-(a2))
RETURN [n IN nodes(p) WHERE n:Actor | n.name] AS path,
       length(p)/2 AS degrees_of_separation


## centrality 
MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(a2:Actor)
WHERE a <> a2
WITH a, COUNT(DISTINCT a2) as centralita
RETURN a.name, centralita
ORDER BY centralita DESC
LIMIT 20;


## raccomandation 
MATCH (target:Actor {actor_id: 145093})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(collab:Actor)
WITH target, collab
MATCH (collab)-[:ACTED_IN]->(m2:Movie)<-[:ACTED_IN]-(candidate:Actor)
WHERE candidate <> target AND NOT (candidate)-[:ACTED_IN]->()<-[:ACTED_IN]-(target)
WITH candidate, COUNT(DISTINCT collab) as score
RETURN candidate.name, score
ORDER BY score DESC
LIMIT 20;


##community detection
MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Actor)
WHERE a.actor_id < b.actor_id
WITH a, b, COUNT(DISTINCT m) AS ab
WHERE ab >= 5
MATCH (b)-[:ACTED_IN]->(m2:Movie)<-[:ACTED_IN]-(c:Actor)
WHERE b.actor_id < c.actor_id
WITH a, b, c, COUNT(DISTINCT m2) AS bc
WHERE bc >= 5
MATCH (a)-[:ACTED_IN]->(m3:Movie)<-[:ACTED_IN]-(c)
WHERE a.actor_id < c.actor_id
WITH a, b, c, COUNT(DISTINCT m3) AS ac
WHERE ac >= 5
RETURN a.name, b.name, c.name
LIMIT 20
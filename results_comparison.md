# CineGraph: Query Performance Comparison

PostgreSQL vs Neo4j Benchmark Results

## Benchmark Summary

| Query | PostgreSQL | Neo4j | Winner | Difference |
|-------|-----------|-------|--------|-----------|
| Genre distribution | 460ms | 548ms | PostgreSQL | 88ms faster |
| Actor collaboration pairs | 2,420ms | 3,603ms | PostgreSQL | 1,183ms faster |
| Actor productivity | 563ms | 1,474ms | PostgreSQL | 911ms faster |
| Shortest path | >15 min (DNF) | 726ms | Neo4j | ~1,200x faster |
| Centrality (degree centrality) | 5,959ms | 6,221ms | PostgreSQL | 262ms faster |
| Community detection (triangles) | 2,051ms | 8,298ms | PostgreSQL | 6,247ms faster |
| Recommendation (collaborative) | 1,100ms | 2,196ms | PostgreSQL | 1,096ms faster |
| **SCORE** | **6/7 wins** | **1/7 wins** | **PostgreSQL** | |

## Detailed Analysis

### 1. Genre Distribution (460ms vs 548ms)

**PostgreSQL WINS: 88ms faster**

PostgreSQL executes a simple LEFT JOIN on two small tables (20 genres, 91K relationships). The query planner recognizes this as a trivial aggregation and uses sequential scan + group-by hash aggregation.

Neo4j traverses from Genre nodes to Movie nodes, collecting distinct movies per genre. The overhead of relationship traversal and property collection exceeds the speed advantage of native edges for this shallow, fixed-depth pattern.

**Takeaway:** Simple aggregations on normalized tables are PostgreSQL's sweet spot.

### 2. Actor Collaboration Pairs (2,420ms vs 3,603ms)

**PostgreSQL WINS: 1,183ms faster**

This query requires a self-join on the cast table (347K rows joined to itself), plus two actor name lookups. PostgreSQL's join optimizer recognizes this pattern and uses hash joins on the indexed actor_id columns.

Neo4j must traverse from each Actor through ACTED_IN edges to movies, then back through ACTED_IN to co-actors. The relationship traversal cost compounds for every pair evaluation.

**Takeaway:** Multi-join queries with indexed columns favor relational databases.

### 3. Actor Productivity (563ms vs 1,474ms)

**PostgreSQL WINS: 911ms faster**

Classic simple aggregation: count distinct movies per actor. PostgreSQL uses a single indexed join + group-by with streaming aggregation.

Neo4j traverses from each Actor to all ACTED_IN relationships and distinct Movie nodes, then counts. No intermediate filtering, so full traversal cost.

**Takeaway:** Shallow aggregations are PostgreSQL's strength; depth does not matter if depth is 1.

### 4. Shortest Path (>15 min vs 726ms)

**Neo4j WINS: ~1,200x faster**

This is the ONLY query where Neo4j's native advantage shines decisively.

**PostgreSQL Failure:** Recursive CTE with path array tracking. On each hop, the query self-joins the cast table, checks for cycles by testing array membership (NOT c2.actor_id = ANY(path)), and appends to the path array. With popular co-stars (e.g., actors in 100+ films), the number of candidate paths explodes combinatorially. At depth 5, a single actor might connect to 1,000+ paths; depth 6 → 100,000 paths. The CTE never finds an early-stop mechanism; it keeps expanding up to depth 8, exploring millions of paths before finally giving up.

**Neo4j Success:** Native shortestPath() traversal. The algorithm stops as soon as the first shortest path is found. Cost scales with path length (3 hops = fast), not with graph size. No cycle array, no path enumeration.

**Takeaway:** Unbounded-depth traversal is Neo4j's killer advantage. PostgreSQL is catastrophically bad here.

### 5. Centrality: Degree Centrality (5,959ms vs 6,221ms)

**PostgreSQL WINS: 262ms faster (barely)**

Both engines do the same logical work: for each actor, count distinct co-actors across all shared movies.

PostgreSQL uses a self-join on cast (same as pairs query) + aggregation. Neo4j traverses Actor → ACTED_IN → Movie → ACTED_IN → Actor, counting distinct neighbors.

The timing is nearly identical because both are fixed-depth (1 hop) with no uncertainty. PostgreSQL's join wins on raw throughput (indexed lookup + hash aggregation faster than traversal), but the advantage is marginal because both must process the full problem set.

**Takeaway:** Fixed-depth patterns converge in cost regardless of the engine. Join overhead + traversal overhead ≈ equivalent at shallow depths.

### 6. Community Detection: Triangles (2,051ms vs 8,298ms)

**PostgreSQL WINS: 6,247ms faster (4x advantage)**

This query demonstrates PostgreSQL's query optimization strength: pre-filtering and reuse.

**PostgreSQL Approach:**
1. Compute "strong_pairs" CTE once: filter cast to pairs with ≥5 shared films. Result: ~2,000 rows (out of 122M possible pairs).
2. Self-join the small strong_pairs table 3 times to close triangles.
3. Three small joins on a pre-filtered set.

**Neo4j Approach:**
1. MATCH clause 1: find pairs A-B with ≥5 shared films. No pre-filtering; re-filters the entire graph at each hop.
2. MATCH clause 2: expand to C via B, check threshold again.
3. MATCH clause 3: verify A-C threshold.
Each MATCH re-traverses from scratch; Cypher does not cache or pre-filter intermediate results in the same way.

**Result:** PostgreSQL materializes 2K rows once, joins them 3 times (fast). Neo4j re-traverses millions of relationship combos across 3 clauses (slow).

**Takeaway:** Relational query planners excel at identifying reducible computations and materializing them. Cypher's strength is pattern matching, not query optimization for pre-filtering.

### 7. Recommendation: Collaborative Filtering (1,100ms vs 2,196ms)

**PostgreSQL WINS: 1,096ms faster**

Similar pattern to centrality: fixed-depth (exactly 2 hops), no uncertainty.

PostgreSQL: Materialize direct_collabs (small set), then expand one more join and count supporters.

Neo4j: COLLECT into a list, UNWIND, then expand. UNWIND achieves the logical effect of pre-filtering, but without cost-based shrink-first optimization.

**Takeaway:** Two-hop patterns are fast in both engines, but PostgreSQL's CTE strategy edges ahead.

## Summary: Why PostgreSQL Wins 6/7

1. **Fixed-depth patterns are its domain.** Known depths → predictable costs → mature optimization.
2. **Pre-filtering and reuse exploit reducible computation.** CTEs materialize intermediate sets; relational planner recognizes them.
3. **Join speed on indexed columns is unmatched.** Hash joins on primary/foreign keys are extremely efficient.
4. **No relationship reconstruction overhead at query time.** Joins are native; edges are reconstructed once per query.

## Why Neo4j Wins Only 1/7 (But That 1 Is Decisive)

1. **Unbounded-depth traversal is its killer app.** When you don't know how many hops, Neo4j stops at the first shortest path. PostgreSQL enumerates all.
2. **Pointer-based traversal avoids join overhead.** Native edges skip the intermediate join/index lookup cost.
3. **Path finding is a solved problem in graph engines.** Shortest path algorithms are optimized for graphs; recursive CTEs are not.

Neo4j's advantage is **narrow but decisive.** It does not win on "graph-shaped" queries; it wins on **variable-depth queries where early-stop is possible.**

## Conclusions

- **Use PostgreSQL** if: data is normalized, queries have fixed/known depth, you need to pre-filter and reuse results, or your workload is primarily OLAP.
- **Use Neo4j** if: you need shortest-path, variable-depth traversal, or your entire domain is relationships (social graphs, recommendation paths).
- **The data shape does not determine the engine.** Cinema collaboration is "graph-shaped," yet PostgreSQL wins 6/7. Query patterns matter more than data shape.


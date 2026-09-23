from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Daddo09@"))

print("Deleting ALL nodes from Neo4j...")
with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    print("✓ All nodes deleted")

with driver.session() as session:
    result = session.run("MATCH (n) RETURN COUNT(n) as count")
    count = result.single()[0]
    print(f"✓ Nodes remaining: {count}")

driver.close()
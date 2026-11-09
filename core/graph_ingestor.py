import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import yaml
load_dotenv()

URI=os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD= os.getenv("NEO4J_PASSWORD")

if not URI or not PASSWORD:
    raise ValueError("Missing Neo4j URI or Password")

class CloudGraphIngestor:
    def __init__(self,URI,USER,PASSWORD,):
        self.driver=GraphDatabase.driver(URI,auth=(USER,PASSWORD))

    def close(self):
        self.driver.close()

    def parse_and_ingest_manifest(self, filepath: str):
        """Parses an infrastructure YAML manifest and pushes nodes and edges to Neo4j."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Manifest not found at {filepath}")

        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        with self.driver.session() as session:
            # Clear previous graph state for clean sync
            session.run("MATCH (n) DETACH DELETE n")

            for resource in data.get("resources", []):
                r_type = resource["type"]
                r_name = resource["name"]
                r_props = resource.get("properties", {})

                # Dynamic node creation using Cypher parameterization
                create_query = f"""
                MERGE (n:{r_type} {{name: $name}} )
                SET n += $props
                """
                session.run(create_query, name=r_name, props=r_props)

                # Process relationships if any
                for rel in resource.get("relationships", []):
                    target_name = rel["target"]
                    rel_type = rel["type"]
                    
                    rel_query = f"""
                    MATCH (source {{name: $source_name}})
                    MATCH (target {{name: $target_name}})
                    MERGE (source)-[:{rel_type}]->(target)
                    """
                    session.run(rel_query, source_name=r_name, target_name=target_name)

        print(f"Successfully parsed manifest from {filepath} and populated Neo4j graph!")

if __name__ == "__main__":
    print("Initializing ALAN Manifest Parser & Ingestor...")
    ingestor = CloudGraphIngestor(URI, USER, PASSWORD)
    try:
        ingestor.parse_and_ingest_manifest("configs/infra_manifest.yaml")
    finally:
        ingestor.close()
        print("Ingestion complete!")
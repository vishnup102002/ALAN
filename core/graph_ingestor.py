import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

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

    def test_connection(self):
        with self.driver.session() as session:
            result=session.run("RETURN 1 AS result")
            record =result.single()
            print(f"Neo4j Connection Status: Successful (Test Query Result: {record['result']}")

    def create_sample_attack_path(self):
        """Creates a sample vulnerable cloud topology for ALAN to audit."""
        query="""
        MERGE(i:IAMRole {name: 'OverprivilegedLambdaRole'})
        MERGE (s:S3Bucket {name: 'customer-pii-bucket', public: true})
        MERGE (ec2:EC2Instance {name: 'web-frontend-server', exposed_to_internet: true})
        
        MERGE (i)-[:HAS_ACCESS_TO]->(s)
        MERGE (ec2)-[:CONNECTS_TO]->(i)
        
        RETURN i.name AS role, s.name AS bucket
         """
        with self.driver.session() as session:
            session.run(query)
            print("Sample attack path topology injected into Neo4j graph!")
            
if __name__ == "__main__":
    ingestor = CloudGraphIngestor(URI, USER, PASSWORD)
    try:
        ingestor.test_connection()
        ingestor.create_sample_attack_path()
    finally:
        ingestor.close()
from neo4j._async.work import result
import os
from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()
URI=os.getenv("NEO4J_URI")
USER=os.getenv("NEO4J_USER")
PASSWORD=os.getenv("NEO4J_PASSWORD")

if not PASSWORD or not URI or not USER:
    raise ValueError("Missing Neo4j URI or Password or user")

mcp=FastMCP("ALAN Security Auditor")
def get_neo4j_driver():
    return GraphDatabase(URI,auth=(USER,PASSWORD))
@mcp.tool()
def audit_attack_paths() -> str:
    """Queries the local Neo4j graph for multi-hop attack paths involving internet-exposed EC2 instances and public S3 buckets."""
    query="""
    MATCH path = (ec2:EC2Instance{exposed_to_internet:true})-[CONNECTS_TO*1..3]->(i:IAMRole)-[HAS_ACCESS_TO]->(s:S3Bucket {public :true})
    RETURN ec2.name AS entrypoint, i.name AS compromised_role, s.name AS target_bucket
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        result=session.run(query)
        records=[dict[record] for record in result]
        driver.close()
        if not records:
            return "No critical multi-hop attack paths detected in the local graph."
        return f"CRITICAL VULNERABILITIES FOUND: {records}"
@mcp.tool()
def list_cloud_assets() -> str:
    """Lists all assets currently ingested in the air-gapped ALAN Neo4j graph database."""
    query="""
    MATCH (n)
    RETURN labels(n) AS assets_type, n.name AS name
    """
    driver=get_neo4j_driver()
    with driver.session as session:
        result=session.run(query)
        assets = [f"[{record['asset_type'][0]}] {record['name']}" for record in result]
        driver.close()
        if not assets:
            return "The graph database is currently empty."
        return "Ingested Cloud Assets:\n" + "\n".join(assets)


if __name__=="__main__":
    mcp.run()
    


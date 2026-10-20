import subprocess
from neo4j._async.work import result
import os
import json
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
    return GraphDatabase.driver(URI, auth=(USER, PASSWORD))
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
    query = """
    MATCH (n)
    RETURN labels(n) AS labels_list, n.name AS name
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(query)
        assets = []
        for record in result:
            labels = record.get("labels_list", ["Unknown"])
            label_str = labels[0] if labels else "Unknown"
            name = record.get("name", "Unnamed Asset")
            assets.append(f"[{label_str}] {name}")
        driver.close()
        if not assets:
            return "The graph database is currently empty."
        return "Ingested Cloud Assets:\n" + "\n".join(assets)

@mcp.tool()
def run_trivy_scan(target_path: str=".")->str:
    """Runs a local Trivy filesystem vulnerability scan on the specified target path and returns JSON findings."""
    try:
        cmd=["trivy","fs","--format","json","--quiet",target_path]    
        result=subprocess.run(cmd,capture_output=True,text=True,check=True)
        scan_data=json.loads(result.stdout)
        return json.dumps(scan_data, indent=2)
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": "Trivy scan failed", "details": e.stderr}, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse Trivy output as JSON", "raw_output": result.stdout}, indent=2)
    except Exception as ex:
        return json.dumps({"error": str(ex)}, indent=2)

@mcp.tool()
def run_checkov_scan(target_path: str=".")->str:
    """Runs a local Checkov IaC security and compliance scan against CIS benchmarks and returns JSON findings."""
    try:
        # Checkov outputs JSON and returns exit code 1 if failures/violations are found
        cmd=["checkov","-d",target_path,"--output","json","--quiet"]
        result=subprocess.run(cmd,capture_output=True,check=True)
        output_to_parse=result.stdout if result.stdout else result.stderr
        scan_data = json.loads(output_to_parse)
        return json.dumps(scan_data, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse Checkov output as JSON", "stdout": result.stdout, "stderr": result.stderr}, indent=2)
    except Exception as ex:
        return json.dumps({"error": str(ex)}, indent=2)


if __name__=="__main__":
    mcp.run()
    


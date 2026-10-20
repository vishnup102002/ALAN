# 📅 ALAN Project Master Sprint Roadmap

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  SPRINT 1       │ ──► │  SPRINT 2       │ ──► │  SPRINT 3       │ ──► │  SPRINT 4       │ ──► │  SPRINT 5       │
│  Data Ingestion │     │  Tooling (MCP)  │     │  Fine-Tuning    │     │  Orchestration  │     │  Multi-Eval     │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

### Sprint 1: Infrastructure Parsing & Graph Knowledge Base

* **Objective:** Set up the air-gapped environment and configure Neo4j to map multi-hop cloud attack paths.
* **Duration:** 3–4 Days

| Task ID        | Task Description                                                                                                                                     | Deliverable / Output                                                        |
| :------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| **T1.1** | Initialize local repository structure (`alan-auditor`), configure `.env` management, and establish GitHub repository.                            | Clean project directory and Git history.<br />Done ✅                       |
| **T1.2** | Write FastMCP security tool wrapper (`core/mcp_server.py`) for local Trivy and Checkov execution.                                                  | Standardized stdio FastMCP tool server.<br />Done ✅                        |
| **T1.3** | Provision **Neo4j Aura Free** instance and establish secure connection credentials.                                                            | Active cloud graph database cluster.<br />Done ✅ & done via neo4j docker  |
| **T1.4** | Design schema for cloud assets (`IAM Role`, `EC2 Instance`, `S3 Bucket`, `Security Group`) and relationships (`CONNECTS_TO`, `EXPOSES`). | Database schema definition document.<br />Done ✅                           |
| **T1.5** | Write parser logic to convert sample Terraform HCL / Kubernetes YAML manifests into graph nodes and edges.                                           | Ingestion script pushing topology to Neo4j.<br />Done ✅                    |

---

### Sprint 2: Deterministic Tooling & FastMCP Integration

* **Objective:** Expand open-source security CLI tools into standardized Model Context Protocol (FastMCP) endpoints and validate local execution.
* **Duration:** 3–4 Days

| Task ID        | Task Description                                                                                                                     | Deliverable / Output                            |
| :------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------- |
| **T2.1** | Install local security CLI scanners (`Trivy` for vulnerabilities, `Checkov` for IaC static compliance) in the local environment. | Working CLI command line binaries.<br />Done ✅ |
| **T2.2** | Implement MCP tool wrapper for Trivy filesystem scans to output clean JSON findings.                                                 | Functional `run_trivy_scan` tool endpoint.    |
| **T2.3** | Implement MCP tool wrapper for Checkov compliance checks against CIS benchmarks.                                                     | Functional `run_checkov_scan` tool endpoint.  |
| **T2.4** | Wire FastMCP server to local Claude Desktop via `claude_desktop_config.json` for manual tool verification.                         | End-to-end verified local MCP setup.            |

---

### Sprint 3: Model Fine-Tuning & vLLM Serving Setup

* **Objective:** Fine-tune `Qwen-2.5-7B-Coder` using Unsloth on Google Colab and deploy via vLLM with guided decoding.
* **Duration:** 4–5 Days

| Task ID        | Task Description                                                                                                 | Deliverable / Output                                                   |
| :------------- | :--------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------- |
| **T3.1** | Create synthetic instruction-tuning dataset mapping cloud security flaws to structured JSON remediation patches. | `security_remediation_dataset.json` file.                            |
| **T3.2** | Configure and run **Unsloth QLoRA** fine-tuning notebook on **Google Colab (Free T4 GPU)**.          | Saved LoRA adapter weights (`alan_adapter`).                         |
| **T3.3** | Merge adapter weights with base model and quantize to 4-bit AWQ format for efficient inference.                  | Optimized model artifacts.                                             |
| **T3.4** | Set up **vLLM** inference serving script enabling guided JSON decoding (`--enable-auto-tool-choice`).    | Running local OpenAI-compatible endpoint at `http://localhost:8000`. |

---

### Sprint 4: LangGraph Agentic Orchestration & Ledger

* **Objective:** Implement the state machine, append-only immutable ledger, and human-in-the-loop review workflow.
* **Duration:** 4–5 Days

| Task ID        | Task Description                                                                                                            | Deliverable / Output                       |
| :------------- | :-------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------- |
| **T4.1** | Architect **LangGraph** state machine connecting tool execution nodes with local vLLM reasoning nodes.                | Core agent topology graph.                 |
| **T4.2** | Build the custom immutable ledger reducer ensuring state transitions append delta changes without overwriting history.      | Append-only ledger state module.           |
| **T4.3** | Implement self-correction loop where parser or tool validation errors feed back into vLLM to regenerate patches.            | Automated error-healing cycle.             |
| **T4.4** | Build a Human-in-the-Loop review gate displaying generated Terraform git diffs for explicit user approval before execution. | Interactive CLI / Console approval prompt. |

---

### Sprint 5: Multi-Layered Evaluation, Benchmarking & Portfolio Polish

* **Objective:** Build the multi-tier evaluation harness (Deterministic, Retrieval, DeepEval, Latency) and publish the repository write-up.
* **Duration:** 3–4 Days

| Task ID        | Task Description                                                                                                                                  | Deliverable / Output                         |
| :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------- |
| **T5.1** | Implement deterministic unit tests (`evaluation/test_deterministic.py`) for Terraform AST and HCL patch validation.                             | Passing syntax validation test harness.      |
| **T5.2** | Build GraphRAG retrieval evaluation (`evaluation/test_retrieval.py`) calculating Precision@K and Recall@K on attack paths.                      | RAG precision report.                        |
| **T5.3** | Implement **DeepEval** test suite (`evaluation/test_deepeval.py`) measuring `FaithfulnessMetric` and `ToolCorrectnessMetric`.         | DeepEval test report.                        |
| **T5.4** | Write benchmark runner (`evaluation/benchmark_runner.py`) comparing fine-tuned ALAN against base models on TTFT latency and schema error rates. | Benchmark metrics report.                    |
| **T5.5** | Finalize repository documentation and record a short screen demonstration showcasing ALAN scanning a vulnerable config.                           | Portfolio video asset and public repository. |

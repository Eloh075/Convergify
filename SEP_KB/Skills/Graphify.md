# Graphify Skill

Graphify is a tool that maps your entire project (code, docs, PDFs, etc.) into a knowledge graph that AI agents can query instead of grepping through files.

## Installation
Requires Python 3.10+.
```bash
uv tool install graphifyy && graphify install
# or
pip install graphifyy && graphify install
```

## Core Command
```bash
graphify .
```
This generates:
- `graphify-out/graph.html` (interactive visualization)
- `graphify-out/GRAPH_REPORT.md` (summary report)
- `graphify-out/graph.json` (full graph data)

## AI Assistant Integration
Run this to make your assistant automatically consult the graph:
```bash
graphify antigravity install
```
*(Replace `antigravity` with your specific agent platform like `claude`, `cursor`, `aider`, etc. if applicable).*

## Querying the Graph
```bash
graphify query "what connects auth to the database?"
graphify path "UserService" "DatabasePool"
graphify explain "RateLimiter"
```

## Usage for Agents
Agents can build a graph of the workspace to better understand the implicit relationships across the entire codebase and knowledge base without individually reading every file.

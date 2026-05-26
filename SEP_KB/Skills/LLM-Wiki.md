# LLM Wiki Pattern

The LLM Wiki pattern is a structured way of building a personal knowledge base using an AI agent. 

## Key Principles
1. **Persistent Accumulation**: Unlike RAG where documents are retrieved on the fly, knowledge is incrementally synthesized into a structured graph of markdown files.
2. **AI-Maintained**: The human curates sources and asks questions; the AI does the summarizing, cross-referencing, and maintenance.
3. **Schema-Driven**: A configuration file (e.g., `AGENTS.md`) defines the workflows and conventions for the AI to follow.

## Operations
- **Ingest**: The AI reads a raw source, discusses takeaways, writes summary pages, and updates the `index.md` and `log.md`.
- **Query**: The human asks questions, and the AI answers using the wiki, often resulting in new synthesis pages added back to the wiki.
- **Lint**: Periodic health-checks to find contradictions, orphan pages, or missing cross-references.

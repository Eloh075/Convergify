# AGENTS Schema

## Introduction
This knowledge base follows the **LLM Wiki** pattern. It is designed to be maintained entirely by AI agents.

## Core Directives for Agents
1. **Never mutate raw sources**: Read from sources, but write only to wiki pages (summaries, concepts, indices).
2. **Always update `index.md`**: Whenever a new page is created, append an entry to `index.md` under the appropriate section.
3. **Always log actions**: Any ingest, query, or lint pass must be recorded chronologically in `log.md` using the format: `## [YYYY-MM-DD] <action> | <description>`.
4. **Use markdown cross-references**: Use double square brackets (Obsidian style) or standard relative markdown links to connect concepts. `[[Page Name]]` or `[[Page Name|Alias]]`.

## Directory Structure
- `/`: Core files like `index.md`, `log.md`, `AGENTS.md`.
- `/Skills/`: Instructions on tools and workflows for the agent.
- `/Sources/`: Parsed and transcribed versions of raw project documents.
- `/Concepts/`: Synthesized knowledge, entities, and topics based on sources.

## Tools
Agents have access to several skills/tools, documented in the `/Skills` directory:
- **MarkItDown**: For ingesting and transcribing `.pdf`, `.pptx`, `.docx` files.
- **Graphify**: For mapping codebase and documents into a searchable graph.

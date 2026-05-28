# Graph Report - SEP  (2026-05-26)

## Corpus Check
- 15 files · ~18,124 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 16 nodes · 15 edges · 4 communities (3 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8138dd29`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]

## God Nodes (most connected - your core abstractions)
1. `Convergify` - 10 edges
2. `Team Composition` - 3 edges
3. `Contact` - 3 edges
4. `Progress Updates` - 2 edges
5. `Overview` - 1 edges
6. `Pitch Video & Deck` - 1 edges
7. `Core Features` - 1 edges
8. `Current Status` - 1 edges
9. `Siva` - 1 edges
10. `Ethan` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities (4 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.25
Nodes (7): Convergify, Core Features, Current Status, Finance & Budget, Overview, Pitch Video & Deck, Product Roadmap & Next Steps

### Community 1 - "Community 1"
Cohesion: 0.67
Nodes (3): Ethan, Siva, Team Composition

### Community 2 - "Community 2"
Cohesion: 0.67
Nodes (3): Contact, Ethan, Siva

## Knowledge Gaps
- **11 isolated node(s):** `Overview`, `Pitch Video & Deck`, `Core Features`, `Current Status`, `Siva` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Convergify` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.933) - this node is a cross-community bridge._
- **Why does `Team Composition` connect `Community 1` to `Community 0`?**
  _High betweenness centrality (0.257) - this node is a cross-community bridge._
- **Why does `Contact` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.257) - this node is a cross-community bridge._
- **What connects `Overview`, `Pitch Video & Deck`, `Core Features` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
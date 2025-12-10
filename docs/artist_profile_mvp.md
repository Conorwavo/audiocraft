# Artist Profile MVP (Continuous Intelligence)

This MVP demonstrates how a universal artist profile can power multiple agents across the music value chain. It combines:

- **Public signals**: biography, links, streaming metrics, notable releases.
- **User intent**: goals, voice, target audience, milestones, collaboration preferences.
- **Private integrations**: DAW sessions, splits, contracts, management/distribution preferences.

The design favors **machine-readable views** (JSON, JSON-LD, agent-specific slices) while keeping a **human-friendly, visually rich** presentation for artists and teams.

## Running the demo

```bash
python demos/artist_profile_mvp.py
```

You will see:

- A **Markdown profile** suited for dashboards or emails.
- A **JSON-LD block** ready for knowledge graphs or search indexing.
- **Agent views** tuned for production, marketing, splits, contracting, and distribution agents.

## Data model highlights

- `PublicPresence`: surface-level identity and stats.
- `UserIntent`: human-supplied creative and business goals.
- `PrivateIntegrations`: DAW/project hooks, splits, and deal preferences.
- `ArtistProfile`: merges everything and can generate specialized views via `agent_view()`.

### Agent slices

- **Production**: genre focus, creative goals, DAW sessions (tempo, key, stems availability).
- **Marketing**: bio, audience, social links, streaming KPIs, milestones.
- **Splits**: contribution breakdown and management contacts.
- **Contracting**: legal/stage names plus preferred contract terms.
- **Distribution**: preferred distributors, catalogue, performance metrics.

## Extending the MVP

- Swap `demo_profile()` with your own data fetchers (public APIs, user forms, DAW bridges).
- Persist the JSON-LD to a graph store; attach embedding vectors for semantic search.
- Connect agent views to specialized tools (e.g., marketing copy generators, royalty calculators).
- Render the Markdown output in a UI; style it with your design system to maintain visual quality.

## Why continuous intelligence?

A single canonical profile feeds every agent with consistent facts, while each agent receives a **minimal, relevant slice**. This prevents drift between production, marketing, rights, and distribution workflows, and keeps human input central to the loop.

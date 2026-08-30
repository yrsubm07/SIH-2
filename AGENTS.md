# AI Agent Instructions — MetrIQ / SIH 26034

Read `README.md` before making changes.

## Non-negotiable architecture

- `app.py` is the Streamlit presentation/workflow layer.
- `rules.py` is the deterministic compliance layer.
- Do not move legal decision logic into an LLM prompt.
- AI/OCR may extract evidence; rules decide the screening outcome.
- Preserve the built-in demo fallback so the project remains demoable without external API keys.

## Safety and legal accuracy

- This is a prototype, not an authoritative legal decision system.
- Verify every new legal rule against the current official Department of Consumer Affairs source before encoding it.
- Store rule IDs, versions, applicability, exceptions and source references.
- If an image cannot support reliable measurement, return REVIEW / physical verification rather than inventing precision.

## Development workflow

1. Inspect current files.
2. Make the smallest coherent change.
3. Keep dependencies justified and lightweight.
4. Do not commit secrets, `.env` files, API keys or credentials.
5. Update README when commands, architecture or major features change.
6. Prefer feature branches; avoid destructive rewrites of `main`.
7. Test `streamlit run app.py` after UI changes when the environment allows it.

## Product direction

Prioritize these upgrades in order:

1. OCR bounding boxes and declaration highlighting.
2. Better document/layout analysis.
3. Calibrated font/character-height estimation.
4. Multi-image package inspection.
5. E-commerce listing vs package comparison.
6. Persistent PostgreSQL/object-storage inspection repository.
7. RBAC, audit logs and signed reports.

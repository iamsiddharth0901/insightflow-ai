# Architecture notes

This MVP implements the architectural brief's core loop: typed query understanding → bounded plan → safe read-only SQL → deterministic calculations → document retrieval → structured, cited response. It uses SQLite and lexical retrieval locally so it can run without services or model downloads.

Production adapters are intentionally isolated. Replace `app/db/database.py` with SQLAlchemy/PostgreSQL and `app/tools/rag/retriever.py` with FAISS/Qdrant plus embeddings. A Hugging Face structured-output client can be introduced behind the query/synthesis seams while retaining deterministic numerical functions and verification gates.

The seed data contains a deliberate Q3 2026 South decline in Atlas and Beacon. The business reports mention a campaign ending and competitor discount as hypotheses, while SQL-derived revenue figures remain verified facts.

# FindMyGap Backend


```
backend/app/
├── utils/                      # Pure utility functions (stateless)
│   ├── database.py            # Database utilities
│   └── schema.py              # Schema formatting utilities
│
├── database/                   # Database layer
│   ├── models/                # SQLAlchemy models
│   ├── repositories/          # Repository pattern (one per table)
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── dataset.py
│   │   ├── review.py
│   │   └── ...
│   ├── base.py
│   └── session.py
│
├── core/                       # Core functionality
│   ├── llm/                   # LLM-related code
│   │   └── metadata_generator.py
│   ├── config/
│   ├── security/
│   └── ...
│
├── services/                   # Business logic orchestration
│   ├── data_ingestion_service.py
│   ├── schema_service.py
│   └── ...
│
└── workflows/                  # Specific workflows only
    ├── product_gap_workflow_refactored.py
    ├── agents/
    ├── steps/
    └── teams/
```
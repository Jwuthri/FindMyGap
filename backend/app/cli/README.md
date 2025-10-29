# CLI Usage

## Installation

```bash
cd backend
pip install click
```

## Commands

### Initialize Database
```bash
python -m app.cli.main init-db
```

### Ingest Mock Data
```bash
python -m app.cli.main ingest-mock
```

### Ingest File
```bash
python -m app.cli.main ingest-file path/to/file.csv --user-id user_123
```

### View Schemas
```bash
python -m app.cli.main view-schemas
python -m app.cli.main view-schemas --user-id user_123
```

### Setup Platform Datasets
```bash
python -m app.cli.main setup-platform
```

## Help
```bash
python -m app.cli.main --help
python -m app.cli.main init-db --help
```

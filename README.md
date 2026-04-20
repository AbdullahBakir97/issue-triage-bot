# Issue Triage Bot

A GitHub App that auto-categorizes, labels, and routes GitHub issues using intelligent keyword analysis.

## Features

- **Auto-Categorization** — Detects issue type (bug, feature, question, docs, enhancement, support)
- **Priority Detection** — Assigns P0-P4 priority based on severity keywords
- **Completeness Check** — Verifies bug reports include required sections
- **Duplicate Detection** — Finds potential duplicates via keyword overlap
- **Auto-Response** — Posts template comments for incomplete/duplicate/good reports
- **Configurable** — Per-repo config via `.github/triage-bot.yml`

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-username/issue-triage-bot.git
cd issue-triage-bot
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your GitHub App credentials

# Run
python -m src.main
```

## Architecture

Clean Architecture with clear separation of concerns:

```
src/
├── domain/          # Entities, enums, interfaces, exceptions
├── analyzers/       # Categorizer, priority, completeness, duplicates
├── generators/      # Comment builder, label manager
├── application/     # Orchestrator, webhook handler
├── infrastructure/  # GitHub client, auth, config loader
├── api/             # FastAPI routes, middleware, schemas
└── config/          # Settings, logging
```

## Configuration

Create `.github/triage-bot.yml` in your repository:

```yaml
enabled: true
auto_label: true
auto_comment: true
auto_assign: false
require_reproduction_steps: true
duplicate_threshold: 0.6
assignees:
  bug: [maintainer1]
  feature: [maintainer2]
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/webhook` | GitHub webhook receiver |
| POST | `/api/analyze` | Demo analysis endpoint |
| GET | `/dashboard` | Web dashboard |

## Development

```bash
# Lint
ruff check .
ruff format .

# Type check
mypy src/

# Test
pytest --cov=src
```

## Deployment

### Render

The included `render.yaml` configures deployment on Render. Set environment variables in the Render dashboard.

### Docker

```bash
docker build -t issue-triage-bot .
docker run -p 8000:8000 --env-file .env issue-triage-bot
```

## License

MIT License - Abdullah Bakir 2026

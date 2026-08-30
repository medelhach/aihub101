# AI Intelligence Site (30 August 2026)

Isolated project for the public AI website. It is separate from the older AI Intelligence Hub foundation in the parent folder.

## Sections

- News — automated briefs from established AI publishers
- Articles — lab, cloud, and research feeds
- AI Models — 50+ structured model profiles
- Compare — side-by-side model dashboard

## Run

```bash
docker compose up --build
```

- Web: http://localhost:3000
- API: http://localhost:8000

Force one ingestion cycle:

```bash
docker compose exec backend python -m app.workers.content_cycle --once
```

Install frontend dependencies once if you run Next.js outside Docker:

```bash
cd frontend
npm install
```

# HD Platform

**API, Reports, and Managed MCP Hosting for Human Design** — powered by [OpenHumanDesignMCP](https://github.com/mbgulden/OpenHumanDesignMCP).

## Products

| Product | Status | Pricing |
|---|---|---|
| **HD Cloud API** | 🚧 Building | $19–$999/mo |
| **Deep Dive Reports** | 📋 Planned | $19–$59 one-time |
| **Managed MCP Hosting** | 📋 Planned | $29–$199/mo |
| **HD Academy** | 🚧 MVP catalog + landing page | $97–$1,997 / $49/mo |

## Architecture

```
hd-platform/
├── api/           # FastAPI REST service (HD Cloud API)
├── reports/       # Report generation pipeline (Deep Dive Reports)
├── hosting/       # MCP provisioning service (Managed MCP Hosting)
├── data/academy/  # File-backed HD Academy course catalog
├── shared/        # Common code: DB models, Stripe, MCP client
├── docker/        # Docker Compose for full stack deployment
└── docs/          # Architecture, task board, API docs
```

## HD Academy MVP

- Landing page: `docs/academy/index.html`
- Public catalog API: `GET /v1/academy`
- Course detail API: `GET /v1/academy/courses/hd-fundamentals`
- Source of truth: `data/academy/catalog.json`

The launch offer is **HD Fundamentals: Read Any Chart in 30 Days** at **$97**.
The next production step is adding Gumroad or Stripe checkout URLs to each course
slug after payment links exist.

## Quick Start

```bash
# Clone with engine dependency
git clone https://github.com/mbgulden/hd-platform.git
cd hd-platform
git clone https://github.com/mbgulden/OpenHumanDesignMCP.git ../OpenHumanDesignMCP

# Set environment variables
cp .env.example .env
# Edit .env with your keys

# Deploy
docker compose -f docker/docker-compose.yml up -d
```

## Trust & Verification

- Engine verified against **Neutrino Design app** for 5 real charts
- Type, Profile, Authority, Centers, Channels, and Variable arrows match
- Methodology: [OpenHumanDesignMCP](https://github.com/mbgulden/OpenHumanDesignMCP) — open source, auditable
- Powered by **Light Filled Human Design** certification

## License

AGPLv3 — free software. Managed hosting and API access available commercially.

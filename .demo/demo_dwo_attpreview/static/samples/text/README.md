# Northwind Catalogue API

A small service that publishes the **Northwind Garden Supplies** catalogue to the shops.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m catalogue.server --port 8080
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | List products, paged |
| GET | `/products/<id>` | One product with its stock |
| POST | `/orders` | Create an order |

## Configuration

Settings live in `settings.yaml`. Environment variables override them:

- `CATALOGUE_DB`: database URL
- `CATALOGUE_CACHE`: cache time in seconds (default `60`)

> **Note**
> Prices are in EUR and include tax.

### Release checklist

1. Run the tests
2. Update `CHANGELOG.md`
3. Tag the release

See also [the plan](docs/plan/milestones.md).

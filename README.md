<p align="center">
  <a href="https://rankr.online"><img src="https://raw.githubusercontent.com/pmsoltani/rankr/master/frontend/src/assets/images/appLogo.svg" height="100" alt="rankr logo"></a>
</p>

# [rankr](https://rankr.online)

**rankr** is a platform for aggregating the results of different academic rankings.

## What does it do?

rankr crawls university ranking tables and aggregates the results. It currently supports [QS](https://www.topuniversities.com/), [Shanghai (ARWU)](http://www.shanghairanking.com), and [Times Higher Education (THE)](https://www.timeshighereducation.com) world university rankings.

To aggregate results across ranking systems, rankr needs a shared identity for each institution. It uses [ROR](https://ror.org) (the Research Organization Registry), a free, open database of ~100,000 research organizations; for example, the ROR ID for MIT is `042nb2s44`.

rankr loads the entire ROR data dump into a local SQLite database (via `SQLAlchemy`), then for each crawled ranking row tries to match the institution to its ROR record using, in order:

- a manual overrides file (`matches.json`).
- the institution's profile URL in the ranking table;
- an exact name + country match;
- ROR's [affiliation-matching API](https://ror.readme.io/docs/api-affiliation); and
- fuzzy matching;

ROR metadata wins on any discrepancy, i.e., if a ranking lists an institution under `Country A` but ROR records `Country B`, `Country B` is used.

## Architecture

- **backend/** — a Python CLI (`uv`, `Typer`, `SQLAlchemy`, `requests`, and `Pydantic`) that crawls the rankings and builds `data/rankr.sqlite`.
- **frontend/** — an `Astro` site (with `shadcn/ui` components) deployed to `Cloudflare Workers`. Because the data only changes when the crawler re-runs, the whole site is **prerendered at build time** from `rankr.sqlite` and served as static assets. Nothing queries a database at request time.

Migrating from the previous `FastAPI`/`PostgreSQL` and `ReactJS` stack to the current architecture reduced hosting costs and enhanced performance.

### Publishing new results

`backend/data/rankr.sqlite` is the single source of truth. After a re-crawl:

```bash
cd frontend
bun run logos   # only if new institutions appeared
bun run deploy  # projects the data, prerenders the pages, verifies, deploys
```

New years, new institutions, the year selector, the search corpus and the sitemap are all derived from the data. Adding a whole new _ranking system_ is the one manual step (an entry in `RANKING_SYSTEMS` in `frontend/src/lib/site.ts`).

See [frontend/cloudflare-deploy.md](frontend/cloudflare-deploy.md) for the full runbook, including `bun run report` for traffic reports.

## Updates

**rankr** is in archive mode. It is no longer actively maintained, and the data is not updated.

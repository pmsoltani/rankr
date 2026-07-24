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
- **frontend/** — an `Astro` SSR site (with `shadcn/ui` components) deployed to `Cloudflare Workers`, reading from `Cloudflare D1`. D1 is a slimmed projection of `rankr.sqlite`: ranked institutions only, with the per-metric ranking rows collapsed into a single JSON column.

Migrating from the previous `FastAPI`/`PostgreSQL` and `ReactJS` stack to the current architecture reduced hosting costs and enhanced performance.

## Updates

**rankr** is in archive mode. It is no longer actively maintained, and the data is not updated.

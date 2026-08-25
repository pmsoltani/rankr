# Cloudflare deploy runbook

The frontend deploys as a **Cloudflare Worker with static assets** via `wrangler deploy` (not Git-connected). Cloudflare never watches a branch; you push the built bundle with a command from whatever is checked out.

The **entire site is prerendered at build time** from the crawler's SQLite. Ranking tables, institution profiles, the sitemap, the search corpus and the Compare payloads are all static files, served by Cloudflare's asset layer without invoking the Worker. There is no D1 binding at all.

All commands run from `frontend/`.

## Why it is built this way

D1's free tier allows 5M rows read/day. Rendering every page per-request needs much more than that, as `getRankingSystems()` scanned the whole `ranking` table on every SSR render, and the table queries sorted a full (system, year) slice to show 50 rows.

Since the data only changes when the crawler re-runs, none of those queries needed to happen per request. Prerendering removes them from the request path entirely rather than making them cheaper, which takes the read count to zero and makes the limit irrelevant.

## Build inputs

`bun run build:data` projects the read model into JSON before Astro runs, reading `backend/data/rankr.sqlite`, and the single source of truth for the site.

It writes `.data/` (build-only) plus the runtime assets `public/data/*.json`, `public/api/institution/*.json` and `public/search.json`. All are gitignored.

```bash
bun run build:data
```

## Deploy

```bash
bun run deploy  # = build:data && astro build && wrangler deploy
```

The build prerenders ~4,900 pages and takes 5-15 minutes. Output is ~10,500 files / ~313 MB, against a free-plan limit of 20,000 files and 25 MiB per file. `verify:build` fails the build before deploy if either limit is crossed. Wrangler only uploads assets whose hashes changed, so redeploys after the first are quick.

Test the `*.workers.dev` URL (table, country filter, pagination, search, profile charts, compare) before touching the domain.

## Updating after a re-crawl

No database step. Crawl into `backend/data/rankr.sqlite`, then:

```bash
bun run logos     # only if new institutions appeared
bun run deploy
```

## Custom domain

- Domain DNS already on Cloudflare: add a route / custom domain in `wrangler.jsonc`, then redeploy (CLI-only).
- Domain not on Cloudflare yet: add the zone + point nameservers (one-time, dashboard or API), then attach.

## Local dev

```bash
bun run dev       # runs build:data first, then astro dev
```

`dev` needs no database or bindings; `build:data` produces everything the pages read.

## Traffic reports

```bash
bun run report                     # today, last 7 days, last 30 days -> stdout
bun run report -- --out usage.md   # write to a file
bun run report -- --top 25         # widen the top-N tables
```

When redirecting, use `--out` or `bun run --silent report > usage.md`; a plain `bun run report > usage.md` captures bun's `$ bun scripts/...` banner as the first line.

Reads Cloudflare's GraphQL Analytics API. Uses `$CLOUDFLARE_API_TOKEN` (needs Zone:Read + Zone Analytics:Read) if set, otherwise the local `wrangler login` credentials.

## Gotchas

- **Every CLI here exits 1 on success (Windows)** → `astro build`, `astro check` and `wrangler deploy` all print full success and then return status 1. Astro's own `exit` event reports code 0 and its CLI promise resolves cleanly, so the status is being mangled during native process teardown; it reproduces under both bun and node. Astro's entry point ends in `.catch(() => process.exit(1))`, which swallows any error silently, so there is nothing to read either.
  - For the build, `build` ignores the status and runs `verify:build`, which checks the output instead.
  - For `deploy`, the exit code is cosmetic: read wrangler's output. A real success prints `Current Version ID: ...` and the deployed triggers. Confirm with `curl -o /dev/null -w '%{http_code}' https://rankr.online/`, or `bunx wrangler deployments list`.
- **`SESSION` KV "namespace already exists" [10014]** → the `@astrojs/cloudflare` adapter auto-enables KV-backed **sessions** (`SESSION` binding) and **Cloudflare Images** (`IMAGES` binding), and wrangler tries to create the KV on deploy. If a prior attempt already made it, bind the existing one in `wrangler.jsonc`:
  `"kv_namespaces": [{ "binding": "SESSION", "id": "<from: wrangler kv namespace list>" }]`.
  The app uses neither sessions nor Images; they can be trimmed later (e.g. `cloudflare({ imageService: "passthrough" })`).

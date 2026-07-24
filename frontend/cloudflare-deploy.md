# Cloudflare deploy runbook

The frontend deploys as a **Cloudflare Worker** via `wrangler deploy` — _not_ Git-connected. Cloudflare never watches a branch; you push the built bundle with a command from whatever is checked out. The backend crawl runs locally; D1 is a slimmed projection of `backend/data/rankr.sqlite` (ranked institutions only, ranking rows collapsed into a JSON `metrics` column).

All commands run from `frontend/`.

## One-time setup

```bash
cd frontend
bunx wrangler login                 # or: export CLOUDFLARE_API_TOKEN=...  (fully headless)
bunx wrangler d1 create rankr       # paste the printed database_id into wrangler.jsonc,
                                    # replacing the "local-rankr" placeholder (deploy fails without a real id)
```

## Seed the remote D1 — NOT automatic

`wrangler deploy` only wires up bindings; it never loads data. You must seed D1 yourself (and re-seed after every backend re-crawl), or every page 500s with `no such table: ranking`.

```bash
bun run dump:d1     # writes .dump/rankr-d1.sql (INSERTs byte-capped so none trips D1's SQLITE_TOOBIG)
bunx wrangler d1 execute rankr --remote --file=.dump/rankr-d1.sql
```

- The dump starts with `DROP TABLE IF EXISTS`, so re-running the command is idempotent (clean re-seed, no manual drop).
- `wrangler d1 import rankr --file=…` is a one-shot bulk loader too but needs **wrangler ≥ 4.114**; `d1 execute --file` works on any version.
- Verify: `bunx wrangler d1 execute rankr --remote --command "SELECT count(*) FROM ranking"` → expect ~36,560.
- ~50k rows is well under the 100k rows/day free write limit, so a full seed is one sitting.

## Deploy

```bash
bun run deploy    # = astro build && wrangler deploy  ->  https://rankr.<subdomain>.workers.dev
```

Test the `*.workers.dev` URL (table, filters, search, profile charts, compare) before touching the domain. The Worker reads D1 live, so after a re-seed you just reload — no redeploy.

## Custom domain

- Domain DNS already on Cloudflare: add a route / custom domain in `wrangler.jsonc`, then redeploy (CLI-only).
- Domain not on Cloudflare yet: add the zone + point nameservers (one-time, dashboard or API), then attach.

## dev -> main flow (Cloudflare doesn't track branches)

1. Test on the `*.workers.dev` URL from the `dev` branch.
2. Retire the VPS, merge `dev` -> `main`.
3. `git checkout main && bun run deploy`.
4. Attach the custom domain.

## Local dev (reference)

```bash
bunx wrangler d1 execute rankr --local --command "SELECT 1"   # create the local D1 file (once)
bun run seed:local                                            # project rankr.sqlite -> local D1
bun run dev
```

## Gotchas (hit during the first deploy)

- **`database_id` placeholder** → `binding DB ... must have a valid database_id [10021]`. Fill in the real id from `d1 create`.
- **`SESSION` KV "namespace already exists" [10014]** → the `@astrojs/cloudflare` adapter auto-enables KV-backed **sessions** (`SESSION` binding) and **Cloudflare Images** (`IMAGES` binding), and wrangler tries to create the KV on deploy. If a prior attempt already made it, bind the existing one in `wrangler.jsonc`:
  `"kv_namespaces": [{ "binding": "SESSION", "id": "<from: wrangler kv namespace list>" }]`.
  The app uses neither sessions nor Images — they can be trimmed later (e.g. `cloudflare({ imageService: "passthrough" })`).
- **`SQLITE_TOOBIG` while seeding** → a single INSERT exceeded D1's statement-length cap. `dump:d1` now byte-caps every INSERT (≤40 KB), so this can't recur.

## Free-tier notes

- Limits: 5M rows **read**/day, 100k rows **written**/day, 5 GB.
- The projection + JSON collapse keep the seed (~50k rows) inside the daily write budget; the D1 indexes (`ix_ranking_lookup`, `ix_ranking_institution`, `ix_link_institution`) keep per-request reads tiny.
- The dump in `.dump/` is gitignored — regenerate with `bun run dump:d1` whenever `rankr.sqlite` changes.
- Push-to-`main` auto-deploy without the dashboard: a GitHub Action running `wrangler deploy` with a `CLOUDFLARE_API_TOKEN` secret.

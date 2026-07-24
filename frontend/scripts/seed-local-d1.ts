#!/usr/bin/env bun
/**
 * Reseed the local (miniflare) D1 database from the crawler's rankr.sqlite.
 *
 * D1 is a *projection* of rankr.sqlite for the frontend's read paths, not a full copy:
 *   - only ranked institutions (and their links), the countries, the rankings;
 *   - the acronym/alias/label/type tables are dropped (their search text is
 *     already in institution.soup, and nothing renders them);
 *   - the `ranking` table is COLLAPSED: one row per (institution, system, type,
 *     year, field, subject), with the per-metric values folded into a `metrics`
 *     JSON blob keyed by metric name. That shrinks the ranking table by about 90%
 *     and the whole DB from ~1.04M to ~50k, which fits a one-shot free-tier seed.
 * Frontend-tuned indexes are created explicitly (rankr.sqlite's own are dropped).
 *
 * Run after rebuilding backend/data/rankr.sqlite (from frontend/, with the dev
 * server stopped so the file isn't locked):
 *   bunx wrangler d1 execute rankr --local --command "SELECT 1"   # once, creates the local D1 file
 *   bun run seed:local
 */

import { Database } from "bun:sqlite";
import { existsSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND = dirname(HERE);
const SRC = join(FRONTEND, "..", "backend", "data", "rankr.sqlite");
const D1_DIR = join(
  FRONTEND,
  ".wrangler",
  "state",
  "v3",
  "d1",
  "miniflare-D1DatabaseObject",
);

// All tables that may exist in a prior local D1, dropped before reseeding.
const ALL_TABLES = [
  "country",
  "institution",
  "link",
  "ranking",
  "acronym",
  "alias",
  "label",
  "type",
];
// Ranked institutions only; their links follow. country copies whole.
const RANKED =
  "SELECT DISTINCT institution_id FROM src.ranking WHERE institution_id IS NOT NULL";
const COPY: Record<string, string> = {
  country: "",
  institution: `WHERE id IN (${RANKED})`,
  link: `WHERE institution_id IN (${RANKED})`,
};
// Collapsed ranking: one row per group, metrics folded into a JSON object
// { "<metric>": { "raw_value": ..., "value": ..., "value_type": ... }, ... }.
const RANKING_DDL = `CREATE TABLE ranking (
  institution_id INTEGER,
  ranking_system TEXT NOT NULL,
  ranking_type   TEXT NOT NULL,
  year           INTEGER,
  field          TEXT NOT NULL,
  subject        TEXT NOT NULL,
  metrics        TEXT NOT NULL
)`;
const RANKING_INSERT = `INSERT INTO main.ranking
  (institution_id, ranking_system, ranking_type, year, field, subject, metrics)
  SELECT institution_id, ranking_system, ranking_type, year, field, subject,
         json_group_object(
           metric,
           json_object('raw_value', raw_value, 'value', value, 'value_type', value_type)
         )
  FROM src.ranking
  WHERE institution_id IS NOT NULL
  GROUP BY institution_id, ranking_system, ranking_type, year, field, subject`;
// Frontend read paths: institution_id lookups (profile/compare) + the
// (system, year) filter that drives the ranking table / country list.
const INDEXES = [
  "CREATE INDEX ix_ranking_institution ON ranking(institution_id)",
  "CREATE INDEX ix_ranking_lookup ON ranking(ranking_system, year)",
  "CREATE INDEX ix_link_institution ON link(institution_id)",
];

function die(message: string): never {
  console.error(message);
  process.exit(1);
}

if (!existsSync(SRC)) die(`source sqlite not found: ${SRC}`);

let d1File: string | undefined;
try {
  d1File = readdirSync(D1_DIR).find(
    (f) => f.endsWith(".sqlite") && !f.includes("metadata"),
  );
} catch {
  /* dir missing → handled below */
}
if (!d1File) {
  die(
    'local D1 file not found. Create it once with:\n  bunx wrangler d1 execute rankr --local --command "SELECT 1"',
  );
}
const dest = join(D1_DIR, d1File);

const db = new Database(dest);
db.run("ATTACH DATABASE ? AS src", [SRC]);
db.run("PRAGMA foreign_keys=OFF");
for (const table of [...ALL_TABLES].reverse())
  db.run(`DROP TABLE IF EXISTS main.${table}`);

for (const table of ["country", "institution", "link"]) {
  const row = db
    .query("SELECT sql FROM src.sqlite_master WHERE type='table' AND name=?")
    .get(table) as { sql: string } | null;
  if (!row) die(`table '${table}' missing in ${SRC}`);
  db.run(row.sql);
  db.run(`INSERT INTO main.${table} SELECT * FROM src.${table} ${COPY[table]}`);
}
db.run(RANKING_DDL);
db.run(RANKING_INSERT);
for (const sql of INDEXES) db.run(sql);

const institutions = (
  db.query("SELECT COUNT(*) AS c FROM institution").get() as { c: number }
).c;
const rankings = (db.query("SELECT COUNT(*) AS c FROM ranking").get() as { c: number })
  .c;
db.close();
console.log(`reseeded local D1 <- ${SRC}`);
console.log(`  institutions: ${institutions}  ranking rows (collapsed): ${rankings}`);

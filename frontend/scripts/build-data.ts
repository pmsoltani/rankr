#!/usr/bin/env bun
/**
 * Project the crawler's rankr.sqlite into the JSON the static build consumes.
 *
 * This replaces D1 on the read path. The site is an archive (the data does not
 * change between deploys) so every page the frontend used to render per-request
 * from D1 is instead rendered at build time from these files.
 *
 * Emits:
 *   .data/systems.json              { system: [year, ...] }, years newest-first
 *   .data/ror-ids.json              every ranked ROR id (getStaticPaths + sitemap)
 *   .data/institutions/{ror}.json   InstitutionDetail for /i/{ror}
 *   public/data/{system}-{year}.json     ranked rows + country facets for one table
 *   public/api/institution/{ror}.json    lean ranks+scores for the Compare island
 *   public/search.json              the typeahead corpus (name | country | soup)
 *
 * `public/` output is deliberate: those are fetched by the browser at runtime
 * (country filtering, compare, search); `public/data` is also read back by the
 * build for page-1 markup. `.data/` is build-only and never shipped.
 *
 *   bun run build:data
 */

import { Database } from "bun:sqlite";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC =
  process.env.RANKR_SQLITE ?? join(FRONTEND, "..", "backend", "data", "rankr.sqlite");
const DATA = join(FRONTEND, ".data");
const PUBLIC_DATA = join(FRONTEND, "public", "data");
const PUBLIC_API = join(FRONTEND, "public", "api", "institution");

// Only these rows are ever surfaced; every row in the source happens to match,
// but the frontend has always scoped to them, so keep the contract explicit.
const SCOPE = `ranking_type = 'university ranking' AND field = 'All' AND subject = 'All'`;
// THE reports these per-institution figures; the profile shows the latest year's.
const STAT_METRICS = [
  "# FTE Students",
  "# Students per Staff",
  "% International Students",
  "% Female Students",
];

if (!existsSync(SRC)) {
  console.error(
    `source database not found: ${SRC}\n` +
      "Run the crawl (backend/), restore a backup, or set $RANKR_SQLITE to a copy.",
  );
  process.exit(1);
}

const db = new Database(SRC, { readonly: true });
const rankedCount = (
  db
    .query(
      `SELECT COUNT(DISTINCT institution_id) AS c FROM ranking WHERE institution_id IS NOT NULL AND ${SCOPE}`,
    )
    .get() as { c: number }
).c;
if (!rankedCount) {
  console.error(
    `${SRC} has no ranking rows; it looks like a bare ROR dump with the crawl\n` +
      "never run into it. Run the crawl, or restore a backup that has the rankings.",
  );
  process.exit(1);
}
console.log(`source: ${SRC}  (${rankedCount.toLocaleString()} ranked institutions)`);

for (const dir of [DATA, PUBLIC_DATA, join(FRONTEND, "public", "api")]) {
  if (existsSync(dir)) rmSync(dir, { recursive: true });
}
for (const dir of [join(DATA, "institutions"), PUBLIC_DATA, PUBLIC_API]) {
  mkdirSync(dir, { recursive: true });
}

const write = (path: string, value: unknown) =>
  writeFileSync(path, JSON.stringify(value));

// ---------------------------------------------------------------- systems ---
type SystemYear = { ranking_system: string; year: number };
const systemYears = db
  .query(
    `SELECT DISTINCT ranking_system, year
       FROM ranking
     WHERE ${SCOPE} AND year IS NOT NULL
     ORDER BY ranking_system, year DESC`,
  )
  .all() as SystemYear[];

const systems: Record<string, number[]> = {};
for (const { ranking_system, year } of systemYears) {
  (systems[ranking_system] ??= []).push(year);
}
write(join(DATA, "systems.json"), systems);

// ----------------------------------------------------------------- tables ---
// One file per (system, year): every ranked institution in rank order, plus the
// country facet list. Page-1 markup is rendered from this at build time; the
// browser refetches it only when someone picks a country filter.
const tableRows = db.query(
  `SELECT i.ror_id, i.name, c.country, c.country_code, r.raw_value, r.value
     FROM ranking r
     JOIN institution i ON i.id = r.institution_id
     LEFT JOIN country c ON c.id = i.country_id
    WHERE r.ranking_system = ? AND r.year = ? AND r.metric = 'Rank' AND ${SCOPE}
    ORDER BY (r.value IS NULL), r.value, i.name`,
);

let tableRowTotal = 0;
for (const [system, years] of Object.entries(systems)) {
  for (const year of years) {
    const rows = (
      tableRows.all(system, year) as {
        ror_id: string;
        name: string;
        country: string | null;
        country_code: string | null;
        raw_value: string | null;
        value: number | null;
      }[]
    ).map((r) => ({
      ror_id: r.ror_id,
      name: r.name,
      country: r.country,
      country_code: r.country_code,
      // THE's numeric ranges arrive with a mangled dash (U+FFFD); clean once here
      // so neither the build nor the client has to.
      raw_value: r.raw_value?.replace(/�/g, "–") ?? null,
      value: r.value,
    }));

    const seen = new Map<string, { country: string; country_code: string }>();
    for (const r of rows) {
      if (r.country && r.country_code && !seen.has(r.country)) {
        seen.set(r.country, { country: r.country, country_code: r.country_code });
      }
    }
    const countries = [...seen.values()].sort((a, b) =>
      a.country.localeCompare(b.country),
    );

    tableRowTotal += rows.length;
    write(join(PUBLIC_DATA, `${system}-${year}.json`), { countries, rows });
  }
}

// ----------------------------------------------------------- institutions ---
interface MetricRow {
  ranking_system: string;
  year: number;
  metric: string;
  raw_value: string | null;
  value: number | string | null;
  value_type: string;
}

const ranked = db
  .query(
    `SELECT i.*, c.id AS c_id, c.country, c.country_code, c.region, c.sub_region
       FROM institution i
       LEFT JOIN country c ON c.id = i.country_id
      WHERE i.id IN (
        SELECT DISTINCT institution_id
          FROM ranking
        WHERE institution_id IS NOT NULL AND ${SCOPE}
      )
      ORDER BY i.ror_id`,
  )
  .all() as Record<string, any>[];

const linksFor = db.query(
  `SELECT type, link FROM link WHERE institution_id = ? ORDER BY type`,
);
const metricsFor = db.query(
  `SELECT ranking_system, year, metric, raw_value, value, value_type
     FROM ranking
   WHERE institution_id = ? AND ${SCOPE} AND year IS NOT NULL`,
);

const bySystemYear = (a: MetricRow, b: MetricRow) =>
  a.ranking_system.localeCompare(b.ranking_system) || a.year - b.year;
const bySystemYearMetric = (a: MetricRow, b: MetricRow) =>
  bySystemYear(a, b) || a.metric.localeCompare(b.metric);

// Ranks and scores are serialized into every institution page's hydration
// payload (~400 rows for a long-ranked university) so they carry only the
// fields something actually renders. `value_type` survives on stats alone,
// which are the only rows displayed with units.
const point = (r: MetricRow) => ({
  ranking_system: r.ranking_system,
  year: r.year,
  metric: r.metric,
  raw_value: r.raw_value,
  value: r.value,
});

const rorIds: string[] = [];
for (const row of ranked) {
  const all = metricsFor.all(row.id) as MetricRow[];

  // THE's student stats, for the institution's most recent THE year only.
  const theYears = all.filter((r) => r.ranking_system === "the").map((r) => r.year);
  const latestThe = theYears.length ? Math.max(...theYears) : null;

  const ranks = all
    .filter((r) => r.metric === "Rank")
    .sort(bySystemYear)
    .map(point);
  const scores = all
    .filter((r) => r.metric.endsWith("Score"))
    .sort(bySystemYearMetric)
    .map(point);

  write(join(DATA, "institutions", `${row.ror_id}.json`), {
    ror_id: row.ror_id,
    name: row.name,
    established: row.established,
    lat: row.lat,
    lng: row.lng,
    city: row.city,
    country: row.c_id
      ? {
          id: row.c_id,
          country: row.country,
          country_code: row.country_code,
          region: row.region,
          sub_region: row.sub_region,
        }
      : null,
    links: linksFor.all(row.id),
    ranks,
    scores,
    stats:
      latestThe === null
        ? []
        : all
            .filter(
              (r) =>
                r.ranking_system === "the" &&
                r.year === latestThe &&
                STAT_METRICS.includes(r.metric),
            )
            .map((r) => ({ ...point(r), value_type: r.value_type })),
  });

  // The Compare island picks institutions client-side, so it cannot be
  // prerendered: it fetches one of these per selection. This used to be a D1
  // query (`/api/institution/[rorId]`); as a static asset it costs nothing and
  // removes the last database read from the request path.
  write(join(PUBLIC_API, `${row.ror_id}.json`), {
    ror_id: row.ror_id,
    name: row.name,
    country_code: row.country_code ?? null,
    ranks,
    scores,
  });

  rorIds.push(row.ror_id);
}
write(join(DATA, "ror-ids.json"), rorIds);

// ----------------------------------------------------------------- search ---
// Mirrors the old SQL (`WHERE soup LIKE '%q%'`, name-prefix first, then shorter
// names) so client-side matching returns what the D1 query used to. Keys are
// short because this ships to every visitor who opens the palette.
const searchRows = db
  .query(
    `SELECT i.ror_id, i.name, i.soup, c.country, c.country_code
       FROM institution i
       LEFT JOIN country c ON c.id = i.country_id
      WHERE i.id IN (
        SELECT DISTINCT institution_id
          FROM ranking
        WHERE institution_id IS NOT NULL AND ${SCOPE}
      )`,
  )
  .all() as {
  ror_id: string;
  name: string;
  soup: string | null;
  country: string | null;
  country_code: string | null;
}[];

write(
  join(FRONTEND, "public", "search.json"),
  searchRows.map((r) => ({
    r: r.ror_id,
    n: r.name,
    c: r.country,
    k: r.country_code,
    // Lowercased once at build time; the client lowercases only the query.
    s: (r.soup ?? r.name).toLowerCase(),
  })),
);

db.close();

const kb = (p: string) => (Bun.file(p).size / 1024).toFixed(0);
console.log(`  systems            ${Object.keys(systems).length}`);
console.log(
  `  system-year tables ${systemYears.length}  (${tableRowTotal.toLocaleString()} rows)`,
);
console.log(`  institutions       ${rorIds.length.toLocaleString()}`);
console.log(`  search.json        ${kb(join(FRONTEND, "public", "search.json"))} KB`);

#!/usr/bin/env bun
/**
 * Emit the projected + collapsed D1 dataset (same shape as seed-local-d1.ts) as
 * a single SQL file for seeding a REMOTE Cloudflare D1:
 *   bun run dump:d1
 *   bunx wrangler d1 execute rankr --remote --file=.dump/rankr-d1.sql
 *
 * INSERTs are byte-capped (STATEMENT_MAX) so no single statement trips D1's
 * SQLITE_TOOBIG limit. Starts with DROP TABLE IF EXISTS (idempotent re-seed);
 * indexes are created last. Output lives in .dump/ (gitignored) — regenerate
 * whenever backend/data/rankr.sqlite changes.
 */
import { Database } from "bun:sqlite";
import { mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND = dirname(HERE);
const SRC = join(FRONTEND, "..", "backend", "data", "rankr.sqlite");
const OUT_DIR = join(FRONTEND, ".dump");
const OUT = join(OUT_DIR, "rankr-d1.sql");
const STATEMENT_MAX = 40_000; // max bytes per INSERT statement (well under D1's cap)

const db = new Database(SRC, { readonly: true });

function lit(v: unknown): string {
  if (v === null || v === undefined) return "NULL";
  if (typeof v === "number" || typeof v === "bigint") return String(v);
  return `'${String(v).replaceAll("'", "''")}'`;
}

// Multi-row INSERTs, flushing a statement before it crosses STATEMENT_MAX bytes.
function insertStatements(table: string, cols: string[], rows: unknown[][]): string[] {
  const head = `INSERT INTO ${table} (${cols.join(", ")}) VALUES\n`;
  const out: string[] = [];
  let buf: string[] = [];
  let size = head.length;
  const flush = () => {
    if (buf.length) out.push(head + buf.join(",\n") + ";");
    buf = [];
    size = head.length;
  };
  for (const r of rows) {
    const tuple = `(${r.map(lit).join(",")})`;
    if (buf.length && size + tuple.length + 2 > STATEMENT_MAX) flush();
    buf.push(tuple);
    size += tuple.length + 2;
  }
  flush();
  return out;
}

function select(sql: string): { cols: string[]; values: unknown[][] } {
  const stmt = db.query(sql);
  return { cols: stmt.columnNames, values: stmt.values() as unknown[][] };
}

const RANKED =
  "SELECT DISTINCT institution_id FROM ranking WHERE institution_id IS NOT NULL";
const statements: string[] = [];

// reset (children first) so re-running is idempotent
for (const t of ["ranking", "link", "institution", "country"]) {
  statements.push(`DROP TABLE IF EXISTS ${t};`);
}
// schema (parents first; mirror seed-local-d1.ts)
for (const t of ["country", "institution", "link"]) {
  const row = db
    .query("SELECT sql FROM sqlite_master WHERE type='table' AND name=?")
    .get(t) as { sql: string } | null;
  if (!row) throw new Error(`table '${t}' missing in ${SRC}`);
  statements.push(`${row.sql};`);
}
statements.push(
  "CREATE TABLE ranking (\n" +
    "  institution_id INTEGER, ranking_system TEXT NOT NULL, ranking_type TEXT NOT NULL,\n" +
    "  year INTEGER, field TEXT NOT NULL, subject TEXT NOT NULL, metrics TEXT NOT NULL\n" +
    ");",
);

// data (parents first so FKs hold without disabling them)
const country = select("SELECT * FROM country");
statements.push(...insertStatements("country", country.cols, country.values));
const inst = select(`SELECT * FROM institution WHERE id IN (${RANKED})`);
statements.push(...insertStatements("institution", inst.cols, inst.values));
const link = select(`SELECT * FROM link WHERE institution_id IN (${RANKED})`);
statements.push(...insertStatements("link", link.cols, link.values));
const ranking = select(
  "SELECT institution_id, ranking_system, ranking_type, year, field, subject, " +
    "json_group_object(metric, json_object('raw_value', raw_value, 'value', value, " +
    "'value_type', value_type)) AS metrics " +
    "FROM ranking WHERE institution_id IS NOT NULL " +
    "GROUP BY institution_id, ranking_system, ranking_type, year, field, subject",
);
statements.push(
  ...insertStatements(
    "ranking",
    [
      "institution_id",
      "ranking_system",
      "ranking_type",
      "year",
      "field",
      "subject",
      "metrics",
    ],
    ranking.values,
  ),
);

// indexes last (faster than maintaining them during the inserts)
statements.push("CREATE INDEX ix_ranking_institution ON ranking(institution_id);");
statements.push("CREATE INDEX ix_ranking_lookup ON ranking(ranking_system, year);");
statements.push("CREATE INDEX ix_link_institution ON link(institution_id);");

db.close();

// clean prior output (this dump, or stale chunk files from an earlier version)
for (const f of readdirSync(FRONTEND)) {
  if (f.startsWith("rankr-d1") && f.endsWith(".sql")) rmSync(join(FRONTEND, f));
}
mkdirSync(OUT_DIR, { recursive: true });
const sql = statements.join("\n\n") + "\n";
writeFileSync(OUT, sql);
console.log(
  `wrote ${OUT}  (${(sql.length / 1e6).toFixed(1)} MB, ${statements.length} statements)`,
);
console.log("seed remote D1:");
console.log("  bunx wrangler d1 execute rankr --remote --file=.dump/rankr-d1.sql");

#!/usr/bin/env bun
/**
 * Emit the projected + collapsed D1 dataset (same shape as seed-local-d1.ts) as
 * one portable SQL file, for seeding a REMOTE Cloudflare D1:
 *   bun run dump:d1
 *   bunx wrangler d1 import rankr --remote --file=./rankr-d1.sql
 *
 * Emits CREATE TABLE + batched INSERT (parent-first, so FKs hold without
 * disabling them) + CREATE INDEX. rankr-d1.sql is a throwaway deploy artifact
 * (gitignored); regenerate whenever backend/data/rankr.sqlite changes.
 */
import { Database } from "bun:sqlite";
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND = dirname(HERE);
const SRC = join(FRONTEND, "..", "backend", "data", "rankr.sqlite");
const OUT = join(FRONTEND, "rankr-d1.sql");
const BATCH = 500;

const db = new Database(SRC, { readonly: true });

function lit(v: unknown): string {
  if (v === null || v === undefined) return "NULL";
  if (typeof v === "number" || typeof v === "bigint") return String(v);
  return `'${String(v).replaceAll("'", "''")}'`;
}

function inserts(table: string, cols: string[], rows: unknown[][]): string {
  if (rows.length === 0) return "";
  const chunks: string[] = [];
  for (let i = 0; i < rows.length; i += BATCH) {
    const values = rows
      .slice(i, i + BATCH)
      .map((r) => `(${r.map(lit).join(",")})`)
      .join(",\n");
    chunks.push(`INSERT INTO ${table} (${cols.join(", ")}) VALUES\n${values};`);
  }
  return chunks.join("\n");
}

function dump(table: string, sql: string, cols?: string[]): string {
  const stmt = db.query(sql);
  const rows = stmt.values() as unknown[][];
  return inserts(table, cols ?? stmt.columnNames, rows);
}

const RANKED =
  "SELECT DISTINCT institution_id FROM ranking WHERE institution_id IS NOT NULL";
const parts: string[] = [];

// --- schema (mirror seed-local-d1.ts) ---
for (const t of ["country", "institution", "link"]) {
  const row = db
    .query("SELECT sql FROM sqlite_master WHERE type='table' AND name=?")
    .get(t) as { sql: string } | null;
  if (!row) throw new Error(`table '${t}' missing in ${SRC}`);
  parts.push(`${row.sql};`);
}
parts.push(
  "CREATE TABLE ranking (\n" +
    "  institution_id INTEGER, ranking_system TEXT NOT NULL, ranking_type TEXT NOT NULL,\n" +
    "  year INTEGER, field TEXT NOT NULL, subject TEXT NOT NULL, metrics TEXT NOT NULL\n" +
    ");",
);

// --- data (parent-first so FKs hold without disabling them) ---
parts.push(dump("country", "SELECT * FROM country"));
parts.push(dump("institution", `SELECT * FROM institution WHERE id IN (${RANKED})`));
parts.push(dump("link", `SELECT * FROM link WHERE institution_id IN (${RANKED})`));
parts.push(
  dump(
    "ranking",
    "SELECT institution_id, ranking_system, ranking_type, year, field, subject, " +
      "json_group_object(metric, json_object('raw_value', raw_value, 'value', value, " +
      "'value_type', value_type)) AS metrics " +
      "FROM ranking WHERE institution_id IS NOT NULL " +
      "GROUP BY institution_id, ranking_system, ranking_type, year, field, subject",
    [
      "institution_id",
      "ranking_system",
      "ranking_type",
      "year",
      "field",
      "subject",
      "metrics",
    ],
  ),
);

// --- indexes last (faster than maintaining them during the inserts) ---
parts.push("CREATE INDEX ix_ranking_institution ON ranking(institution_id);");
parts.push("CREATE INDEX ix_ranking_lookup ON ranking(ranking_system, year);");
parts.push("CREATE INDEX ix_link_institution ON link(institution_id);");

const sql = parts.filter(Boolean).join("\n\n") + "\n";
writeFileSync(OUT, sql);
db.close();
console.log(`wrote ${OUT}  (${(sql.length / 1e6).toFixed(1)} MB)`);

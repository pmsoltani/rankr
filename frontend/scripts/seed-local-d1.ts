#!/usr/bin/env bun
/**
 * Reseed the local (miniflare) D1 database from the crawler's rankr.sqlite.
 *
 * Copies every table directly via SQLite ATTACH (fast, native) into the offline
 * D1 file that `astro dev` / `wrangler --local` use. Run after rebuilding
 * backend/data/rankr.sqlite.
 *
 * Usage (from frontend/, with the dev server stopped so the file isn't locked):
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
// Parent tables before children (FKs).
const ORDER = [
  "country",
  "institution",
  "acronym",
  "alias",
  "label",
  "link",
  "ranking",
  "type",
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
for (const table of [...ORDER].reverse()) db.run(`DROP TABLE IF EXISTS main.${table}`);
for (const table of ORDER) {
  const row = db
    .query("SELECT sql FROM src.sqlite_master WHERE type='table' AND name=?")
    .get(table) as { sql: string } | null;
  if (!row) die(`table '${table}' missing in ${SRC}`);
  db.run(row.sql);
  db.run(`INSERT INTO main.${table} SELECT * FROM src.${table}`);
}
const indexes = db
  .query("SELECT sql FROM src.sqlite_master WHERE type='index' AND sql IS NOT NULL")
  .all() as { sql: string }[];
for (const { sql } of indexes) db.run(sql);

const institutions = (
  db.query("SELECT COUNT(*) AS c FROM institution").get() as { c: number }
).c;
const rankings = (db.query("SELECT COUNT(*) AS c FROM ranking").get() as { c: number })
  .c;
db.close();
console.log(`reseeded local D1 <- ${SRC}`);
console.log(`  institutions: ${institutions}  rankings: ${rankings}`);

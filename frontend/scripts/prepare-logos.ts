#!/usr/bin/env bun
/**
 * Copy institution logos from backend/data/wikipedia into frontend/public/logos.
 * public/logos is gitignored; no manifest; the institution page requests
 * /logos/{ror}.svg and falls back through png/jpg/jpeg/gif to the placeholder
 * client-side. Re-run when the logo set changes:
 *   bun run logos
 */
import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND = dirname(HERE);
const SRC = join(FRONTEND, "..", "backend", "data", "wikipedia");
const OUT = join(FRONTEND, "public", "logos");

// Preferred extension order (matches the client-side fallback chain).
const EXT_ORDER = ["svg", "png", "jpg", "jpeg", "gif"];

if (!existsSync(SRC)) {
  console.error(`logos source not found: ${SRC}`);
  process.exit(1);
}

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

const byRor = new Map<string, Set<string>>();
for (const file of readdirSync(SRC)) {
  const match = /^(.+)\.([a-z0-9]+)$/i.exec(file);
  if (!match) continue;
  const [, ror, ext] = match;
  const e = ext.toLowerCase();
  if (!EXT_ORDER.includes(e)) continue;
  if (!byRor.has(ror)) byRor.set(ror, new Set());
  byRor.get(ror)?.add(e);
}

let count = 0;
for (const [ror, set] of byRor) {
  const ext = EXT_ORDER.find((e) => set.has(e)) ?? [...set][0];
  copyFileSync(join(SRC, `${ror}.${ext}`), join(OUT, `${ror}.${ext}`));
  count++;
}
console.log(`copied ${count} logos -> public/logos`);

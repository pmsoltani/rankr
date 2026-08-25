#!/usr/bin/env bun
/**
 * Assert that `astro build` produced a complete, fresh `dist/`.
 *
 * Why this exists: on Windows `astro build` returns a non-zero status even on a
 * fully successful build; Astro's own `exit` event reports code 0 and its CLI
 * promise resolves cleanly, but the process status is mangled during native
 * teardown (the CLI entry point's final `.catch(() => process.exit(1))` swallows
 * errors silently, so there is nothing to read either). Gating `deploy` on that
 * status would mean never deploying; ignoring it would mean deploying a broken
 * build. So the build chain ignores the status and runs this instead, which
 * checks the thing we actually care about.
 *
 * Freshness matters as much as completeness: if Astro died early, a `dist/` left
 * over from a previous run would otherwise sail through. Every expected artifact
 * must therefore be newer than the data it was built from.
 *
 *   bun run verify:build
 */

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND = dirname(dirname(fileURLToPath(import.meta.url)));
const DATA = join(FRONTEND, ".data");
const CLIENT = join(FRONTEND, "dist", "client");

// Cloudflare's Workers free plan: 20,000 files per version, 25 MiB per file.
const MAX_FILES = 20_000;
const MAX_FILE_BYTES = 25 * 1024 * 1024;

const problems: string[] = [];
const fail = (msg: string) => problems.push(msg);

if (!existsSync(CLIENT)) {
  console.error(`no build output at ${CLIENT}\nRun \`bun run build\`.`);
  process.exit(1);
}

// Anything older than the projection is a leftover from an earlier build.
const dataStamp = statSync(join(DATA, "systems.json")).mtimeMs;
const stale = (path: string) => statSync(path).mtimeMs < dataStamp;

const systems = JSON.parse(readFileSync(join(DATA, "systems.json"), "utf8")) as Record<
  string,
  number[]
>;
const rorIds = JSON.parse(readFileSync(join(DATA, "ror-ids.json"), "utf8")) as string[];

// --- required singletons -----------------------------------------------------
// Only artifacts Astro regenerates each build are freshness-checked. Files
// copied verbatim out of `public/` (robots.txt, the hand-written _headers rules)
// keep their source mtime, which legitimately predates the last data projection.
const GENERATED = new Set(["index.html", "404.html", "sitemap.xml", "_redirects"]);
for (const rel of [
  "index.html",
  "404.html",
  "robots.txt",
  "sitemap.xml",
  "search.json",
  "_headers",
  "_redirects",
]) {
  const path = join(CLIENT, rel);
  if (!existsSync(path)) fail(`missing ${rel}`);
  else if (GENERATED.has(rel) && stale(path)) fail(`stale ${rel} (older than .data/)`);
}

// --- one page per ranked institution -----------------------------------------
const missingInstitutions = rorIds.filter(
  (ror) => !existsSync(join(CLIENT, "i", ror, "index.html")),
);
if (missingInstitutions.length) {
  fail(
    `${missingInstitutions.length}/${rorIds.length} institution pages missing ` +
      `(e.g. /i/${missingInstitutions[0]})`,
  );
}

// --- one Compare payload per ranked institution -------------------------------
// These replaced the D1-backed /api/institution/[rorId] route; a missing one
// means Compare silently fails for that institution.
const missingApi = rorIds.filter(
  (ror) => !existsSync(join(CLIENT, "api", "institution", `${ror}.json`)),
);
if (missingApi.length) {
  fail(
    `${missingApi.length}/${rorIds.length} compare payloads missing ` +
      `(e.g. /api/institution/${missingApi[0]}.json)`,
  );
}

// --- one page per (system, year), plus its pagination -------------------------
let expectedRankingPages = 0;
for (const [system, years] of Object.entries(systems)) {
  for (const year of years) {
    const table = JSON.parse(
      readFileSync(join(FRONTEND, "public", "data", `${system}-${year}.json`), "utf8"),
    ) as { rows: unknown[] };
    const pages = Math.max(1, Math.ceil(table.rows.length / 50));
    expectedRankingPages += pages;

    if (!existsSync(join(CLIENT, "rankings", system, String(year), "index.html"))) {
      fail(`missing /rankings/${system}/${year}`);
    }
    for (let page = 2; page <= pages; page++) {
      if (
        !existsSync(
          join(CLIENT, "rankings", system, String(year), String(page), "index.html"),
        )
      ) {
        fail(`missing /rankings/${system}/${year}/${page}`);
        break; // one report per table is enough
      }
    }
  }
}

// --- the sitemap should list everything we generated --------------------------
if (existsSync(join(CLIENT, "sitemap.xml"))) {
  const sitemap = readFileSync(join(CLIENT, "sitemap.xml"), "utf8");
  const locs = [...sitemap.matchAll(/<loc>([^<]*)<\/loc>/g)].map((m) => m[1]);
  const expected = 3 + expectedRankingPages + rorIds.length; // home, about, compare
  if (locs.length !== expected) {
    fail(`sitemap lists ${locs.length} urls, expected ${expected}`);
  }
  // robots.txt disallows `/*?`, so advertising a query-string url would be a
  // direct contradiction. (Checked per-url: the XML declaration has a `?` too.)
  const withQuery = locs.filter((loc) => loc.includes("?"));
  if (withQuery.length) {
    fail(
      `sitemap contains ${withQuery.length} query-string urls (e.g. ${withQuery[0]})`,
    );
  }
  // Canonical URLs carry no trailing slash (astro `trailingSlash: "never"` +
  // wrangler `html_handling: "drop-trailing-slash"`). Advertising the slashed
  // form would send every crawler through a 307.
  const slashed = locs.filter((loc) => {
    const { pathname } = new URL(loc);
    return pathname !== "/" && pathname.endsWith("/");
  });
  if (slashed.length) {
    fail(
      `sitemap has ${slashed.length} urls with a trailing slash (e.g. ${slashed[0]})`,
    );
  }
}

// --- platform limits ----------------------------------------------------------
let files = 0;
let bytes = 0;
const oversized: string[] = [];
(function walk(dir: string) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) walk(path);
    else {
      files++;
      const { size } = statSync(path);
      bytes += size;
      if (size > MAX_FILE_BYTES) oversized.push(path);
    }
  }
})(CLIENT);

if (files > MAX_FILES) fail(`${files} asset files exceeds the ${MAX_FILES} limit`);
for (const path of oversized) fail(`${path} exceeds the 25 MiB per-file limit`);

// --- report -------------------------------------------------------------------
const mb = (n: number) => `${(n / 1024 / 1024).toFixed(1)} MB`;
if (problems.length) {
  console.error("build verification FAILED:");
  for (const p of problems.slice(0, 20)) console.error(`  - ${p}`);
  if (problems.length > 20) console.error(`  ... and ${problems.length - 20} more`);
  process.exit(1);
}

console.log("build verified");
console.log(`  institution pages ${rorIds.length.toLocaleString()}`);
console.log(`  ranking pages     ${expectedRankingPages.toLocaleString()}`);
console.log(
  `  assets            ${files.toLocaleString()} files, ${mb(bytes)} ` +
    `(limit ${MAX_FILES.toLocaleString()} files, 25 MiB each)`,
);

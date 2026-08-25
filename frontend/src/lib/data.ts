/**
 * Build-time data access. Replaces the D1 read path (`lib/db.ts` + `lib/queries.ts`).
 *
 * The site is an archive, so every page is rendered from the JSON that
 * `scripts/build-data.ts` projects out of the crawler's SQLite. Nothing here runs
 * at the edge; these functions are called from `getStaticPaths()` and from
 * prerendered frontmatter, both of which execute during `astro build`.
 *
 * `node:fs` is used rather than `import`ing the JSON so Vite never pulls 60 MB of
 * institution detail into the bundle graph; only what a page asks for is read.
 */

import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";

import type { InstitutionDetail, RankingSystems, RankingTableRow } from "@/lib/types";

// This module is bundled into dist/ before it runs, so `import.meta.url` points
// at the build output rather than the source tree. Walk up from the working
// directory instead; `astro build` runs from the project root, and the search
// keeps it working if a runner starts a level deeper.
function projectRoot(): string {
  let dir = process.cwd();
  for (;;) {
    if (existsSync(join(dir, ".data"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) return process.cwd();
    dir = parent;
  }
}

const FRONTEND = projectRoot();
const DATA = join(FRONTEND, ".data");
const PUBLIC_DATA = join(FRONTEND, "public", "data");

const MISSING =
  "Run `bun run build:data` first (it projects backend/data/rankr.sqlite into .data/).";

function read<T>(path: string): T {
  try {
    return JSON.parse(readFileSync(path, "utf8")) as T;
  } catch (cause) {
    throw new Error(`missing build data: ${path}\n${MISSING}`, { cause });
  }
}

/** Rows for one (system, year) table, in rank order, plus its country facets. */
export interface RankingTableData {
  countries: { country: string; country_code: string }[];
  rows: RankingTableRow[];
}

export const PER_PAGE = 50;

let systemsCache: RankingSystems | undefined;

/** system id -> years, newest first. */
export function getRankingSystems(): RankingSystems {
  return (systemsCache ??= read<RankingSystems>(join(DATA, "systems.json")));
}

export function getRankingTableData(system: string, year: number): RankingTableData {
  return read<RankingTableData>(join(PUBLIC_DATA, `${system}-${year}.json`));
}

export function getInstitution(rorId: string): InstitutionDetail {
  return read<InstitutionDetail>(join(DATA, "institutions", `${rorId}.json`));
}

/** Every ranked ROR id; used for /i/ path generation and the sitemap. */
export function getAllRankedRorIds(): string[] {
  return read<string[]>(join(DATA, "ror-ids.json"));
}

export const pageCount = (total: number) => Math.max(1, Math.ceil(total / PER_PAGE));

export const pageSlice = <T>(rows: T[], page: number): T[] =>
  rows.slice((page - 1) * PER_PAGE, page * PER_PAGE);

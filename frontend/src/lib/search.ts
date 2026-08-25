import type { SearchResult } from "@/lib/types";

/**
 * Client-side institution search over the prebuilt index.
 *
 * The typeahead used to be a D1 query per keystroke-pause (`WHERE soup LIKE
 * '%q%'`), which scanned all ~3.8k rows every time. The corpus is small and
 * never changes between deploys, so `scripts/build-data.ts` emits it as a static
 * asset instead: one lazy fetch per session, then matching happens locally.
 */

/**
 * One entry per ranked institution. Keys are terse because the whole corpus
 * ships to the client:
 *   r = ror_id, n = name, c = country, k = country_code,
 *   s = lowercased match blob (name | country | acronyms | aliases | labels)
 */
export interface IndexEntry {
  r: string;
  n: string;
  c: string | null;
  k: string | null;
  s: string;
}

// ~230 KB gzipped. Shared across every island on the page, fetched at most once
// per load, then served from the browser cache.
let indexPromise: Promise<IndexEntry[]> | undefined;

export function loadSearchIndex(): Promise<IndexEntry[]> {
  return (indexPromise ??= fetch("/search.json")
    .then((r) =>
      r.ok
        ? (r.json() as Promise<IndexEntry[]>)
        : Promise.reject(new Error(String(r.status))),
    )
    .catch((err) => {
      indexPromise = undefined; // let a later open retry
      throw err;
    }));
}

/**
 * Ranks matches the way the old SQL did: substring match over the blob, then
 * name-prefix matches first, then shorter names, so the canonical institution
 * surfaces above its departments and affiliates.
 */
export function searchIndex(
  index: IndexEntry[],
  raw: string,
  limit = 20,
): SearchResult[] {
  const q = raw.toLowerCase();
  const hits = index.filter((e) => e.s.includes(q));
  hits.sort((a, b) => {
    const byPrefix =
      Number(!a.n.toLowerCase().startsWith(q)) -
      Number(!b.n.toLowerCase().startsWith(q));
    return byPrefix || a.n.length - b.n.length;
  });
  return hits.slice(0, limit).map((e) => ({
    ror_id: e.r,
    name: e.n,
    country: e.c,
    country_code: e.k,
  }));
}

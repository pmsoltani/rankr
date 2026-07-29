import { env } from "cloudflare:workers";
import type { D1Database } from "@cloudflare/workers-types";

/**
 * Minimal read-only query interface over the Cloudflare D1 binding.
 *
 * Both production and local dev use D1 (locally it's miniflare's offline
 * SQLite in `.wrangler/`, seeded from the crawler's rankr.sqlite).
 */
export interface Db {
  all<T = Record<string, unknown>>(sql: string, params?: unknown[]): Promise<T[]>;
  first<T = Record<string, unknown>>(
    sql: string,
    params?: unknown[],
  ): Promise<T | null>;
}

function d1Db(d1: D1Database): Db {
  return {
    async all<T>(sql: string, params: unknown[] = []) {
      const { results } = await d1
        .prepare(sql)
        .bind(...params)
        .all<T>();
      return results;
    },
    async first<T>(sql: string, params: unknown[] = []) {
      return (await d1
        .prepare(sql)
        .bind(...params)
        .first<T>()) as T | null;
    },
  };
}

export function getDb(): Db {
  const d1 = (env as { DB?: D1Database }).DB;
  if (!d1) {
    throw new Error(
      "D1 binding 'DB' is unavailable. For local dev, seed a local D1 " +
        "(see wrangler.jsonc) and run `bun run dev`.",
    );
  }
  return d1Db(d1);
}

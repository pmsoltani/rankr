#!/usr/bin/env bun
/**
 * Render a markdown traffic report for rankr.online from Cloudflare's GraphQL
 * Analytics API: traffic for today, the last 7 days and the last 30 days, then
 * account usage against the free-tier limits.
 *
 *   bun run report                    # full report
 *   bun run report -- --out usage.md  # write to a file instead of stdout
 *   bun run report -- --top 25        # widen the "top N" tables
 *
 * The free-tier section exists because there is no `wrangler` equivalent:
 * wrangler introspects one product at a time (`d1 info`, `d1 insights`,
 * `kv namespace list`) and the dashboard splits the same numbers across pages.
 *
 * Tables are emitted with their borders aligned, so the report is as readable in
 * a terminal as it is rendered, and the output is already formatted;
 * formatting a generated file is a no-op. Use `--out` or `bun run --silent` when
 * redirecting: a plain `bun run report > f.md` captures bun's own banner line too.
 *
 * Auth, in order of preference:
 *   1. $CLOUDFLARE_API_TOKEN, an API token with Zone:Read + Zone Analytics:Read
 *      (dash → My Profile → API Tokens). Preferred, and required in CI.
 *   2. The local wrangler OAuth token, if you are already `wrangler login`ed.
 *      That token expires hourly; this refreshes it via wrangler when stale.
 *
 * Free-plan limits shape this report, and they are not the same for both halves:
 *   - Per-path data (`httpRequestsAdaptiveGroups`) is retained ~8 days. Day and
 *     week sections therefore have page-level detail; the month section cannot.
 *   - The daily rollup (`httpRequests1dGroups`) keeps ~30 days but has no path
 *     dimension, so the month section reports totals, countries and statuses only.
 *   - Referrer and bot-score dimensions are Pro+; they are absent here on purpose,
 *     not by oversight.
 */

import {
  existsSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND = dirname(dirname(fileURLToPath(import.meta.url)));
const GRAPHQL = "https://api.cloudflare.com/client/v4/graphql";
const ZONE_NAME = process.env.RANKR_ZONE ?? "rankr.online";

const args = process.argv.slice(2);
const flag = (name: string) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? undefined : args[i + 1];
};
const TOP = Number(flag("top") ?? 15);
const OUT = flag("out");

// ---------------------------------------------------------------------- auth --
// wrangler stores its OAuth token under XDG config on every platform it can.
const WRANGLER_CONFIGS = [
  join(
    homedir(),
    "AppData",
    "Roaming",
    "xdg.config",
    ".wrangler",
    "config",
    "default.toml",
  ),
  join(homedir(), ".wrangler", "config", "default.toml"),
  join(homedir(), ".config", ".wrangler", "config", "default.toml"),
];

function readWranglerToken(): { token: string; expires: number } | undefined {
  for (const path of WRANGLER_CONFIGS) {
    if (!existsSync(path)) continue;
    const text = readFileSync(path, "utf8");
    const token = text.match(/^oauth_token = "([^"]+)"/m)?.[1];
    if (!token) continue;
    const expiry = text.match(/^expiration_time = "([^"]+)"/m)?.[1];
    return { token, expires: expiry ? Date.parse(expiry) : 0 };
  }
  return undefined;
}

let TOKEN = process.env.CLOUDFLARE_API_TOKEN ?? readWranglerToken()?.token;
if (!TOKEN) {
  console.error(
    "no Cloudflare credentials found.\n" +
      "Either run `bunx wrangler login`, or create an API token with\n" +
      "Zone:Read + Zone Analytics:Read and export it as CLOUDFLARE_API_TOKEN.",
  );
  process.exit(1);
}

/**
 * The wrangler OAuth token lives about an hour and only wrangler renews it, so
 * ask wrangler to, then re-read the file.
 *
 * Deliberately ignores the exit status: every CLI on Windows returns 1 even on
 * a fully successful run (see scripts/verify-build.ts), so the only trustworthy
 * signal is whether the token on disk actually changed.
 */
function refreshToken(): boolean {
  if (process.env.CLOUDFLARE_API_TOKEN) return false; // not ours to refresh
  const before = TOKEN;
  Bun.spawnSync(["bunx", "wrangler", "whoami"], {
    cwd: FRONTEND,
    stdout: "ignore",
    stderr: "ignore",
  });
  TOKEN = readWranglerToken()?.token ?? TOKEN;
  return TOKEN !== before;
}

const looksLikeAuthFailure = (message: string) =>
  /authentication|invalid access token|unauthor|forbidden|9109|10000/i.test(message);

/**
 * Fetch with one refresh-and-retry on an auth failure.
 *
 * Expiry cannot be predicted reliably from `expiration_time`: a concurrent
 * wrangler command (a `tail`, another deploy) rotates the token and invalidates
 * the copy read a moment earlier, so a token that looks fresh can still be
 * rejected. Reacting to the rejection covers both that race and plain expiry.
 */
async function authedFetch(
  url: string,
  init: RequestInit = {},
  retried = false,
): Promise<{ body: any; authFailed: boolean }> {
  const res = await fetch(url, {
    ...init,
    headers: { ...init.headers, Authorization: `Bearer ${TOKEN}` },
  });
  const body = await res.json();
  const messages = [
    ...(body?.errors ?? []).map((e: { message?: string }) => e?.message ?? ""),
    res.status === 401 || res.status === 403 ? "unauthorized" : "",
  ].join(" ");
  const authFailed = Boolean(messages.trim()) && looksLikeAuthFailure(messages);
  if (authFailed && !retried && refreshToken()) {
    return authedFetch(url, init, true);
  }
  return { body, authFailed };
}

/** Distinguish an expired local token from a genuinely wrong one. */
function authHint(): string {
  return process.env.CLOUDFLARE_API_TOKEN
    ? "Check that $CLOUDFLARE_API_TOKEN has Zone:Read and Zone Analytics:Read."
    : "The wrangler login may have expired; run `bunx wrangler login` and retry,\n" +
        "or export a CLOUDFLARE_API_TOKEN with Zone:Read + Zone Analytics:Read.";
}

async function graphql<T>(
  scope: "zones" | "accounts",
  query: string,
  variables: Record<string, unknown>,
): Promise<T> {
  const { body, authFailed } = await authedFetch(GRAPHQL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  const json = body as {
    data?: { viewer?: Record<string, T[]> };
    errors?: { message: string }[];
  };
  if (json.errors?.length) {
    const reason = json.errors.map((e) => e.message).join("; ");
    throw new Error(authFailed ? `${reason}\n${authHint()}` : reason);
  }
  const node = json.data?.viewer?.[scope]?.[0];
  if (!node) throw new Error(`no analytics returned for this ${scope.slice(0, -1)}`);
  return node;
}

const gql = <T>(query: string, variables: Record<string, unknown>) =>
  graphql<T>("zones", query, variables);

/** Resolve a single id from a REST list endpoint. */
async function restId(url: string, what: string): Promise<string> {
  const { body } = await authedFetch(url);
  const json = body as {
    success: boolean;
    result?: { id: string }[];
    errors?: { message: string }[];
  };
  if (!json.success || !json.result?.length) {
    const reason = json.errors?.map((e) => e.message).join("; ") ?? "not found";
    throw new Error(`could not resolve ${what}: ${reason}\n${authHint()}`);
  }
  return json.result[0].id;
}

/** Free-tier limits are per account, so quota checks need the account, not the zone. */
const accountId = () =>
  process.env.CLOUDFLARE_ACCOUNT_ID
    ? Promise.resolve(process.env.CLOUDFLARE_ACCOUNT_ID)
    : restId("https://api.cloudflare.com/client/v4/accounts", "account");

const zoneId = () =>
  process.env.CLOUDFLARE_ZONE_ID
    ? Promise.resolve(process.env.CLOUDFLARE_ZONE_ID)
    : restId(
        `https://api.cloudflare.com/client/v4/zones?name=${encodeURIComponent(ZONE_NAME)}`,
        `zone "${ZONE_NAME}"`,
      );

// ------------------------------------------------------------------- helpers --
const iso = (d: Date) => d.toISOString().slice(0, 10);
const daysAgo = (n: number) => new Date(Date.now() - n * 86_400_000);
const num = (n: number) => n.toLocaleString("en-US");
const bytes = (n: number) => {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let v = n;
  let u = 0;
  while (v >= 1024 && u < units.length - 1) ((v /= 1024), u++);
  return `${v.toFixed(1)} ${units[u]}`;
};
const pct = (part: number, whole: number) =>
  whole ? `${((part / whole) * 100).toFixed(1)}%` : "—";

/**
 * Institution URLs dominate the top-pages table but read as opaque ROR ids, so
 * label them where the build data is on hand. Absent (a fresh clone that has not
 * run `build:data`), paths are shown bare rather than failing.
 */
function pathLabeller(): (path: string) => string {
  let names: Map<string, string> | undefined;
  const index = join(FRONTEND, "public", "search.json");
  if (existsSync(index)) {
    try {
      const entries = JSON.parse(readFileSync(index, "utf8")) as {
        r: string;
        n: string;
      }[];
      names = new Map(entries.map((e) => [e.r, e.n]));
    } catch {
      /* unreadable index → fall through to bare paths */
    }
  }
  return (path: string) => {
    const ror = /^\/i\/([0-9a-z]+)\/?$/.exec(path)?.[1];
    const name = ror && names?.get(ror);
    return name ? `\`${path}\` — ${name}` : `\`${path}\``;
  };
}

/**
 * Render a markdown table with its borders aligned.
 *
 * Columns are sized by *display* width (`Bun.stringWidth`), not `String#length`.
 * Institution names in the top-pages table carry CJK, which occupies two
 * terminal columns per code unit; measuring UTF-16 units would leave every row
 * containing one short by exactly the number of wide characters in it.
 */
function table(header: string[], rows: (string | number)[][]): string {
  if (!rows.length) return "_No data for this period._\n";

  const body = rows.map((r) => r.map(String));
  const widths = header.map((h, i) =>
    // 3 is markdown's minimum separator length (`---`).
    Math.max(3, Bun.stringWidth(h), ...body.map((r) => Bun.stringWidth(r[i] ?? ""))),
  );

  const pad = (cell: string, i: number) =>
    cell + " ".repeat(Math.max(0, widths[i] - Bun.stringWidth(cell)));
  const row = (cells: string[]) => `| ${cells.map(pad).join(" | ")} |`;

  return (
    [
      row(header),
      `| ${widths.map((w) => "-".repeat(w)).join(" | ")} |`,
      ...body.map(row),
    ].join("\n") + "\n"
  );
}

// ------------------------------------------------------------------- queries --
interface AdaptiveRow {
  count: number;
  sum: { edgeResponseBytes: number; visits: number };
  dimensions: Record<string, string | number>;
}

const ADAPTIVE = `
query($zone:String!,$since:Time!,$until:Time!,$limit:Int!){
  viewer{ zones(filter:{zoneTag:$zone}){
    total: httpRequestsAdaptiveGroups(limit:1, filter:{datetime_geq:$since, datetime_lt:$until}){
      count sum{ edgeResponseBytes visits }
    }
    paths: httpRequestsAdaptiveGroups(limit:$limit, filter:{datetime_geq:$since, datetime_lt:$until}, orderBy:[count_DESC]){
      count dimensions{ clientRequestPath }
    }
    countries: httpRequestsAdaptiveGroups(limit:$limit, filter:{datetime_geq:$since, datetime_lt:$until}, orderBy:[count_DESC]){
      count dimensions{ clientCountryName }
    }
    statuses: httpRequestsAdaptiveGroups(limit:20, filter:{datetime_geq:$since, datetime_lt:$until}, orderBy:[count_DESC]){
      count dimensions{ edgeResponseStatus }
    }
    devices: httpRequestsAdaptiveGroups(limit:10, filter:{datetime_geq:$since, datetime_lt:$until}, orderBy:[count_DESC]){
      count dimensions{ clientDeviceType }
    }
    browsers: httpRequestsAdaptiveGroups(limit:10, filter:{datetime_geq:$since, datetime_lt:$until}, orderBy:[count_DESC]){
      count dimensions{ userAgentBrowser }
    }
  }}}`;

const DAILY = `
query($zone:String!,$since:Date!,$until:Date!){
  viewer{ zones(filter:{zoneTag:$zone}){
    daily: httpRequests1dGroups(limit:60, filter:{date_geq:$since, date_lt:$until}, orderBy:[date_ASC]){
      dimensions{ date }
      sum{ requests pageViews bytes threats
           countryMap{ clientCountryName requests }
           responseStatusMap{ edgeResponseStatus requests }
      }
      uniq{ uniques }
    }
  }}}`;

const label = pathLabeller();

interface AdaptiveChunk {
  total: AdaptiveRow[];
  paths: AdaptiveRow[];
  countries: AdaptiveRow[];
  statuses: AdaptiveRow[];
  devices: AdaptiveRow[];
  browsers: AdaptiveRow[];
}

/**
 * The Free plan refuses a path-level query spanning more than one day, so a
 * multi-day window has to be fetched a day at a time and merged here. Each
 * chunk's own "top N" is a per-day top N, which is why the merge sums across
 * chunks before re-ranking rather than trusting any single chunk's order.
 */
function mergeCounts(
  chunks: AdaptiveChunk[],
  key: keyof AdaptiveChunk,
  dim: string,
): [string, number][] {
  const totals = new Map<string, number>();
  for (const chunk of chunks) {
    for (const row of chunk[key] as AdaptiveRow[]) {
      const name = String(row.dimensions[dim]);
      totals.set(name, (totals.get(name) ?? 0) + row.count);
    }
  }
  return [...totals.entries()].sort((a, b) => b[1] - a[1]);
}

/** Split [since, until) into windows of at most one day. */
function dayChunks(since: Date, until: Date): [Date, Date][] {
  const out: [Date, Date][] = [];
  let cursor = since;
  while (cursor < until) {
    const next = new Date(Math.min(cursor.getTime() + 86_400_000, until.getTime()));
    out.push([cursor, next]);
    cursor = next;
  }
  return out;
}

async function windowSection(
  title: string,
  note: string,
  zone: string,
  since: Date,
  until: Date,
): Promise<string> {
  const chunks: AdaptiveChunk[] = [];
  const failures: string[] = [];
  for (const [from, to] of dayChunks(since, until)) {
    try {
      chunks.push(
        await gql<AdaptiveChunk>(ADAPTIVE, {
          zone,
          since: from.toISOString(),
          until: to.toISOString(),
          // Per-day top-N must be generous: a page ranked 30th on each of seven
          // days can still be a top-10 page for the week.
          limit: Math.max(TOP * 4, 50),
        }),
      );
    } catch (err) {
      failures.push(`${iso(from)}: ${(err as Error).message}`);
    }
  }
  if (!chunks.length) {
    return `## ${title}\n\n_Unavailable: ${failures[0] ?? "no data"}_\n`;
  }

  const requests = chunks.reduce((n, c) => n + (c.total[0]?.count ?? 0), 0);
  const visits = chunks.reduce((n, c) => n + (c.total[0]?.sum.visits ?? 0), 0);
  const served = chunks.reduce(
    (n, c) => n + (c.total[0]?.sum.edgeResponseBytes ?? 0),
    0,
  );
  if (!requests) return `## ${title}\n\n${note}\n\n_No traffic recorded._\n`;

  const rows = (
    key: keyof AdaptiveChunk,
    dim: string,
    limit = TOP,
    fmt = (v: string) => v,
  ) =>
    mergeCounts(chunks, key, dim)
      .slice(0, limit)
      .map(([name, n]) => [fmt(name), num(n), pct(n, requests)]);

  return [
    `## ${title}`,
    "",
    note,
    "",
    `**${num(requests)} requests** · **${num(visits)} visits** · ${bytes(served)} served`,
    ...(failures.length
      ? ["", `_Partial: ${failures.length} day(s) unavailable (${failures[0]})._`]
      : []),
    "",
    "### Most visited pages",
    "",
    table(
      ["Page", "Requests", "Share"],
      rows("paths", "clientRequestPath", TOP, label),
    ),
    "### Top countries",
    "",
    table(["Country", "Requests", "Share"], rows("countries", "clientCountryName")),
    "### Response status",
    "",
    table(["Status", "Requests", "Share"], rows("statuses", "edgeResponseStatus", 20)),
    "### Device & browser",
    "",
    table(["Device", "Requests", "Share"], rows("devices", "clientDeviceType", 10)),
    table(["Browser", "Requests", "Share"], rows("browsers", "userAgentBrowser", 10)),
  ].join("\n");
}

async function monthSection(zone: string): Promise<string> {
  interface DailyRow {
    dimensions: { date: string };
    sum: {
      requests: number;
      pageViews: number;
      bytes: number;
      threats: number;
      countryMap: { clientCountryName: string; requests: number }[];
      responseStatusMap: { edgeResponseStatus: number; requests: number }[];
    };
    uniq: { uniques: number };
  }
  let data: { daily: DailyRow[] };
  try {
    data = await gql(DAILY, {
      zone,
      since: iso(daysAgo(30)),
      until: iso(daysAgo(0)),
    });
  } catch (err) {
    return `## Last 30 days\n\n_Unavailable: ${(err as Error).message}_\n`;
  }

  const days = data.daily;
  if (!days.length) return "## Last 30 days\n\n_No traffic recorded._\n";

  const totals = days.reduce(
    (acc, d) => ({
      requests: acc.requests + d.sum.requests,
      pageViews: acc.pageViews + d.sum.pageViews,
      bytes: acc.bytes + d.sum.bytes,
      uniques: acc.uniques + d.uniq.uniques,
      threats: acc.threats + d.sum.threats,
    }),
    { requests: 0, pageViews: 0, bytes: 0, uniques: 0, threats: 0 },
  );

  const byCountry = new Map<string, number>();
  for (const d of days) {
    for (const c of d.sum.countryMap) {
      byCountry.set(
        c.clientCountryName,
        (byCountry.get(c.clientCountryName) ?? 0) + c.requests,
      );
    }
  }
  const topCountries = [...byCountry.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, TOP);

  const byStatus = new Map<number, number>();
  for (const d of days) {
    for (const s of d.sum.responseStatusMap) {
      byStatus.set(
        s.edgeResponseStatus,
        (byStatus.get(s.edgeResponseStatus) ?? 0) + s.requests,
      );
    }
  }

  // A sparkline makes the shape of the month legible without a chart.
  const blocks = "▁▂▃▄▅▆▇█";
  const max = Math.max(...days.map((d) => d.sum.requests), 1);
  const spark = days
    .map((d) => blocks[Math.min(7, Math.floor((d.sum.requests / max) * 7))])
    .join("");

  return [
    "## Last 30 days",
    "",
    "_Cloudflare's Free plan keeps per-path analytics for about 8 days, so this",
    "section reports totals, countries and statuses but not individual pages._",
    "",
    `**${num(totals.requests)} requests** · **${num(totals.pageViews)} page views** · ` +
      `**${num(totals.uniques)} unique visitors** · ${bytes(totals.bytes)} served` +
      (totals.threats ? ` · ${num(totals.threats)} threats blocked` : ""),
    "",
    `Daily requests: \`${spark}\` (${days[0].dimensions.date} → ${days[days.length - 1].dimensions.date}, peak ${num(max)})`,
    "",
    "### Top countries",
    "",
    table(
      ["Country", "Requests", "Share"],
      topCountries.map(([c, n]) => [c, num(n), pct(n, totals.requests)]),
    ),
    "### Response status",
    "",
    table(
      ["Status", "Requests", "Share"],
      [...byStatus.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([s, n]) => [String(s), num(n), pct(n, totals.requests)]),
    ),
    "### Daily detail",
    "",
    table(
      ["Date", "Requests", "Page views", "Uniques", "Bytes"],
      days.map((d) => [
        d.dimensions.date,
        num(d.sum.requests),
        num(d.sum.pageViews),
        num(d.uniq.uniques),
        bytes(d.sum.bytes),
      ]),
    ),
  ].join("\n");
}

// ------------------------------------------------------------- free-tier use --
/**
 * Usage against the free-tier limits.
 *
 * Every limit here is per *account*, so a second Worker in the same account
 * draws on the same daily request budget. The per-script breakdown below exists
 * to make that visible.
 */

// Verified against Cloudflare's published free-plan limits.
const LIMITS = {
  workerRequests: 100_000, // per day, account-wide; static-asset hits are exempt
  d1RowsRead: 5_000_000, // per day
  d1RowsWritten: 100_000, // per day
  kvReads: 100_000, // per day
  kvWrites: 1_000, // per day
  assetFiles: 20_000, // per Worker version
  assetFileBytes: 25 * 1024 * 1024, // per file
};

interface WorkerRow {
  dimensions: { scriptName: string };
  sum: { requests: number; errors: number };
}
interface D1Row {
  dimensions: { databaseId: string };
  sum: { rowsRead: number; rowsWritten: number };
}
interface KvRow {
  dimensions: { namespaceId: string; actionType: string };
  sum: { requests: number };
}

async function quotaSection(): Promise<string> {
  let account: string;
  try {
    account = await accountId();
  } catch (err) {
    return `## Free-tier usage\n\n_Unavailable: ${(err as Error).message}_\n`;
  }

  const since = `${iso(new Date())}T00:00:00Z`;
  const until = new Date().toISOString();
  const today = iso(new Date());
  const tomorrow = iso(daysAgo(-1));

  const workers = await graphql<{ workersInvocationsAdaptive: WorkerRow[] }>(
    "accounts",
    `
      query ($a: String!, $since: Time!, $until: Time!) {
        viewer {
          accounts(filter: { accountTag: $a }) {
            workersInvocationsAdaptive(
              limit: 100
              filter: { datetime_geq: $since, datetime_lt: $until }
            ) {
              dimensions {
                scriptName
              }
              sum {
                requests
                errors
              }
            }
          }
        }
      }
    `,
    { a: account, since, until },
  ).catch(() => ({ workersInvocationsAdaptive: [] as WorkerRow[] }));

  const d1 = await graphql<{ d1AnalyticsAdaptiveGroups: D1Row[] }>(
    "accounts",
    `
      query ($a: String!, $since: Date!, $until: Date!) {
        viewer {
          accounts(filter: { accountTag: $a }) {
            d1AnalyticsAdaptiveGroups(
              limit: 100
              filter: { date_geq: $since, date_lt: $until }
            ) {
              dimensions {
                databaseId
              }
              sum {
                rowsRead
                rowsWritten
              }
            }
          }
        }
      }
    `,
    { a: account, since: today, until: tomorrow },
  ).catch(() => ({ d1AnalyticsAdaptiveGroups: [] as D1Row[] }));

  const kv = await graphql<{ kvOperationsAdaptiveGroups: KvRow[] }>(
    "accounts",
    `
      query ($a: String!, $since: Date!, $until: Date!) {
        viewer {
          accounts(filter: { accountTag: $a }) {
            kvOperationsAdaptiveGroups(
              limit: 100
              filter: { date_geq: $since, date_lt: $until }
            ) {
              dimensions {
                namespaceId
                actionType
              }
              sum {
                requests
              }
            }
          }
        }
      }
    `,
    { a: account, since: today, until: tomorrow },
  ).catch(() => ({ kvOperationsAdaptiveGroups: [] as KvRow[] }));

  const sum = <T>(list: T[], pick: (row: T) => number) =>
    list.reduce((n, row) => n + pick(row), 0);

  const rows: (string | number)[][] = [];
  const add = (label: string, used: number, limit: number, fmt = num) => {
    const ratio = limit ? used / limit : 0;
    rows.push([
      label,
      fmt(used),
      fmt(limit),
      `${(ratio * 100).toFixed(ratio < 0.1 ? 2 : 1)}%`,
      ratio >= 1 ? "OVER" : ratio >= 0.8 ? "high" : "ok",
    ]);
  };

  add(
    "Worker requests",
    sum(workers.workersInvocationsAdaptive, (w) => w.sum.requests),
    LIMITS.workerRequests,
  );
  add(
    "D1 rows read",
    sum(d1.d1AnalyticsAdaptiveGroups, (d) => d.sum.rowsRead),
    LIMITS.d1RowsRead,
  );
  add(
    "D1 rows written",
    sum(d1.d1AnalyticsAdaptiveGroups, (d) => d.sum.rowsWritten),
    LIMITS.d1RowsWritten,
  );
  const kvOps = (type: string) =>
    sum(
      kv.kvOperationsAdaptiveGroups.filter((k) => k.dimensions.actionType === type),
      (k) => k.sum.requests,
    );
  add("KV reads", kvOps("read"), LIMITS.kvReads);
  add("KV writes", kvOps("write"), LIMITS.kvWrites);

  // Asset counts come from the local build: the cap is per deployed version, not
  // per day, so this is only meaningful right after `bun run build`.
  const client = join(FRONTEND, "dist", "client");
  if (existsSync(client)) {
    let files = 0;
    let biggest = 0;
    (function walk(dir: string) {
      for (const entry of readdirSync(dir, { withFileTypes: true })) {
        const path = join(dir, entry.name);
        if (entry.isDirectory()) walk(path);
        else {
          files++;
          biggest = Math.max(biggest, statSync(path).size);
        }
      }
    })(client);
    add("Static asset files", files, LIMITS.assetFiles);
    add("Largest single asset", biggest, LIMITS.assetFileBytes, bytes);
  }

  const out = [
    "## Free-tier usage",
    "",
    "_Today so far (UTC). Limits are per account, not per Worker or zone._",
    "",
    table(["Resource", "Used", "Limit", "Share", ""], rows),
  ];

  const scripts = workers.workersInvocationsAdaptive
    .filter((w) => w.sum.requests > 0)
    .sort((a, b) => b.sum.requests - a.sum.requests);
  if (scripts.length > 1) {
    out.push(
      "### Worker requests by script",
      "",
      "_All scripts in the account share the same 100k/day budget._",
      "",
      table(
        ["Script", "Requests", "Errors"],
        scripts.map((w) => [
          `\`${w.dimensions.scriptName}\``,
          num(w.sum.requests),
          num(w.sum.errors),
        ]),
      ),
    );
  }

  const kvByNamespace = new Map<string, number>();
  for (const k of kv.kvOperationsAdaptiveGroups) {
    kvByNamespace.set(
      k.dimensions.namespaceId,
      (kvByNamespace.get(k.dimensions.namespaceId) ?? 0) + k.sum.requests,
    );
  }
  if (kvByNamespace.size) {
    out.push(
      "### KV namespaces in use",
      "",
      "_Check here before deleting a namespace that looks unreferenced._",
      "",
      table(
        ["Namespace", "Operations"],
        [...kvByNamespace]
          .sort((a, b) => b[1] - a[1])
          .map(([id, n]) => [`\`${id}\``, num(n)]),
      ),
    );
  }

  return out.join("\n");
}

// ---------------------------------------------------------------------- main --
const zone = await zoneId();
const now = new Date();
const startOfToday = new Date(
  Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()),
);

/**
 * Sections compose from pieces that each end in their own newline, so joining
 * them leaves runs of blank lines. Collapse those (and any trailing space).
 */
const tidy = (md: string) =>
  md
    .replace(/[ \t]+$/gm, "")
    .replace(/\n{3,}/g, "\n\n")
    .trimEnd() + "\n";

const report = tidy(
  [
    `# ${ZONE_NAME} — usage report`,
    "",
    `_Generated ${now.toISOString().replace("T", " ").slice(0, 16)} UTC_`,
    "",
    await windowSection(
      "Today so far",
      `_${iso(startOfToday)} 00:00 UTC → now._`,
      zone,
      startOfToday,
      now,
    ),
    "",
    await windowSection(
      "Last 7 days",
      `_${iso(daysAgo(7))} → ${iso(now)}._`,
      zone,
      daysAgo(7),
      now,
    ),
    "",
    await monthSection(zone),
    "",
    await quotaSection(),
  ].join("\n"),
);

if (OUT) {
  writeFileSync(OUT, report);
  console.log(`wrote ${OUT}`);
} else {
  // process.stdout avoids console.log's trailing newline on top of tidy()'s.
  process.stdout.write(report);
}

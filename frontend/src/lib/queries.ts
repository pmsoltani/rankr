import type { Db } from "@/lib/db";
import type {
  Country,
  Institution,
  InstitutionDetail,
  InstitutionLink,
  InstitutionRankingData,
  Ranking,
  RankingSystems,
  RankingTableRow,
  SearchResult,
} from "@/lib/types";

const STAT_METRICS = [
  "# FTE Students",
  "# Students per Staff",
  "% International Students",
  "% Female Students",
];

// D1 stores one collapsed `ranking` row per (institution, system, type, year,
// field, subject); the per-metric data lives in a `metrics` JSON blob keyed by
// metric name. We re-expand it into the flat per-metric `Ranking[]` that the
// chart components expect, so the collapse stays invisible above this layer.
interface CollapsedRanking {
  institution_id: number;
  ranking_system: string;
  ranking_type: string;
  year: number;
  field: string;
  subject: string;
  metrics: string;
}

type MetricEntry = {
  raw_value: string | null;
  value: number | string | null;
  value_type: string;
};

function expand(row: CollapsedRanking): Ranking[] {
  const metrics = JSON.parse(row.metrics) as Record<string, MetricEntry>;
  return Object.entries(metrics).map(([metric, m]) => ({
    id: 0, // synthetic — the collapsed table has no per-metric id, and nothing reads it
    institution_id: row.institution_id,
    ranking_system: row.ranking_system,
    ranking_type: row.ranking_type,
    year: row.year,
    field: row.field,
    subject: row.subject,
    metric,
    raw_value: m.raw_value,
    value: m.value,
    value_type: m.value_type,
  }));
}

const bySystemYear = (a: Ranking, b: Ranking) =>
  a.ranking_system.localeCompare(b.ranking_system) || a.year - b.year;
const bySystemYearMetric = (a: Ranking, b: Ranking) =>
  bySystemYear(a, b) || a.metric.localeCompare(b.metric);

// All (university-ranking, All/All) metric rows for one institution, flattened.
async function institutionRankings(db: Db, institutionId: number): Promise<Ranking[]> {
  const rows = await db.all<CollapsedRanking>(
    `SELECT institution_id, ranking_system, ranking_type, year, field, subject, metrics
     FROM ranking
     WHERE institution_id = ? AND ranking_type = 'university ranking'
       AND field = 'All' AND subject = 'All'`,
    [institutionId],
  );
  return rows.flatMap(expand);
}

export async function getInstitutionByRorId(
  db: Db,
  rorId: string,
): Promise<InstitutionDetail | null> {
  const institution = await db.first<Institution>(
    "SELECT * FROM institution WHERE ror_id = ?",
    [rorId],
  );
  if (!institution) return null;

  const country = institution.country_id
    ? await db.first<Country>("SELECT * FROM country WHERE id = ?", [
        institution.country_id,
      ])
    : null;

  const links = await db.all<InstitutionLink>(
    "SELECT type, link FROM link WHERE institution_id = ?",
    [institution.id],
  );

  const all = await institutionRankings(db, institution.id);
  const ranks = all.filter((r) => r.metric === "Rank").sort(bySystemYear);
  const scores = all.filter((r) => r.metric.endsWith("Score")).sort(bySystemYearMetric);

  // THE stats (student counts/ratios) for the institution's latest THE year.
  const theRows = all.filter((r) => r.ranking_system === "the");
  const latestYear = theRows.length ? Math.max(...theRows.map((r) => r.year)) : null;
  const stats =
    latestYear === null
      ? []
      : theRows.filter((r) => r.year === latestYear && STAT_METRICS.includes(r.metric));

  return { ...institution, country, links, ranks, scores, stats };
}

export async function getRankingSystems(db: Db): Promise<RankingSystems> {
  const rows = await db.all<{ ranking_system: string; year: number }>(
    `SELECT DISTINCT ranking_system, year FROM ranking
     WHERE ranking_type = 'university ranking' AND field = 'All' AND subject = 'All'
     ORDER BY ranking_system, year DESC`,
  );
  const systems: RankingSystems = {};
  for (const r of rows) (systems[r.ranking_system] ??= []).push(r.year);
  return systems;
}

export async function getRankingTable(
  db: Db,
  system: string,
  year: number,
  page = 1,
  perPage = 50,
  country?: string,
): Promise<{ rows: RankingTableRow[]; total: number }> {
  const offset = (page - 1) * perPage;
  // One collapsed row per institution for this system+year; the rank lives in
  // metrics.Rank. Non-numeric ranks (THE's "Reporter" tier, value NULL) sort last.
  const base = `FROM ranking r
     JOIN institution i ON i.id = r.institution_id
     LEFT JOIN country c ON c.id = i.country_id
     WHERE r.ranking_system = ? AND r.ranking_type = 'university ranking'
       AND r.field = 'All' AND r.subject = 'All'
       AND r.year = ?${country ? " AND c.country = ?" : ""}`;
  const filters = country ? [system, year, country] : [system, year];
  const rows = await db.all<RankingTableRow>(
    `SELECT i.ror_id, i.name, c.country, c.country_code,
       json_extract(r.metrics, '$.Rank.raw_value') AS raw_value,
       json_extract(r.metrics, '$.Rank.value') AS value
     ${base}
     ORDER BY (json_extract(r.metrics, '$.Rank.value') IS NULL),
              json_extract(r.metrics, '$.Rank.value')
     LIMIT ? OFFSET ?`,
    [...filters, perPage, offset],
  );
  const total = await db.first<{ n: number }>(`SELECT COUNT(*) AS n ${base}`, filters);
  return { rows, total: total?.n ?? 0 };
}

export async function getCountries(
  db: Db,
  system: string,
  year: number,
): Promise<{ country: string; country_code: string }[]> {
  return db.all<{ country: string; country_code: string }>(
    `SELECT DISTINCT c.country, c.country_code
     FROM ranking r
     JOIN institution i ON i.id = r.institution_id
     JOIN country c ON c.id = i.country_id
     WHERE r.ranking_system = ? AND r.ranking_type = 'university ranking'
       AND r.field = 'All' AND r.subject = 'All'
       AND r.year = ?
     ORDER BY c.country`,
    [system, year],
  );
}

export async function searchInstitutions(
  db: Db,
  query: string,
  limit = 20,
): Promise<SearchResult[]> {
  const q = query.trim();
  if (!q) return [];
  // Match the pipe-joined `soup` blob (name | country | acronyms | aliases |
  // labels). The D1 institution table holds only ranked institutions (the seed
  // projects them), so a plain scan over ~3k rows is cheap, no ranked-subset
  // filter needed. Name-prefix matches rank first, then shorter names, so the
  // canonical institution surfaces near the top.
  return db.all<SearchResult>(
    `SELECT i.ror_id, i.name, c.country, c.country_code
     FROM institution i
     LEFT JOIN country c ON c.id = i.country_id
     WHERE i.soup LIKE ?
     ORDER BY
       CASE WHEN i.name LIKE ? THEN 0 ELSE 1 END,
       LENGTH(i.name)
     LIMIT ?`,
    [`%${q}%`, `${q}%`, limit],
  );
}

// Lean ranks + scores for one institution, used by the Compare island's
// per-institution fetch (/api/institution/[rorId]).
export async function getInstitutionRankingData(
  db: Db,
  rorId: string,
): Promise<InstitutionRankingData | null> {
  const inst = await db.first<{
    id: number;
    ror_id: string;
    name: string;
    country_code: string | null;
  }>(
    `SELECT i.id, i.ror_id, i.name, c.country_code
     FROM institution i
     LEFT JOIN country c ON c.id = i.country_id
     WHERE i.ror_id = ?`,
    [rorId],
  );
  if (!inst) return null;

  const all = await institutionRankings(db, inst.id);
  const ranks = all.filter((r) => r.metric === "Rank").sort(bySystemYear);
  const scores = all.filter((r) => r.metric.endsWith("Score")).sort(bySystemYearMetric);

  return {
    ror_id: inst.ror_id,
    name: inst.name,
    country_code: inst.country_code,
    ranks,
    scores,
  };
}

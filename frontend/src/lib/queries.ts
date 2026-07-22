import type { Db } from "@/lib/db";
import type {
  Country,
  Institution,
  InstitutionDetail,
  InstitutionLink,
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

export async function getInstitutionByRorId(
  db: Db,
  rorId: string,
): Promise<InstitutionDetail | null> {
  const institution = await db.first<Institution>(
    "SELECT * FROM institution WHERE ror_id = ?",
    [rorId],
  );
  if (!institution) return null;

  const id = institution.id;

  const country = institution.country_id
    ? await db.first<Country>("SELECT * FROM country WHERE id = ?", [
        institution.country_id,
      ])
    : null;

  const [acronyms, aliases, labels, links, types] = await Promise.all([
    db.all<{ acronym: string }>(
      "SELECT acronym FROM acronym WHERE institution_id = ?",
      [id],
    ),
    db.all<{ alias: string }>("SELECT alias FROM alias WHERE institution_id = ?", [id]),
    db.all<{ iso639: string; label: string }>(
      "SELECT iso639, label FROM label WHERE institution_id = ?",
      [id],
    ),
    db.all<InstitutionLink>("SELECT type, link FROM link WHERE institution_id = ?", [
      id,
    ]),
    db.all<{ type: string }>("SELECT type FROM type WHERE institution_id = ?", [id]),
  ]);

  const ranks = await db.all<Ranking>(
    `SELECT * FROM ranking
     WHERE institution_id = ? AND ranking_type = 'university ranking'
       AND metric = 'Rank'
     ORDER BY ranking_system, year`,
    [id],
  );

  const latest = await db.first<{ year: number }>(
    `SELECT MAX(year) AS year FROM ranking
     WHERE institution_id = ? AND ranking_system = 'the'
       AND ranking_type = 'university ranking'
       AND field = 'All' AND subject = 'All'`,
    [id],
  );

  let stats: Ranking[] = [];
  if (latest?.year) {
    const placeholders = STAT_METRICS.map(() => "?").join(", ");
    stats = await db.all<Ranking>(
      `SELECT * FROM ranking
       WHERE institution_id = ? AND ranking_system = 'the'
         AND ranking_type = 'university ranking'
         AND field = 'All' AND subject = 'All'
         AND year = ? AND metric IN (${placeholders})`,
      [id, latest.year, ...STAT_METRICS],
    );
  }

  // Score metrics (percent sub-scores, all systems/years) for the score charts;
  // metric names end in "Score", which excludes Rank/National Rank and THE stats.
  const scores = await db.all<Ranking>(
    `SELECT * FROM ranking
     WHERE institution_id = ? AND ranking_type = 'university ranking'
       AND field = 'All' AND subject = 'All' AND metric LIKE '%Score'
     ORDER BY ranking_system, year, metric`,
    [id],
  );

  return {
    ...institution,
    country,
    acronyms: acronyms.map((a) => a.acronym),
    aliases: aliases.map((a) => a.alias),
    labels,
    links,
    types: types.map((t) => t.type),
    ranks,
    scores,
    stats,
  };
}

export async function getRankingSystems(db: Db): Promise<RankingSystems> {
  const rows = await db.all<{ ranking_system: string; year: number }>(
    `SELECT DISTINCT ranking_system, year FROM ranking
     WHERE ranking_type = 'university ranking' AND metric = 'Rank'
       AND field = 'All' AND subject = 'All'
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
  perPage = 100,
): Promise<{ rows: RankingTableRow[]; total: number }> {
  const offset = (page - 1) * perPage;
  const rows = await db.all<RankingTableRow>(
    `SELECT i.ror_id, i.name, c.country, c.country_code, r.raw_value, r.value
     FROM ranking r
     JOIN institution i ON i.id = r.institution_id
     LEFT JOIN country c ON c.id = i.country_id
     WHERE r.ranking_system = ? AND r.ranking_type = 'university ranking'
       AND r.metric = 'Rank' AND r.field = 'All' AND r.subject = 'All'
       AND r.year = ?
     ORDER BY r.value
     LIMIT ? OFFSET ?`,
    [system, year, perPage, offset],
  );
  const total = await db.first<{ n: number }>(
    `SELECT COUNT(*) AS n FROM ranking
     WHERE ranking_system = ? AND ranking_type = 'university ranking'
       AND metric = 'Rank' AND field = 'All' AND subject = 'All' AND year = ?`,
    [system, year],
  );
  return { rows, total: total?.n ?? 0 };
}

export async function searchInstitutions(
  db: Db,
  query: string,
  limit = 20,
): Promise<SearchResult[]> {
  const q = query.trim();
  if (!q) return [];
  // Match the pipe-joined `soup` blob (name | country | acronyms | aliases |
  // labels), limited to institutions that appear in any ranking. The
  // `id IN (…)` set lets SQLite drive from the small ranked subset via the
  // institution PK (fast) and drops the long tail of unranked orgs. Name-prefix
  // matches rank first, then shorter names, so the canonical institution
  // surfaces near the top.
  return db.all<SearchResult>(
    `SELECT i.ror_id, i.name, c.country, c.country_code
     FROM institution i
     LEFT JOIN country c ON c.id = i.country_id
     WHERE i.soup LIKE ?
       AND i.id IN (SELECT institution_id FROM ranking)
     ORDER BY
       CASE WHEN i.name LIKE ? THEN 0 ELSE 1 END,
       LENGTH(i.name)
     LIMIT ?`,
    [`%${q}%`, `${q}%`, limit],
  );
}

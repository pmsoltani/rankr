import type { Db } from "@/lib/db";
import type {
  Country,
  Institution,
  InstitutionDetail,
  InstitutionLink,
  Ranking,
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

  return {
    ...institution,
    country,
    acronyms: acronyms.map((a) => a.acronym),
    aliases: aliases.map((a) => a.alias),
    labels,
    links,
    types: types.map((t) => t.type),
    ranks,
    stats,
  };
}

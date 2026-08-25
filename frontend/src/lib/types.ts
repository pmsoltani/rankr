export interface Country {
  id: number;
  country: string;
  country_code: string;
  region: string;
  sub_region: string | null;
}

/**
 * One metric datum for an institution in a given ranking system and year.
 *
 * Deliberately narrower than the crawler's `ranking` row. Every row in the
 * source is `university ranking` / `All` / `All`, and nothing renders the
 * surrogate keys, so `id`, `institution_id`, `ranking_type`, `field` and
 * `subject` are dropped during projection (scripts/build-data.ts). They are
 * pure overhead here: these rows are serialized into every institution page's
 * hydration payload, ~400 of them for a long-ranked university.
 */
export interface Ranking {
  ranking_system: string;
  year: number;
  metric: string;
  raw_value: string | null;
  value: number | string | null;
}

/**
 * A THE student statistic (FTE students, % international, ...). Unlike ranks and
 * scores these are rendered as values with units, so they keep `value_type`.
 */
export interface InstitutionStat extends Ranking {
  value_type: string;
}

export interface InstitutionLink {
  type: string;
  link: string;
}

/** Everything /i/{rorId} renders. Built at build time, never shipped whole. */
export interface InstitutionDetail {
  ror_id: string;
  name: string;
  established: number | null;
  lat: string | null;
  lng: string | null;
  city: string | null;
  country: Country | null;
  links: InstitutionLink[];
  ranks: Ranking[];
  scores: Ranking[];
  stats: InstitutionStat[];
}

/** Lean payload for the Compare island (fetched client-side per institution). */
export interface InstitutionRankingData {
  ror_id: string;
  name: string;
  country_code: string | null;
  ranks: Ranking[];
  scores: Ranking[];
}

/** system id -> available years, e.g. { qs: [2018, ...], the: [...] } */
export type RankingSystems = Record<string, number[]>;

export interface RankingTableRow {
  ror_id: string;
  name: string;
  country: string | null;
  country_code: string | null;
  raw_value: string | null;
  value: number | string | null;
}

export interface SearchResult {
  ror_id: string;
  name: string;
  country: string | null;
  country_code: string | null;
}

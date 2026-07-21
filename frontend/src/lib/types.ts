export interface Country {
  id: number;
  country: string;
  country_code: string;
  region: string;
  sub_region: string | null;
}

export interface Ranking {
  id: number;
  institution_id: number;
  ranking_system: string;
  ranking_type: string;
  year: number;
  field: string;
  subject: string;
  metric: string;
  raw_value: string | null;
  value: number | string | null;
  value_type: string;
}

export interface Institution {
  id: number;
  ror_id: string;
  grid_id: string | null;
  name: string;
  established: number | null;
  lat: string | null;
  lng: string | null;
  city: string | null;
  state: string | null;
  country_id: number | null;
  soup: string | null;
}

export interface InstitutionLink {
  type: string;
  link: string;
}

export interface InstitutionDetail extends Institution {
  country: Country | null;
  acronyms: string[];
  aliases: string[];
  labels: { iso639: string; label: string }[];
  links: InstitutionLink[];
  types: string[];
  ranks: Ranking[];
  stats: Ranking[];
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

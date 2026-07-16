export const SITE = {
  name: "rankr",
  description:
    "rankr is a free and open-source platform for aggregating the results " +
    "of different academic rankings, which could help students get a clearer " +
    "picture about their next place of study.",
  url: "https://rankr.online",
  github: "https://github.com/pmsoltani/rankr",
  author: {
    name: "Pooria Soltani",
    url: "https://www.linkedin.com/in/pmsoltani",
  },
  // Institution identity provider (replaces the retired GRID).
  ror: {
    label: "Research Organization Registry (ROR)",
    url: "https://ror.org",
    baseURL: "https://ror.org/",
  },
} as const;

export type RankingSystemId = "qs" | "shanghai" | "the";

export const RANKING_SYSTEMS: Record<
  RankingSystemId,
  { alias: string; color: string; url: string; label: string }
> = {
  qs: {
    alias: "QS",
    color: "#feb019",
    url: "https://www.topuniversities.com",
    label: "Top Universities (QS)",
  },
  shanghai: {
    alias: "Shanghai",
    color: "#ff4560",
    url: "https://www.shanghairanking.com",
    label: "Shanghai Ranking",
  },
  the: {
    alias: "THE",
    color: "#008ffb",
    url: "https://www.timeshighereducation.com",
    label: "Times Higher Education (THE)",
  },
};

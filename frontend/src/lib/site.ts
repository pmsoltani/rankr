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

/**
 * Full metric name -> short chart label, per ranking system. Key order also
 * defines the display/sort order of score categories in the charts.
 */
export const SCORE_ALIASES: Record<RankingSystemId, Record<string, string>> = {
  qs: {
    "Overall Score": "Overall",
    "Academic Reputation Score": "Academic Rep.",
    "Employer Reputation Score": "Employer Rep.",
    "Faculty Student Score": "Faculty Student",
    "International Faculty Score": "Intl. Faculty",
    "International Students Score": "Intl. Student",
    "Citations per Faculty Score": "Cite/Faculty",
    "Citations per Paper Score": "Cite/Paper",
    "H-index Citations Score": "H-index Cite",
  },
  shanghai: {
    "Overall Score": "Overall",
    "Alumni Score": "Alumni",
    "Award Score": "Award",
    "HiCi Score": "HiCi",
    "N&S Score": "N&S",
    "PUB Score": "PUB",
    "PCP Score": "PCP",
    "CNCI Score": "CNCI",
    "IC Score": "IC",
    "TOP Score": "TOP",
    "Q1 Score": "Q1",
  },
  the: {
    "Overall Score": "Overall",
    "Teaching Score": "Teaching",
    "Research Score": "Research",
    "Citations Score": "Citations",
    "Industry Income Score": "Ind. Income",
    "International Outlook Score": "Intl. Outlook",
  },
};

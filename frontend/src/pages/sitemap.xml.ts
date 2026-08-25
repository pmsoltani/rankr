import type { APIRoute } from "astro";

import {
  getAllRankedRorIds,
  getRankingSystems,
  getRankingTableData,
  pageCount,
} from "@/lib/data";
import { SITE } from "@/lib/site";

export const prerender = true;

// GET /sitemap.xml: home, about, compare, every ranking table page (including
// pagination), and every ranked institution. Referenced from public/robots.txt.
// Built once at deploy time; the URL set only changes when the data does.
export const GET: APIRoute = () => {
  const systems = getRankingSystems();

  const paths = ["/", "/about", "/compare"];
  for (const [system, years] of Object.entries(systems)) {
    for (const year of years) {
      paths.push(`/rankings/${system}/${year}`);
      const { rows } = getRankingTableData(system, year);
      for (let page = 2; page <= pageCount(rows.length); page++) {
        paths.push(`/rankings/${system}/${year}/${page}`);
      }
    }
  }
  for (const ror of getAllRankedRorIds()) paths.push(`/i/${ror}`);

  const body =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    paths
      .map((p) => `  <url><loc>${new URL(p, SITE.url).href}</loc></url>`)
      .join("\n") +
    "\n</urlset>\n";

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};

import type { APIRoute } from "astro";

import { getDb } from "@/lib/db";
import { getAllRankedRorIds, getRankingSystems } from "@/lib/queries";
import { SITE } from "@/lib/site";

export const prerender = false;

// GET /sitemap.xml — home, about, compare, every ranking system/year table, and
// every ranked institution page. Referenced from public/robots.txt.
export const GET: APIRoute = async () => {
  const db = getDb();
  const [systems, rorIds] = await Promise.all([
    getRankingSystems(db),
    getAllRankedRorIds(db),
  ]);

  const paths = ["/", "/about", "/compare"];
  for (const [system, years] of Object.entries(systems)) {
    for (const year of years) paths.push(`/rankings/${system}/${year}`);
  }
  for (const ror of rorIds) paths.push(`/i/${ror}`);

  const body =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    paths
      .map((p) => `  <url><loc>${new URL(p, SITE.url).href}</loc></url>`)
      .join("\n") +
    "\n</urlset>\n";

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=86400",
    },
  });
};

import type { APIRoute } from "astro";

import { getDb } from "@/lib/db";
import { searchInstitutions } from "@/lib/queries";

export const prerender = false;

// GET /api/search?q=...: institution typeahead over D1 (used by the Search island).
export const GET: APIRoute = async ({ url }) => {
  const q = url.searchParams.get("q")?.trim() ?? "";
  if (q.length < 2) return Response.json([]);

  const results = await searchInstitutions(getDb(), q, 20);
  return Response.json(results);
};

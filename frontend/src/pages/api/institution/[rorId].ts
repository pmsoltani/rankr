import type { APIRoute } from "astro";

import { getDb } from "@/lib/db";
import { getInstitutionRankingData } from "@/lib/queries";

export const prerender = false;

// GET /api/institution/:rorId - lean ranks + scores for the Compare island.
export const GET: APIRoute = async ({ params }) => {
  const rorId = params.rorId?.trim();
  if (!rorId) return new Response("Bad request", { status: 400 });

  const data = await getInstitutionRankingData(getDb(), rorId);
  if (!data) return new Response("Not found", { status: 404 });

  return Response.json(data);
};

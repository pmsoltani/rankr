import {
  QueryClient,
  QueryClientProvider,
  useQueries,
} from "@tanstack/react-query";
import { XIcon } from "lucide-react";
import {
  parseAsArrayOf,
  parseAsInteger,
  parseAsString,
  parseAsStringLiteral,
  useQueryState,
} from "nuqs";
import { NuqsAdapter } from "nuqs/adapters/react";
import { useState } from "react";

import { CompareRadarChart } from "@/components/charts/CompareRadarChart";
import { CompareRankChart } from "@/components/charts/CompareRankChart";
import { RANKING_SYSTEMS, type RankingSystemId } from "@/lib/site";
import type { InstitutionRankingData, SearchResult } from "@/lib/types";
import { cn } from "@/lib/utils";

import { ComparePicker } from "./ComparePicker";

const SYSTEMS = ["qs", "shanghai", "the"] as const;
const MAX = 3;

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 5 * 60 * 1000 } },
});

// A prebuilt static asset, not an endpoint: scripts/build-data.ts writes one of
// these per ranked institution.
async function fetchInstitution(
  rorId: string,
): Promise<InstitutionRankingData> {
  const res = await fetch(`/api/institution/${encodeURIComponent(rorId)}.json`);
  if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
  return res.json() as Promise<InstitutionRankingData>;
}

function CompareInner() {
  const [ids, setIds] = useQueryState(
    "ids",
    parseAsArrayOf(parseAsString).withDefault([]),
  );
  const [system, setSystem] = useQueryState(
    "system",
    parseAsStringLiteral(SYSTEMS).withDefault("qs"),
  );
  const [year, setYear] = useQueryState("year", parseAsInteger);
  // Immediate chip labels so a freshly-added institution shows its name before its fetch resolves.
  const [nameHints, setNameHints] = useState<Record<string, string>>({});

  const results = useQueries({
    queries: ids.map((id) => ({
      queryKey: ["institution", id],
      queryFn: () => fetchInstitution(id),
    })),
  });
  const institutions = results
    .map((r) => r.data)
    .filter((d): d is InstitutionRankingData => Boolean(d));
  const loading = results.some((r) => r.isLoading);
  const nameById = new Map(institutions.map((i) => [i.ror_id, i.name]));

  const availableSystems = SYSTEMS.filter((s) =>
    institutions.some(
      (inst) =>
        inst.ranks.some((r) => r.ranking_system === s) ||
        inst.scores.some((sc) => sc.ranking_system === s),
    ),
  );
  const activeSystem: RankingSystemId = availableSystems.includes(system)
    ? system
    : (availableSystems[0] ?? system);

  const scoreYears = [
    ...new Set(
      institutions.flatMap((inst) =>
        inst.scores
          .filter((s) => s.ranking_system === activeSystem)
          .map((s) => s.year),
      ),
    ),
  ].sort((a, b) => b - a);
  const activeYear = year && scoreYears.includes(year) ? year : scoreYears[0];

  const add = (r: SearchResult) => {
    if (ids.includes(r.ror_id) || ids.length >= MAX) return;
    setNameHints((prev) => ({ ...prev, [r.ror_id]: r.name }));
    void setIds([...ids, r.ror_id]);
  };
  const remove = (id: string) => void setIds(ids.filter((x) => x !== id));

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {ids.map((id) => (
            <span
              key={id}
              className="flex items-center gap-1.5 rounded-full border bg-white py-1 pr-1 pl-3 text-sm"
            >
              <a
                href={`/i/${id}`}
                className="hover:text-foreground max-w-56 truncate hover:underline"
              >
                {nameById.get(id) ?? nameHints[id] ?? "..."}
              </a>
              <button
                type="button"
                onClick={() => remove(id)}
                aria-label="Remove institution"
                className="rounded-full p-0.5 hover:bg-neutral-100"
              >
                <XIcon className="size-3.5" />
              </button>
            </span>
          ))}
          <ComparePicker
            onAdd={add}
            disabled={ids.length >= MAX}
            excludeIds={ids}
          />
        </div>

        {institutions.length > 0 && (
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex gap-2">
              {SYSTEMS.map((s) => {
                const avail = availableSystems.includes(s);
                return (
                  <button
                    key={s}
                    type="button"
                    disabled={!avail}
                    onClick={() => void setSystem(s)}
                    className={cn(
                      "rounded-md px-3 py-1.5 text-sm font-medium",
                      !avail && "cursor-not-allowed opacity-40",
                      s === activeSystem
                        ? "bg-primary text-primary-foreground"
                        : "border hover:bg-neutral-100",
                    )}
                  >
                    {RANKING_SYSTEMS[s].alias}
                  </button>
                );
              })}
            </div>
            {scoreYears.length > 0 && (
              <label className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Score year</span>
                <select
                  value={activeYear}
                  onChange={(e) => void setYear(Number(e.target.value))}
                  className="rounded-md border bg-white px-2 py-1 text-xs tabular-nums"
                >
                  {scoreYears.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </label>
            )}
          </div>
        )}
      </div>

      {ids.length === 0 ? (
        <p className="text-muted-foreground rounded-lg border border-dashed py-16 text-center text-sm">
          Add institutions to compare their ranks and scores.
        </p>
      ) : loading && institutions.length === 0 ? (
        <p className="text-muted-foreground py-16 text-center text-sm">
          Loading...
        </p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <CompareRankChart institutions={institutions} system={activeSystem} />
          {activeYear ? (
            <CompareRadarChart
              institutions={institutions}
              system={activeSystem}
              year={activeYear}
            />
          ) : null}
        </div>
      )}
    </div>
  );
}

export default function CompareApp() {
  return (
    <NuqsAdapter>
      <QueryClientProvider client={queryClient}>
        <CompareInner />
      </QueryClientProvider>
    </NuqsAdapter>
  );
}

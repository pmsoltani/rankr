import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { lineDash, systemShades } from "@/lib/charts";
import { SCORE_ALIASES, type RankingSystemId } from "@/lib/site";
import type { InstitutionRankingData } from "@/lib/types";

import { ChartCard } from "./ChartCard";

interface TooltipItem {
  dataKey: string;
  name: string;
  value: number | null;
  color: string;
}

function CompareRadarTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipItem[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border bg-white px-3 py-2 text-xs shadow-sm">
      <div className="mb-1 font-medium">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center gap-2">
          <span
            className="inline-block size-2 rounded-full"
            style={{ background: p.color }}
          />
          <span className="text-muted-foreground max-w-44 truncate">{p.name}</span>
          <span className="ml-auto font-medium tabular-nums">{p.value ?? "—"}</span>
        </div>
      ))}
    </div>
  );
}

type RadarRow = { metric: string; [rorId: string]: number | string | null };

// Score comparison: one radar polygon per institution across a single ranking
// system's score metrics for a given year (0-100). Distinguished by line style
// + system-color shade.
export function CompareRadarChart({
  institutions,
  system,
  year,
}: {
  institutions: InstitutionRankingData[];
  system: RankingSystemId;
  year: number;
}) {
  const shades = systemShades(system, institutions.length);
  const aliasMap = SCORE_ALIASES[system];

  const rows: RadarRow[] = Object.keys(aliasMap)
    .map((metric): RadarRow | null => {
      const row: RadarRow = { metric: aliasMap[metric] };
      let hasValue = false;
      institutions.forEach((inst) => {
        const match = inst.scores.find(
          (s) => s.ranking_system === system && s.year === year && s.metric === metric,
        );
        const value = match && match.value !== null ? Number(match.value) : null;
        row[inst.ror_id] = value;
        if (value !== null) hasValue = true;
      });
      return hasValue ? row : null;
    })
    .filter((r): r is RadarRow => r !== null);

  return (
    <ChartCard title="Score comparison" filename={`compare-scores-${system}-${year}`}>
      {rows.length === 0 ? (
        <p className="text-muted-foreground py-12 text-center text-sm">
          No {system.toUpperCase()} score data for {year}.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={360}>
          <RadarChart data={rows} margin={{ top: 16, right: 24, bottom: 16, left: 24 }}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
            <PolarRadiusAxis
              domain={[0, 100]}
              tickCount={6}
              tick={false}
              axisLine={false}
            />
            <Tooltip content={<CompareRadarTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              iconType="plainline"
              wrapperStyle={{ fontSize: 14 }}
            />
            {institutions.map((inst, i) => (
              <Radar
                key={inst.ror_id}
                name={inst.name}
                dataKey={inst.ror_id}
                stroke={shades[i]}
                strokeWidth={2}
                strokeDasharray={lineDash(i)}
                fill={shades[i]}
                fillOpacity={0.08}
                isAnimationActive={false}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}

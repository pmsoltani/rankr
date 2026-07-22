import { useState } from "react";
import {
  Bar,
  BarChart,
  LabelList,
  Rectangle,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Slider } from "@/components/ui/slider";
import { RANKING_SYSTEMS, SCORE_ALIASES, type RankingSystemId } from "@/lib/site";
import type { Ranking } from "@/lib/types";

import { ChartCard } from "./ChartCard";

const SYS_ORDER: RankingSystemId[] = ["qs", "shanghai", "the"];

interface ScoreRow {
  label: string;
  system: RankingSystemId;
  systemAlias: string;
  metric: string;
  value: number;
  rounded: number;
  raw: string;
  color: string;
}

function ScoreTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: ScoreRow }[];
}) {
  if (!active || !payload?.length) return null;
  const r = payload[0].payload;
  return (
    <div className="rounded-md border bg-white px-3 py-2 text-xs shadow-sm">
      <div className="flex items-center gap-2">
        <span
          className="inline-block size-2 rounded-full"
          style={{ background: r.color }}
        />
        <span className="font-medium">{r.systemAlias}</span>
      </div>
      <div className="text-muted-foreground mt-0.5">{r.metric}</div>
      <div className="mt-0.5 font-medium tabular-nums">{r.raw}</div>
    </div>
  );
}

// Scores for a selected year as distributed bars (one color per system), 0-100,
// labeled "System: Alias". Year is chosen with a slider; per-bar color uses the
// `shape` prop (Recharts' replacement for the deprecated <Cell>).
export default function ScoreBarChart({
  scores,
  name,
}: {
  scores: Ranking[];
  name: string;
}) {
  const years = [...new Set(scores.map((s) => s.year))].sort((a, b) => a - b);
  const [year, setYear] = useState(years[years.length - 1]);
  if (!years.length) return null;

  const rows: ScoreRow[] = scores
    .filter((s) => s.year === year)
    .map((s): ScoreRow | null => {
      const system = s.ranking_system as RankingSystemId;
      const alias = SCORE_ALIASES[system]?.[s.metric];
      if (!alias) return null;
      const value = s.value === null ? 0 : Number(s.value);
      return {
        label: `${RANKING_SYSTEMS[system].alias}: ${alias}`,
        system,
        systemAlias: RANKING_SYSTEMS[system].alias,
        metric: s.metric,
        value,
        rounded: Math.round(value),
        raw: s.raw_value ?? String(s.value ?? ""),
        color: RANKING_SYSTEMS[system].color,
      };
    })
    .filter((r): r is ScoreRow => r !== null)
    .sort(
      (a, b) =>
        SYS_ORDER.indexOf(a.system) - SYS_ORDER.indexOf(b.system) ||
        Object.keys(SCORE_ALIASES[a.system]).indexOf(a.metric) -
          Object.keys(SCORE_ALIASES[b.system]).indexOf(b.metric),
    );

  return (
    <ChartCard title="Scores" filename={`scores-${name}-${year}`}>
      {rows.length === 0 ? (
        <p className="text-muted-foreground py-12 text-center text-sm">
          No score data for {year}.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={rows} margin={{ top: 24, right: 16, bottom: 4, left: 8 }}>
            <XAxis
              dataKey="label"
              interval={0}
              angle={-35}
              textAnchor="end"
              height={90}
              tick={{ fontSize: 11 }}
              tickLine={false}
            />
            <Tooltip content={<ScoreTooltip />} cursor={{ fill: "rgba(0,0,0,0.04)" }} />
            <Bar
              dataKey="value"
              isAnimationActive={false}
              shape={(props: { payload?: ScoreRow }) => (
                <Rectangle
                  {...props}
                  radius={[4, 4, 0, 0]}
                  fill={props.payload?.color}
                />
              )}
            >
              <LabelList
                dataKey="rounded"
                position="top"
                fontSize={16}
                fill="#525252"
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
      {years.length > 1 && (
        <div className="mx-auto mb-5 max-w-[90%]">
          <Slider
            min={0}
            max={years.length - 1}
            step={1}
            value={[years.indexOf(year)]}
            onValueChange={([i]) => setYear(years[i] ?? year)}
            aria-label="Score year"
          />
          <div className="mt-2 flex justify-between text-[11px] tabular-nums">
            {years.map((y) => (
              <span
                key={y}
                className={
                  y === year ? "text-foreground font-semibold" : "text-muted-foreground"
                }
              >
                {y}
              </span>
            ))}
          </div>
        </div>
      )}
    </ChartCard>
  );
}

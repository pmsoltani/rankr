import {
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { RANKING_SYSTEMS, type RankingSystemId } from "@/lib/site";
import type { Ranking } from "@/lib/types";

import { ChartCard } from "./ChartCard";

const SYSTEMS: RankingSystemId[] = ["qs", "shanghai", "the"];

type RankRow = { year: number; [key: string]: number | string | null };

interface TooltipItem {
  dataKey: string;
  name: string;
  value: number;
  color: string;
  payload: RankRow;
}

function RankTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipItem[];
  label?: string | number;
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
          <span className="text-muted-foreground">{p.name}</span>
          <span className="ml-auto font-medium tabular-nums">
            {String(p.payload[`${p.dataKey}_raw`] ?? p.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

// Rank-over-time: one line per ranking system, Y-axis reversed + hidden so rank 1
// sits on top (mirrors the old ApexCharts config). Tooltip shows the raw rank
// (e.g. "601-800") rather than the numeric value used for plotting.
export default function RankLineChart({
  ranks,
  name,
}: {
  ranks: Ranking[];
  name: string;
}) {
  const byYear = new Map<number, RankRow>();
  for (const r of ranks) {
    const sys = r.ranking_system as RankingSystemId;
    if (!SYSTEMS.includes(sys)) continue;
    let row = byYear.get(r.year);
    if (!row) {
      row = { year: r.year };
      byYear.set(r.year, row);
    }
    row[sys] = r.value === null ? null : Number(r.value);
    row[`${sys}_raw`] = r.raw_value ?? (r.value === null ? null : String(r.value));
  }
  const data = [...byYear.values()].sort((a, b) => a.year - b.year);
  const present = SYSTEMS.filter((s) => ranks.some((r) => r.ranking_system === s));
  if (!data.length || !present.length) return null;

  return (
    <ChartCard title="Rank over time" filename={`ranks-${name}`}>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 24, right: 16, bottom: 8, left: 8 }}>
          <XAxis
            dataKey="year"
            tick={{ fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: "#e5e5e5" }}
            padding={{ left: 16, right: 16 }}
          />
          <YAxis
            reversed
            hide
            domain={["dataMin", "dataMax"]}
            padding={{ top: 12, bottom: 12 }}
          />
          <Tooltip content={<RankTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="plainline"
            wrapperStyle={{ fontSize: 16, fontWeight: 600 }}
          />
          {present.map((s) => (
            <Line
              key={s}
              type="monotone"
              dataKey={s}
              name={RANKING_SYSTEMS[s].alias}
              stroke={RANKING_SYSTEMS[s].color}
              strokeWidth={3}
              dot={{ r: 5 }}
              activeDot={{ r: 5 }}
              connectNulls={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

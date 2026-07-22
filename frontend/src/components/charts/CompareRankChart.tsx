import {
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { lineDash, systemShades } from "@/lib/charts";
import type { RankingSystemId } from "@/lib/site";
import type { InstitutionRankingData } from "@/lib/types";

import { ChartCard } from "./ChartCard";

type Row = { year: number; [key: string]: number | string | null };

interface TooltipItem {
  dataKey: string;
  name: string;
  value: number;
  color: string;
  payload: Row;
}

function CompareRankTooltip({
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
          <span className="text-muted-foreground max-w-44 truncate">{p.name}</span>
          <span className="ml-auto font-medium tabular-nums">
            {String(p.payload[`${p.dataKey}_raw`] ?? p.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

// Rank comparison: one line per institution within a single ranking system.
// Series are distinguished by line style (solid/dashed/dotted) + a shade of the
// system color. Y-axis reversed + hidden so rank 1 is on top.
export function CompareRankChart({
  institutions,
  system,
}: {
  institutions: InstitutionRankingData[];
  system: RankingSystemId;
}) {
  const shades = systemShades(system, institutions.length);
  const byYear = new Map<number, Row>();
  institutions.forEach((inst) => {
    inst.ranks
      .filter((r) => r.ranking_system === system)
      .forEach((r) => {
        let row = byYear.get(r.year);
        if (!row) {
          row = { year: r.year };
          byYear.set(r.year, row);
        }
        row[inst.ror_id] = r.value === null ? null : Number(r.value);
        row[`${inst.ror_id}_raw`] =
          r.raw_value ?? (r.value === null ? null : String(r.value));
      });
  });
  const data = [...byYear.values()].sort((a, b) => a.year - b.year);

  return (
    <ChartCard title="Rank comparison" filename={`compare-ranks-${system}`}>
      {data.length === 0 ? (
        <p className="text-muted-foreground py-12 text-center text-sm">
          No {system.toUpperCase()} rank data for the selected institutions.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={360}>
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
            <Tooltip content={<CompareRankTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              iconType="plainline"
              wrapperStyle={{ fontSize: 14 }}
            />
            {institutions.map((inst, i) => (
              <Line
                key={inst.ror_id}
                type="monotone"
                dataKey={inst.ror_id}
                name={inst.name}
                stroke={shades[i]}
                strokeWidth={2.5}
                strokeDasharray={lineDash(i)}
                dot={{ r: 5, strokeDasharray: "0" }}
                activeDot={{ r: 5, strokeDasharray: "0" }}
                connectNulls={false}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}

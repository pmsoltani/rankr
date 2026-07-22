import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Ranking } from "@/lib/types";

import RankLineChart from "./RankLineChart";
import ScoreBarChart from "./ScoreBarChart";

// Tabbed wrapper for the institution charts (Ranks / Scores). Renders as one
// island so shadcn Tabs can switch between the two Recharts charts.
export default function InstitutionCharts({
  ranks,
  scores,
  name,
}: {
  ranks: Ranking[];
  scores: Ranking[];
  name: string;
}) {
  const hasRanks = ranks.length > 0;
  const hasScores = scores.length > 0;
  if (!hasRanks && !hasScores) return null;

  return (
    <Tabs defaultValue={hasRanks ? "ranks" : "scores"} className="w-full gap-4">
      <TabsList>
        {hasRanks && <TabsTrigger value="ranks">Rank over time</TabsTrigger>}
        {hasScores && <TabsTrigger value="scores">Scores</TabsTrigger>}
      </TabsList>
      {hasRanks && (
        <TabsContent value="ranks">
          <RankLineChart ranks={ranks} name={name} />
        </TabsContent>
      )}
      {hasScores && (
        <TabsContent value="scores">
          <ScoreBarChart scores={scores} name={name} />
        </TabsContent>
      )}
    </Tabs>
  );
}

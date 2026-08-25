import { useEffect, useMemo, useState } from "react";

import type { RankingTableRow } from "@/lib/types";

const PER_PAGE = 50;

interface Props {
  system: string;
  year: number;
  /** Rank-ordered rows for this page, rendered to HTML at build time. */
  rows: RankingTableRow[];
  /** Every country present in this (system, year), for the filter. */
  countries: { country: string; country_code: string }[];
  total: number;
  page: number;
}

const pageHref = (system: string, year: number, page: number) =>
  page <= 1
    ? `/rankings/${system}/${year}`
    : `/rankings/${system}/${year}/${page}`;

/**
 * The ranking table.
 *
 * Astro renders this to static HTML at build time, so the rank list is in the
 * markup for crawlers and for readers without JS, and paging between unfiltered
 * pages is plain links to other prerendered pages.
 *
 * Filtering by country is the one thing that cannot be a static page (53
 * system-years x ~100 countries would be a combinatorial path explosion), so it
 * happens here: the component lazily fetches the full rank list for this
 * (system, year) and takes over rendering.
 */
export default function RankingTable({
  system,
  year,
  rows,
  countries,
  total,
  page,
}: Props) {
  const [country, setCountry] = useState("");
  const [clientPage, setClientPage] = useState(1);
  const [allRows, setAllRows] = useState<RankingTableRow[] | null>(null);
  const [loading, setLoading] = useState(false);

  // Adopt ?country= / ?page= on mount so a shared or reloaded filtered URL land
  // on the right view rather than silently on page 1.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initial = params.get("country") ?? "";
    if (initial) {
      setCountry(initial);
      setClientPage(Math.max(1, Number(params.get("page")) || 1));
    }
  }, []);

  // One fetch per (system, year); cached by the browser as an immutable asset.
  useEffect(() => {
    if (!country || allRows || loading) return;
    setLoading(true);
    fetch(`/data/${system}-${year}.json`)
      .then((r) =>
        r.ok
          ? (r.json() as Promise<{ rows: RankingTableRow[] }>)
          : Promise.reject(new Error(String(r.status))),
      )
      .then((d) => setAllRows(d.rows))
      .catch(() => setAllRows([]))
      .finally(() => setLoading(false));
  }, [country, system, year, allRows, loading]);

  const filtering = country !== "";

  const filtered = useMemo(
    () =>
      filtering && allRows
        ? allRows.filter((r) => r.country === country)
        : null,
    [filtering, allRows, country],
  );

  const shown = filtered
    ? filtered.slice((clientPage - 1) * PER_PAGE, clientPage * PER_PAGE)
    : rows;
  const shownTotal = filtered ? filtered.length : total;
  const currentPage = filtering ? clientPage : page;
  const totalPages = Math.max(1, Math.ceil(shownTotal / PER_PAGE));

  const navigate = (nextCountry: string, nextPage: number) => {
    const params = new URLSearchParams();
    if (nextCountry) params.set("country", nextCountry);
    if (nextPage > 1) params.set("page", String(nextPage));
    const qs = params.toString();
    // Filtered views are client-only, so keep them out of history as distinct
    // documents: replaceState keeps the URL shareable without a navigation.
    window.history.replaceState(
      null,
      "",
      qs ? `?${qs}` : window.location.pathname,
    );
  };

  const onCountry = (next: string) => {
    setCountry(next);
    setClientPage(1);
    navigate(next, 1);
  };

  const goTo = (next: number) => {
    setClientPage(next);
    navigate(country, next);
    window.scrollTo({ top: 0 });
  };

  return (
    <div className="flex flex-col gap-6 lg:flex-row-reverse lg:items-start">
      <aside className="flex shrink-0 flex-col gap-5 lg:w-56">
        <div>
          <h2 className="text-muted-foreground mb-2 text-xs font-semibold uppercase">
            Country
          </h2>
          <select
            value={country}
            onChange={(e) => onCountry(e.target.value)}
            className="w-full rounded-md border bg-white px-2 py-1.5 text-sm"
            aria-label="Filter by country"
          >
            <option value="">All countries</option>
            {countries.map((c) => (
              <option key={c.country} value={c.country}>
                {c.country}
              </option>
            ))}
          </select>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <p className="text-muted-foreground mb-3 text-sm">
          {loading && !filtered
            ? "Loading..."
            : `${shownTotal.toLocaleString()} institutions`}
          {filtering && ` · ${country}`}
        </p>

        <div className="overflow-x-auto rounded-lg border bg-white">
          <table className="w-full text-sm">
            <thead className="bg-neutral-50 text-left">
              <tr>
                <th className="w-28 px-4 py-2 text-center font-medium">Rank</th>
                <th className="w-16 px-4 py-2 font-medium">Country</th>
                <th className="px-4 py-2 font-medium">Institution</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((row) => (
                <tr key={row.ror_id} className="border-t hover:bg-neutral-50">
                  <td className="px-4 py-2 text-center">
                    <span className="inline-block rounded bg-neutral-200 px-2 py-0.5 text-xs font-medium tabular-nums whitespace-nowrap">
                      {row.raw_value ?? row.value ?? ""}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    {row.country_code && (
                      <span
                        className={`fi fi-${row.country_code.toLowerCase()}`}
                        title={row.country ?? ""}
                      />
                    )}
                  </td>
                  <td className="px-4 py-2">
                    <a
                      href={`/i/${row.ror_id}`}
                      className="font-medium text-sky-700 hover:underline"
                    >
                      {row.name}
                    </a>
                  </td>
                </tr>
              ))}
              {shown.length === 0 && !loading && (
                <tr>
                  <td
                    colSpan={3}
                    className="text-muted-foreground px-4 py-8 text-center"
                  >
                    No institutions found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            page {currentPage} of {totalPages}
          </span>
          <div className="flex gap-2">
            {/* Unfiltered paging is real links between prerendered pages; filtered
                paging is client-side, since those views have no static URL. */}
            {currentPage > 1 &&
              (filtering ? (
                <button
                  type="button"
                  onClick={() => goTo(currentPage - 1)}
                  className="rounded-md border px-3 py-1.5 hover:bg-neutral-100"
                >
                  Previous
                </button>
              ) : (
                <a
                  href={pageHref(system, year, currentPage - 1)}
                  className="rounded-md border px-3 py-1.5 hover:bg-neutral-100"
                >
                  Previous
                </a>
              ))}
            {currentPage < totalPages &&
              (filtering ? (
                <button
                  type="button"
                  onClick={() => goTo(currentPage + 1)}
                  className="rounded-md border px-3 py-1.5 hover:bg-neutral-100"
                >
                  Next
                </button>
              ) : (
                <a
                  href={pageHref(system, year, currentPage + 1)}
                  className="rounded-md border px-3 py-1.5 hover:bg-neutral-100"
                >
                  Next
                </a>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

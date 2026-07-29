import { useEffect, useState } from "react";

// Build the Wikipedia REST summary endpoint from a page URL, preserving the
// language subdomain (e.g. de.wikipedia.org). Always https: stored links may
// use http, which the browser blocks as mixed content on the live site.
function summaryApi(url: string): string | null {
  try {
    const u = new URL(url);
    const title = u.pathname.split("/wiki/")[1];
    return title ? `https://${u.host}/api/rest_v1/page/summary/${title}` : null;
  } catch {
    return null;
  }
}

export default function WikiSummary({ url }: { url: string }) {
  const [extract, setExtract] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const api = summaryApi(url);
    if (!api) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    fetch(api)
      .then((r) =>
        r.ok
          ? (r.json() as Promise<{ extract?: string }>)
          : Promise.reject(new Error(String(r.status))),
      )
      .then((data) => {
        if (!cancelled) {
          setExtract(data.extract ?? null);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  if (loading) {
    return (
      <div className="max-w-3xl space-y-2">
        <div className="h-3 w-full animate-pulse rounded bg-neutral-200" />
        <div className="h-3 w-4/5 animate-pulse rounded bg-neutral-200" />
      </div>
    );
  }
  if (!extract) return null;
  return <p className="text-muted-foreground text-m leading-relaxed">{extract}</p>;
}

import {
  QueryClient,
  QueryClientProvider,
  keepPreviousData,
  useQuery,
} from "@tanstack/react-query";
import { SearchIcon } from "lucide-react";
import { useEffect, useState } from "react";

import {
  Command,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import type { SearchResult } from "@/lib/types";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 1 } },
});

/** Debounce a value so the query key only changes once the user pauses. */
function useDebounced<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

async function fetchSearch(q: string): Promise<SearchResult[]> {
  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error(`search failed: ${res.status}`);
  return res.json() as Promise<SearchResult[]>;
}

function SearchInner() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const debounced = useDebounced(query, 300).trim();
  const active = debounced.length >= 2;

  // ⌘K / Ctrl+K toggles the palette.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  // TanStack Query keyed on the debounced query; this alone fixes the old
  // keystroke-lag bug: only the latest key's data is rendered, stale responses
  // are discarded, and keepPreviousData avoids flicker while retyping.
  const { data, isFetching, isError } = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => fetchSearch(debounced),
    enabled: active,
    placeholderData: keepPreviousData,
  });
  const results = active ? (data ?? []) : [];

  const go = (rorId: string) => {
    setOpen(false);
    window.location.href = `/i/${rorId}`;
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="text-muted-foreground flex w-full max-w-sm items-center gap-2 rounded-md border bg-neutral-50 px-3 py-1.5 text-sm transition-colors hover:bg-neutral-100"
        aria-label="Search for institutions"
      >
        <SearchIcon className="size-4 shrink-0" aria-hidden="true" />
        <span className="truncate">Search for institutions…</span>
        <kbd className="ml-auto hidden items-center gap-0.5 rounded border bg-white px-1.5 font-mono text-[10px] sm:inline-flex">
          ⌘K
        </kbd>
      </button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="overflow-hidden p-0" showCloseButton={false}>
          <DialogTitle className="sr-only">Search for institutions</DialogTitle>
          <Command
            shouldFilter={false}
            className="[&_[cmdk-input-wrapper]_svg]:size-5 **:[[cmdk-input]]:h-12 **:[[cmdk-item]]:px-3 **:[[cmdk-item]]:py-2.5"
          >
            <CommandInput
              value={query}
              onValueChange={setQuery}
              placeholder="Search for institutions…"
            />
            <CommandList>
              {!active ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  Type at least 2 characters to search.
                </p>
              ) : isError ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  Something went wrong. Try again.
                </p>
              ) : results.length === 0 && isFetching ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  Searching…
                </p>
              ) : results.length === 0 ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  No institutions found for “{debounced}”.
                </p>
              ) : (
                <CommandGroup heading="Institutions">
                  {results.map((r) => (
                    <CommandItem
                      key={r.ror_id}
                      value={r.ror_id}
                      onSelect={() => go(r.ror_id)}
                      className="gap-3"
                    >
                      {r.country_code ? (
                        <span
                          className={`fi fi-${r.country_code.toLowerCase()} shrink-0`}
                          title={r.country ?? ""}
                        />
                      ) : (
                        <span className="w-[1.33em] shrink-0" />
                      )}
                      <span className="truncate">{r.name}</span>
                      {r.country ? (
                        <span className="text-muted-foreground ml-auto shrink-0 text-xs">
                          {r.country}
                        </span>
                      ) : null}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </DialogContent>
      </Dialog>
    </>
  );
}

export default function SearchCommand() {
  return (
    <QueryClientProvider client={queryClient}>
      <SearchInner />
    </QueryClientProvider>
  );
}

import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { PlusIcon } from "lucide-react";
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

export function ComparePicker({
  onAdd,
  disabled,
  excludeIds,
}: {
  onAdd: (result: SearchResult) => void;
  disabled?: boolean;
  excludeIds: string[];
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const debounced = useDebounced(query, 300).trim();
  const active = debounced.length >= 2;

  const { data, isFetching } = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => fetchSearch(debounced),
    enabled: active,
    placeholderData: keepPreviousData,
  });
  const results = (active ? (data ?? []) : []).filter(
    (r) => !excludeIds.includes(r.ror_id),
  );

  const pick = (r: SearchResult) => {
    onAdd(r);
    setOpen(false);
    setQuery("");
  };

  return (
    <>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 rounded-full border border-dashed px-3 py-1 text-sm font-medium hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-40"
      >
        <PlusIcon className="size-4" />
        Add institution
      </button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="overflow-hidden p-0" showCloseButton={false}>
          <DialogTitle className="sr-only">Add institution to compare</DialogTitle>
          <Command
            shouldFilter={false}
            className="[&_[cmdk-input-wrapper]_svg]:size-5 **:[[cmdk-input]]:h-12 **:[[cmdk-item]]:px-3 **:[[cmdk-item]]:py-2.5"
          >
            <CommandInput
              value={query}
              onValueChange={setQuery}
              placeholder="Search institutions to compare…"
            />
            <CommandList>
              {!active ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  Type at least 2 characters to search.
                </p>
              ) : results.length === 0 && isFetching ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  Searching…
                </p>
              ) : results.length === 0 ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  No institutions found.
                </p>
              ) : (
                <CommandGroup heading="Institutions">
                  {results.map((r) => (
                    <CommandItem
                      key={r.ror_id}
                      value={r.ror_id}
                      onSelect={() => pick(r)}
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

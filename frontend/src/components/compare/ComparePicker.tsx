import { PlusIcon } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  Command,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { type IndexEntry, loadSearchIndex, searchIndex } from "@/lib/search";
import type { SearchResult } from "@/lib/types";

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
  // Matching runs against the locally cached index, so there is nothing to debounce.
  const debounced = query.trim();
  const active = debounced.length >= 2;

  const [index, setIndex] = useState<IndexEntry[] | null>(null);

  // Shared with the navbar palette: whichever opens first pays for the fetch.
  useEffect(() => {
    if (!open || index) return;
    let cancelled = false;
    loadSearchIndex().then(
      (data) => !cancelled && setIndex(data),
      () => {},
    );
    return () => {
      cancelled = true;
    };
  }, [open, index]);

  const isFetching = active && !index;
  const results = useMemo(
    () =>
      active && index
        ? searchIndex(index, debounced).filter(
            (r) => !excludeIds.includes(r.ror_id),
          )
        : [],
    [active, index, debounced, excludeIds],
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
          <DialogTitle className="sr-only">
            Add institution to compare
          </DialogTitle>
          <Command
            shouldFilter={false}
            className="[&_[cmdk-input-wrapper]_svg]:size-5 **:[[cmdk-input]]:h-12 **:[[cmdk-item]]:px-3 **:[[cmdk-item]]:py-2.5"
          >
            <CommandInput
              value={query}
              onValueChange={setQuery}
              placeholder="Search institutions to compare..."
            />
            <CommandList>
              {!active ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  Type at least 2 characters to search.
                </p>
              ) : results.length === 0 && isFetching ? (
                <p className="text-muted-foreground py-6 text-center text-sm">
                  Searching...
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

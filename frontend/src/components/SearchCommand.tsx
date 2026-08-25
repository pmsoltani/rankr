import { SearchIcon } from "lucide-react";
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

export default function SearchCommand() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  // Matching is local, so there is no request to debounce; every keystroke can
  // filter the corpus directly.
  const debounced = query.trim();
  const active = debounced.length >= 2;

  const [index, setIndex] = useState<IndexEntry[] | null>(null);
  const [isError, setIsError] = useState(false);

  // Load the corpus the first time the palette opens, not on page load.
  useEffect(() => {
    if (!open || index) return;
    let cancelled = false;
    loadSearchIndex().then(
      (data) => !cancelled && setIndex(data),
      () => !cancelled && setIsError(true),
    );
    return () => {
      cancelled = true;
    };
  }, [open, index]);

  // Show the platform-correct modifier (⌘ on Mac, Ctrl elsewhere). Defaults to
  // "⌘K" so SSR and first client render match; the effect corrects it after mount.
  const [modKey, setModKey] = useState("⌘K");
  useEffect(() => {
    const isMac = /Mac|iPhone|iPad|iPod/.test(navigator.userAgent);
    if (!isMac) setModKey("Ctrl K");
  }, []);

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

  const isFetching = active && !index && !isError;
  const results = useMemo(
    () => (active && index ? searchIndex(index, debounced) : []),
    [active, index, debounced],
  );

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
        <span className="truncate">Search for institutions...</span>
        <kbd className="ml-auto hidden items-center gap-0.5 rounded border bg-white px-2 py-0.5 font-mono text-xs sm:inline-flex">
          {modKey}
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
              placeholder="Search for institutions..."
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
                  Searching...
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

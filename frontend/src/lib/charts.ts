import { RANKING_SYSTEMS, type RankingSystemId } from "@/lib/site";

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  r /= 255;
  g /= 255;
  b /= 255;
  const mx = Math.max(r, g, b);
  const mn = Math.min(r, g, b);
  const l = (mx + mn) / 2;
  let h = 0;
  let s = 0;
  if (mx !== mn) {
    const d = mx - mn;
    s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
    if (mx === r) h = (g - b) / d + (g < b ? 6 : 0);
    else if (mx === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h /= 6;
  }
  return [h, s, l];
}

function hslToHex(h: number, s: number, l: number): string {
  let r: number;
  let g: number;
  let b: number;
  if (s === 0) {
    r = g = b = l;
  } else {
    const hue = (p: number, q: number, t: number) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue(p, q, h + 1 / 3);
    g = hue(p, q, h);
    b = hue(p, q, h - 1 / 3);
  }
  const to = (x: number) =>
    Math.round(x * 255)
      .toString(16)
      .padStart(2, "0");
  return `#${to(r)}${to(g)}${to(b)}`;
}

/**
 * N shades of a ranking system's color (darkest -> lightest) for compare series.
 * Shades vary by lightness (colorblind-safe); paired with line styles they
 * distinguish up to 3 institutions within a single ranking system. Amber (QS)
 * can't yield 3 well-separated shades on its own, so `lineDash` is the primary
 * differentiator and the shade is a reinforcing cue.
 */
export function systemShades(system: RankingSystemId, n: number): string[] {
  const [h, s] = rgbToHsl(...hexToRgb(RANKING_SYSTEMS[system].color));
  const sat = Math.min(1, Math.max(s, 0.6));
  if (n <= 1) return [hslToHex(h, sat, 0.44)];
  const lo = 0.32;
  const hi = 0.6;
  return Array.from({ length: n }, (_, i) =>
    hslToHex(h, sat, lo + ((hi - lo) * i) / (n - 1)),
  );
}

/** SVG strokeDasharray per series index: solid, dashed, dotted. */
const DASHES = ["0", "7 4", "2 4"];
export function lineDash(i: number): string {
  return DASHES[i % DASHES.length];
}

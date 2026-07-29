import { saveAs } from "file-saver";
import { toPng } from "html-to-image";
import { DownloadIcon } from "lucide-react";
import type { ReactNode } from "react";
import { useRef } from "react";
import watermark from "watermarkjs";

import appLogoSmall from "@/assets/images/appLogoSmall.svg";

/**
 * Card wrapper for a chart: title, optional action (e.g. a year picker), and a
 * PNG download that mirrors the old ApexCharts export; the chart is rasterized
 * with html-to-image, stamped with the logo watermark (lower-left), and saved.
 * If the SVG-logo watermark step fails, the un-watermarked PNG is still saved.
 */
export function ChartCard({
  title,
  filename,
  action,
  children,
}: {
  title: string;
  filename: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  const bodyRef = useRef<HTMLDivElement>(null);

  async function handleDownload() {
    const node = bodyRef.current;
    if (!node) return;
    const dataUrl = await toPng(node, { backgroundColor: "#ffffff", pixelRatio: 2 });
    try {
      const img = await watermark([dataUrl, appLogoSmall.src]).image(
        watermark.image.lowerLeft(0.5),
      );
      saveAs(img.src, `${filename}.png`);
    } catch {
      saveAs(dataUrl, `${filename}.png`);
    }
  }

  return (
    <div className="rounded-lg border bg-white">
      <div className="flex items-center justify-between gap-2 border-b px-4 py-2.5">
        <h3 className="text-sm font-semibold">{title}</h3>
        <div className="flex items-center gap-2">
          {action}
          <button
            type="button"
            onClick={handleDownload}
            title="Download PNG"
            aria-label="Download chart as PNG"
            className="text-muted-foreground hover:text-foreground rounded p-1 hover:bg-neutral-100"
          >
            <DownloadIcon className="size-4" />
          </button>
        </div>
      </div>
      <div ref={bodyRef} className="bg-white p-4">
        {children}
      </div>
    </div>
  );
}

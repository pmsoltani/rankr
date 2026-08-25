// @ts-check
import { readFileSync } from "node:fs";

import cloudflare from "@astrojs/cloudflare";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";

// Written by `bun run build:data`, which every build/dev script runs first.
/** @type {Record<string, number[]>} */
const systems = JSON.parse(readFileSync("./.data/systems.json", "utf8"));

const redirects = Object.fromEntries(
  Object.entries(systems).map(([system, years]) => [
    `/rankings/${system}`,
    `/rankings/${system}/${years[0]}`,
  ]),
);

// https://astro.build/config
export default defineConfig({
  output: "server",
  trailingSlash: "never",
  adapter: cloudflare({ prerenderEnvironment: "node" }),
  integrations: [react()],
  redirects,
  vite: {
    plugins: [tailwindcss()],
  },
});

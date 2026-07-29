// @ts-check
import cloudflare from "@astrojs/cloudflare";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";

// https://astro.build/config
export default defineConfig({
  // SSR on Cloudflare (Worker with static assets);
  // static pages opt in per-route with `prerender`.
  // Bindings (D1, etc.) come from `wrangler.jsonc`; workerd loads them in
  // `astro dev` and at the edge.
  output: "server",
  adapter: cloudflare(),
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()],
  },
});

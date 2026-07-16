// @ts-check
import cloudflare from "@astrojs/cloudflare";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";

// https://astro.build/config
export default defineConfig({
  // SSR on Cloudflare Pages; static pages opt in per-route with `prerender`.
  output: "server",
  adapter: cloudflare({
    platformProxy: { enabled: true }, // local D1/bindings during `astro dev`
  }),
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()],
  },
});

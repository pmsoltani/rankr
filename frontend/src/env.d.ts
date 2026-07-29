/// <reference types="astro/client" />

// Cloudflare bindings are accessed via `import { env } from "cloudflare:workers"`.
declare namespace Cloudflare {
  interface Env {
    DB: import("@cloudflare/workers-types").D1Database;
  }
}

// watermarkjs ships no type declarations.
declare module "watermarkjs";

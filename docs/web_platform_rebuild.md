# Web platform rebuild

This branch replaces the Streamlit runtime with a client-side React and
TypeScript application built by Vite.

## Architecture

- React renders the application and keeps profile state in browser storage.
- The scoring model V2 is implemented in `web/scoring.ts`.
- Personalized interpretation is implemented in `web/analysis.ts`.
- The reference dataset is imported from the existing verified CSV.
- The visualization and its 500 reference profiles are split into lazy-loaded
  production chunks. They are not downloaded on the input or analysis views.
- No application server, database, account, or cloud storage is required.

The existing Python application remains in the branch temporarily as a
reference implementation and regression oracle. It is not part of the Vite
production bundle.

## Local development

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite.

## Verification

```powershell
npm test
npm run build
python -m pytest
npm audit
```

## Vercel

The root `vercel.json` declares the Vite build:

- build command: `npm run build`
- output directory: `dist`
- SPA fallback: `index.html`

Import the repository in Vercel and select this branch. No environment
variables are required.

## Cloudflare Pages

The root `wrangler.toml` declares `dist` as the Pages output directory.

Cloudflare Pages project settings:

- build command: `npm run build`
- build output directory: `dist`
- Node.js version: a version supported by the current Vite release

No Workers binding or environment variable is required.

## Current scope

Implemented:

- bilingual profile input;
- multiple locally persisted profiles;
- JSON import and export;
- scoring model V2 projection;
- lazy-loaded political map;
- multi-value reference filters using `role_category`;
- detailed personalized interpretation;
- profile comparison;
- methodology page;
- responsive layout;
- Vercel and Cloudflare Pages configuration.

The Streamlit and desktop entry points are retained during migration. Removing
them should happen only after the web application has been accepted in browser
testing and the repository documentation tests have been migrated deliberately.

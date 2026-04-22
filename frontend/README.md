# `frontend/` — the website

This folder contains the **web page** the user sees. It is a Next.js
(React) application. Everything inside `frontend/` is just the user
interface — it has no ability to predict prices or read the dataset on
its own. It talks over the network to the backend services in the
`backend/` folder to get its answers.

## What it does

The website has two pages:

- **`/estimator`** — a form where the user types in a property's details
  and sees a predicted price. Past submissions appear in a history
  table below the form.
- **`/market`** — a dashboard showing charts and a table summarising the
  training dataset, plus a *what-if* panel for trying a prediction
  against any dataset row, plus CSV and PDF download buttons.

## How it combines with the rest of the project

```
Browser ──► frontend (this folder, port 3000)
                │
                ├──► backend/estimator-api (port 8001)  for predictions + history
                └──► backend/market-api    (port 8002)  for charts, table, exports
```

The frontend never talks to `ml-api` directly; the two backend services
do that on its behalf.

## How to run just the website (for UI work)

You only need this if you want to change the look of the site. To just
*use* the site, run the whole stack from the repo root with
`docker compose up --build` and open <http://localhost:3000>.

You need **Node.js 24** (install via
[nvm](https://github.com/nvm-sh/nvm)). Then from this folder:

```bash
npm install
npm run dev          # starts on http://localhost:3000
```

The dev server expects the backend services to be running at
`http://localhost:8001` (estimator) and `http://localhost:8002`
(market). The easiest way is to leave `docker compose up` running for
the backends and only replace the `portal` container with this dev
server.

## Useful commands

| Command              | What it does                                      |
|----------------------|---------------------------------------------------|
| `npm install`        | Downloads the libraries it depends on.            |
| `npm run dev`        | Runs the site in development mode with hot reload.|
| `npm run build`      | Produces an optimised production build.           |
| `npx tsc --noEmit`   | Type-checks the TypeScript code without building. |

## Environment variables

The website reads two URLs from the environment at startup:

- `NEXT_PUBLIC_ESTIMATOR_API_URL` — where the estimator API lives
  (default `http://localhost:8001`).
- `NEXT_PUBLIC_MARKET_API_URL` — where the market API lives
  (default `http://localhost:8002`).

These are rendered into the browser bundle, so they must be URLs the
user's browser can reach (not Docker internal names).

A reference copy of these and all other settings lives in `keys/` at
the repo root.

## Folder map inside `frontend/`

- `app/` — the Next.js pages (`/`, `/estimator`, `/market`).
- `components/` — reusable UI building blocks (forms, cards, tables).
- `lib/` — helpers: API clients, number formatting, validation schemas.
- `public/` — static assets.
- `Dockerfile` — how the website is packaged for production.

## Libraries worth naming

- **Next.js 16 (App Router)** — the web framework.
- **Tailwind CSS v4** — the styling system (CSS-first, no JS config).
- **React Hook Form + Zod** — form handling and validation.
- **Lucide** — icon set.

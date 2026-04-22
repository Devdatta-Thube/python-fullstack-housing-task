# Housing Price — Fullstack Application

This project predicts house prices from a small set of features (size,
bedrooms, year built, etc.) and shows the results in a website. It is the
submission for the EY Python Fullstack interview task.

If you are new to the project, start here — this page is written to be
readable without a software background.

---

## What you get

- A **website** to type in a property's details and see a predicted price.
- A **dashboard** with charts and tables that summarise the training data
  and let you export the dataset as a CSV or a PDF report.
- Three **backend services** that do the actual work: training the model,
  storing submission history, and computing statistics.

Everything runs together with one command. You do not need to install
Python or Node; only Docker Desktop.

---

## What is in each folder

| Folder          | What it holds                                                    | Read its README to …                        |
|-----------------|------------------------------------------------------------------|---------------------------------------------|
| `frontend/`     | The website — the part you see in a browser.                     | Run the website on its own.                 |
| `backend/`      | The three services that power the website (ml-api, estimator-api, market-api). | Run the APIs on their own.                  |
| `docker-images/`| Pre-built Docker image(s) so you can run the ML API without rebuilding it from source. | Load and run the shipped image.             |
| `keys/`         | Environment variables / configuration the services read at startup. (No real secrets are in this repo — see the note inside.) | Understand which settings exist and how to change them. |

Also at the repo root:

- `docker-compose.yml` — the single file that wires all four services together.
- `README.md` — this page.
- `DATA.md` — where to put the housing dataset (not shipped for
  confidentiality reasons).

---

## Run everything in one go

### 1. Install Docker Desktop

Download from <https://www.docker.com/products/docker-desktop/> and start it.
Wait until its status bar says "Docker Desktop is running".

### 2. Put the dataset in place

The dataset is not in this repository — it belongs to the task issuer.
See **[DATA.md](DATA.md)** for exactly where to copy it (two places,
one command).

### 3. From the repository root, run

```bash
docker compose up --build -d
```

The first run takes 3–5 minutes (Docker downloads base images and trains
the model). Later runs take ~10 seconds.

### 4. Check everything is up

```bash
docker compose ps
```

All four rows should say **healthy** in the STATUS column. If any say
`unhealthy`, wait another 30 seconds and re-check — the website takes
longest to warm up.

### 5. Open the app

| Page                        | URL                                  | What you do there                            |
|-----------------------------|--------------------------------------|----------------------------------------------|
| Home                        | <http://localhost:3000>              | Pick either tool.                            |
| Estimator                   | <http://localhost:3000/estimator>    | Type property details → see predicted price. |
| Market dashboard            | <http://localhost:3000/market>       | Charts, table, exports, what-if analysis.    |
| Swagger (API explorer)      | <http://localhost:8000/docs>         | Try the ML API directly.                     |

### 6. Stop everything

```bash
docker compose down
```

---

## What you will see when it works

- **Estimator page:** a form with fields like *Square footage*, *Bedrooms*,
  *Year built*, etc. Hit **Predict** and a price in rupees appears below
  the form. Past predictions appear in a history table.
- **Market page:** the top of the page shows four cards (Total
  properties, Median price, Mean price, Price range). Below that is a
  histogram of the price distribution, then a dataset table with sort
  and filter controls, and buttons to download the data as CSV or PDF.
- **All prices are shown in Indian rupees** (₹) with
  lakh/crore grouping.

---

## Glossary (plain English)

- **API** — a piece of software that answers questions over the network.
  Here it answers "given these property details, what is the price?".
- **Service** — one running piece of the system. This project has four:
  the ML API, two helper APIs, and the website.
- **Docker** — a tool that packages a service and everything it needs to
  run into a single file (an *image*) so you don't have to install Python,
  Node, etc. yourself.
- **Docker Compose** — the tool that runs several Docker services
  together with one command.
- **Model** — the trained mathematical formula that maps property
  details to a price. Trained once when `docker compose up --build`
  builds the ML API.

---

## Trouble running it?

1. Is Docker Desktop running? (Its icon must be solid in the system tray.)
2. Did you place the CSV file in both paths listed in
   [DATA.md](DATA.md)? The build will stop partway with a clear error
   if not.
3. Are ports 3000, 8000, 8001, or 8002 already in use on your machine?
   Stop whatever is using them, or edit `docker-compose.yml` to use
   different host ports (left side of `"3000:3000"` etc.).
4. Running on Windows? Use **Windows PowerShell** or **WSL Ubuntu**.
   The commands above work in both.

If it still won't start, `docker compose logs --tail=50` prints the most
recent output from all services — paste that when asking for help.

---

## For reviewers with a technical background

- Architecture, design choices, and per-service details are documented
  inside `backend/README.md`, `frontend/README.md`, and each service's
  own `README.md`.
- `DATA.md` covers dataset schema, ingestion path, and how to swap in
  a different CSV.
- All four services share one Docker network; inter-service calls use
  Docker DNS (`http://ml-api:8000`), browser-facing URLs use
  `http://localhost:800X`.

## License

Interview deliverable; not licensed for redistribution.

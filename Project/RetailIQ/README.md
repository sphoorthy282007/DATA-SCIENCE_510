# RetailIQ

## Full-Cycle E-Commerce Customer & Sales Analytics

RetailIQ is an end-to-end e-commerce analytics project built using Python, Pandas, Scikit-learn, Matplotlib, Seaborn, and Streamlit.

The project analyzes online retail transaction data to understand sales performance, customer behavior, product performance, customer segmentation, and future revenue trends.

---

## Project Objectives

The main objectives of RetailIQ are:

- Clean and prepare raw retail transaction data
- Analyze sales and revenue trends
- Understand customer purchasing behavior
- Perform RFM (Recency, Frequency, Monetary) analysis
- Segment customers into meaningful groups
- Identify top-performing products
- Analyze sales across countries
- Forecast future revenue
- Build an interactive business dashboard

---

## Dataset

The project uses the Online Retail dataset containing e-commerce transactions.

The raw dataset is stored in:

```text
data/raw/Online Retail.xlsx
```

---

## Interactive Dashboard

The dashboard (`dashboard/app.py`) is a redesigned, multi-page Streamlit app styled as a
modern admin/analytics panel:

- **Sidebar** — drag-and-drop dataset upload, page navigation, plus live
  filters (date range, country) that recompute every KPI, chart, and table
  on the page.
- **Dashboard (Overview)** — KPI cards with month-over-month growth badges, a
  revenue trend chart, an adjustable "Sales Target" progress ring, a Top
  Selling Products strip, and a Customer Segments breakdown.
- **Sales Analytics** — monthly revenue trend, orders by day of week, and
  sales by hour of day.
- **Customers** — customer KPIs, RFM table, and an interactive segment
  breakdown (Champions / Loyal / At Risk / Lost / etc.).
- **Products & Countries** — a product gallery with keyword-inferred icons,
  plus top products and country performance tables/charts.
- **Forecast** — historical vs. predicted revenue and an adjustable-horizon
  linear forecast (1–6 months ahead).
- **Assistant** — a built-in chatbot that answers questions about the
  currently loaded/filtered data ("top 5 products", "revenue in Germany",
  "customer segments"...). Rule-based, so it needs no API key and has no
  running cost — see `src/chatbot.py` for how to swap in a real LLM later.

Run it with:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

### Drag-and-drop any compatible dataset

The sidebar file uploader accepts `.csv`/`.xlsx`. Drop in the UCI
**Online Retail** file, the newer **Online Retail II** file (different
column names: `Invoice`, `Price`, `Customer ID`), or any similarly-shaped
transactional export — `src/data_cleaning.py` normalizes whichever column
names it finds (see `COLUMN_ALIASES`) and runs the full cleaning +
analytics pipeline automatically. Leave it empty to use the bundled
sample dataset. Larger files (Online Retail II is ~1M rows) take a few
seconds longer on first load; results are cached after that.

### Product icons

The dataset has no real product photos — only text descriptions like
"WHITE HANGING HEART T-LIGHT HOLDER". `src/product_icons.py` maps
keywords in each description to a representative emoji so products are
easier to scan visually, without fabricating images that don't exist in
the source data.

### Currency by country

Money values (KPIs, charts, forecasts, the Assistant's answers) switch
to the local currency of whichever country is selected in the sidebar
filter — e.g. filtering to "Germany" shows amounts in €, "India" in ₹.
Selecting no country, or more than one, falls back to the base currency
(GBP), since a single currency can't represent a multi-country view.
Exchange rates in `src/currency.py` are fixed and indicative (for
presentation only, not live FX data).

### AI-powered Assistant mode (optional)

The Assistant page's rule-based chatbot needs no setup and answers a
fixed set of question types (top products, revenue by country, best
month, segments, win-back tips, etc.). Turning on **AI Mode** in that
page lets it answer open-ended business questions instead, using the
free Google Gemini API:

1. Get a free API key (no credit card) at https://aistudio.google.com
2. Copy `.env.example` to `.env` and paste your key into it
3. Restart the app — AI Mode will detect the key automatically

Without a key configured, AI Mode shows a text box to paste one in for
that session only (never written to disk). The rule-based chatbot keeps
working regardless of whether AI Mode is set up.

### Running with Docker

As an alternative to the `pip install` + `streamlit run` steps above,
this also runs in a container — same app, either way:

```bash
docker compose up --build
```

Then open http://localhost:8501. To enable AI Mode inside Docker, put
your Gemini key in a `.env` file in the project root (same file as
above) — `docker-compose.yml` passes it through automatically.

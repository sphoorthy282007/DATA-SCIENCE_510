"""
RetailIQ - Analytics Assistant

A lightweight, rule-based Q&A engine that answers natural-language
questions about the currently loaded/filtered dataset using the same
aggregates the dashboard already computes (RFM, product performance,
country performance, monthly sales). It needs no external API key and
has no per-query cost, so it works out of the box for a portfolio/
academic submission.

If you have an OpenAI or Anthropic API key, you can swap `answer()`'s
fallback branch for a real LLM call and pass this module's summary
dict in as context - see the note at the bottom of this file.
"""

import re

import pandas as pd

from src.retention import get_recommendations, get_segment_summary


_CURRENCY_SYMBOL = "£"


def set_currency(symbol: str) -> None:
    """Set the currency symbol used by every money-formatted chatbot answer."""
    global _CURRENCY_SYMBOL
    _CURRENCY_SYMBOL = symbol


def _fmt_money(x):
    return f"{_CURRENCY_SYMBOL}{x:,.0f}"


def _find_country(question, countries):
    q = question.lower()
    for c in sorted(countries, key=len, reverse=True):
        if c.lower() in q:
            return c
    return None


def _find_number(question, default=5):
    match = re.search(r"\b(\d{1,3})\b", question)
    if match:
        return max(1, min(50, int(match.group(1))))
    return default


def build_context(df, rfm, product_perf, country_perf, monthly_sales):
    """Bundle everything the assistant is allowed to answer from."""
    return {
        "df": df,
        "rfm": rfm,
        "product_perf": product_perf,
        "country_perf": country_perf,
        "monthly_sales": monthly_sales,
    }


def answer(question, context):
    """Return a plain-text answer to `question` using `context`."""

    df = context["df"]
    rfm = context["rfm"]
    product_perf = context["product_perf"]
    country_perf = context["country_perf"]
    monthly_sales = context["monthly_sales"]

    q = question.lower().strip()

    if not q:
        return "Ask me something like “top 5 products” or “revenue in Germany”."

    # ---- Top products ----
    if "top" in q and "product" in q:
        n = _find_number(q, 5)
        top = product_perf.head(n)
        lines = [
            f"{i+1}. {row.Description or row.StockCode} — "
            f"{_fmt_money(row.Revenue)} ({int(row.Quantity):,} units)"
            for i, row in enumerate(top.itertuples())
        ]
        return f"Top {n} products by revenue:\n" + "\n".join(lines)

    # ---- Country revenue ----
    country = _find_country(q, country_perf["Country"].unique())
    if country and ("revenue" in q or "sales" in q or "country" in q or "how much" in q):
        row = country_perf[country_perf["Country"] == country].iloc[0]
        return (
            f"{country}: {_fmt_money(row.Revenue)} revenue, "
            f"{int(row.Orders):,} orders, {int(row.Customers):,} customers."
        )

    # ---- Top countries ----
    if "top" in q and "countr" in q:
        n = _find_number(q, 5)
        top = country_perf.head(n)
        lines = [
            f"{i+1}. {row.Country} — {_fmt_money(row.Revenue)}"
            for i, row in enumerate(top.itertuples())
        ]
        return f"Top {n} countries by revenue:\n" + "\n".join(lines)

    # ---- Best / worst month ----
    if ("best" in q or "highest" in q) and "month" in q:
        best = monthly_sales.loc[monthly_sales["Revenue"].idxmax()]
        return f"Best month: {best.Month.strftime('%B %Y')} with {_fmt_money(best.Revenue)} revenue."

    if ("worst" in q or "lowest" in q) and "month" in q:
        worst = monthly_sales.loc[monthly_sales["Revenue"].idxmin()]
        return f"Lowest month: {worst.Month.strftime('%B %Y')} with {_fmt_money(worst.Revenue)} revenue."

    # ---- Win-back / retention advice (checked before generic segment counts,
    # since phrases like "at risk" would otherwise match that branch first) ----
    if any(w in q for w in ["win back", "win-back", "winback", "retention", "retain", "recommend",
                             "come back", "recover", "re-engage", "reengage", "suggest", "tip"]):
        segment = None
        if "lost" in q:
            segment = "Lost Customers"
        elif "at risk" in q or "risk" in q:
            segment = "At Risk"
        elif "champion" in q:
            segment = "Champions"
        elif "loyal" in q:
            segment = "Loyal Customers"
        elif "new" in q:
            segment = "New Customers"
        elif "regular" in q:
            segment = "Regular Customers"
        else:
            segment = "At Risk" if "At Risk" in rfm["Segment"].unique() else "Lost Customers"

        summary = get_segment_summary(rfm, segment)
        rec = get_recommendations(segment)
        lines = [f"- {t}" for t in rec["tips"]]
        return (
            f"{segment} ({summary['count']:,} customers, "
            f"{_fmt_money(summary['total_monetary'])} in historical revenue):\n"
            f"{rec['headline']}\n" + "\n".join(lines)
        )

    # ---- Customer segments ----
    if "segment" in q or "champion" in q or "at risk" in q or "loyal" in q:
        counts = rfm["Segment"].value_counts()
        lines = [f"- {seg}: {cnt:,} customers" for seg, cnt in counts.items()]
        return "Customer segments:\n" + "\n".join(lines)

    # ---- Totals / overview ----
    if any(w in q for w in ["total revenue", "how much revenue", "overall revenue"]):
        return f"Total revenue: {_fmt_money(df['Revenue'].sum())}"

    if "total order" in q or "how many order" in q:
        return f"Total orders: {df['InvoiceNo'].nunique():,}"

    if "total customer" in q or "how many customer" in q:
        return f"Total customers: {df['CustomerID'].nunique():,}"

    if "average order" in q or "aov" in q:
        revenue = df["Revenue"].sum()
        orders = df["InvoiceNo"].nunique()
        aov = revenue / orders if orders else 0
        return f"Average order value: {_fmt_money(aov)}"

    if "product" in q and ("how many" in q or "count" in q or "number of" in q):
        return f"Distinct products in the current selection: {df['StockCode'].nunique():,}"

    if "countr" in q and ("how many" in q or "count" in q or "number of" in q):
        return f"Distinct countries in the current selection: {df['Country'].nunique():,}"

    # ---- Fallback ----
    return (
        "I can answer questions about: top products, top countries, revenue "
        "for a specific country, best/worst month, customer segments, "
        "win-back tips for At Risk/Lost customers, total revenue/orders/"
        "customers, and average order value. Try something like “top 5 "
        "products” or “how do I win back lost customers”."
    )


# ------------------------------------------------------------------
# Optional: swap in a real LLM
# ------------------------------------------------------------------
# If you want free-form answers instead of the rule-based ones above,
# set an API key as an environment variable and replace the fallback
# branch in answer() with something like:
#
#   import os, anthropic
#   client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
#   summary = {
#       "total_revenue": float(df["Revenue"].sum()),
#       "top_products": product_perf.head(10).to_dict("records"),
#       "top_countries": country_perf.head(10).to_dict("records"),
#   }
#   response = client.messages.create(
#       model="claude-sonnet-4-6",
#       max_tokens=300,
#       messages=[{"role": "user", "content": f"Data: {summary}\n\nQuestion: {question}"}],
#   )
#
# This keeps the app free to run by default, with a documented upgrade path.

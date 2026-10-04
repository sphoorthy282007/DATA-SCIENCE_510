"""
RetailIQ - AI Assistant Module (optional, Gemini-powered)

This is entirely optional and additive: if no API key is configured, the
rest of the app works exactly as before with the free rule-based chatbot
in src/chatbot.py. When a Gemini API key IS available, this module lets
the Assistant page answer genuinely open-ended business questions instead
of only the fixed set of rule-based intents.

Design choice: rather than having the LLM write and execute arbitrary
pandas code against the raw dataframe (a text-to-pandas agent), we give
it a compact, pre-computed summary of the current dataset - top products,
country performance, monthly trend, RFM segments - and let it reason and
write a natural-language answer over that summary. This is simpler, safer
(no code execution), and still covers the vast majority of the business
questions someone would actually ask about their data.
"""

import os

try:
    from google import genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False


def is_library_installed() -> bool:
    return _GENAI_AVAILABLE


def get_api_key(session_key: str = None) -> str:
    """
    Look for a Gemini API key, in priority order:
    1. A key explicitly passed in (e.g. from a Streamlit session_state input)
    2. The GEMINI_API_KEY environment variable (e.g. from a local .env / Docker)
    """
    if session_key:
        return session_key
    return os.environ.get("GEMINI_API_KEY", "")


def build_ai_context(df, rfm, product_perf, country_perf, monthly_sales, currency_symbol="£") -> str:
    """Compact text summary of the currently loaded/filtered dataset."""

    def money(x):
        return f"{currency_symbol}{x:,.0f}"

    lines = []
    lines.append(f"Date range: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}")
    lines.append(f"Total revenue: {money(df['Revenue'].sum())}")
    lines.append(f"Total orders: {df['InvoiceNo'].nunique():,}")
    lines.append(f"Total customers: {df['CustomerID'].nunique():,}")
    lines.append(f"Total unique products (SKUs): {df['StockCode'].nunique():,}")

    lines.append("\nTop 15 products by revenue:")
    for row in product_perf.head(15).itertuples():
        lines.append(f"- {row.Description}: {money(row.Revenue)}, {int(row.Quantity):,} units")

    lines.append("\nRevenue by country (top 10):")
    for row in country_perf.head(10).itertuples():
        lines.append(f"- {row.Country}: {money(row.Revenue)}")

    lines.append("\nMonthly revenue trend:")
    for row in monthly_sales.itertuples():
        lines.append(f"- {row.Month.strftime('%B %Y')}: {money(row.Revenue)}")

    lines.append("\nCustomer segments (RFM-based):")
    seg_counts = rfm["Segment"].value_counts()
    seg_monetary = rfm.groupby("Segment")["Monetary"].sum()
    for seg, cnt in seg_counts.items():
        lines.append(f"- {seg}: {cnt:,} customers, {money(seg_monetary.get(seg, 0))} historical revenue")

    return "\n".join(lines)


SYSTEM_INSTRUCTION = """You are RetailIQ's AI business analyst. You answer questions about a
retailer's e-commerce transaction data, using ONLY the data summary provided below - do not
invent numbers that aren't in it. If a question needs a number that isn't in the summary, say
so plainly rather than guessing.

Give clear, concise, business-relevant answers. Where relevant, add 1-3 concrete, actionable
suggestions a retail business owner could act on (a tip, a recommendation, a risk to watch).
Keep answers focused - a few sentences or a short list, not an essay. Use the currency symbol
already shown in the data summary; don't convert it."""


# "gemini-flash-latest" is an alias Google hot-swaps to whatever their current
# recommended flash model is - using it (rather than a pinned version like
# "gemini-2.5-flash") avoids this code going stale every time Google retires
# a specific model version. A pinned version is kept as a second attempt in
# case the alias itself is ever briefly unavailable.
DEFAULT_MODEL = "gemini-flash-latest"
FALLBACK_MODEL = "gemini-3.8-flash"


def ask_ai(api_key: str, question: str, data_context: str, chat_history=None, model: str = DEFAULT_MODEL):
    """
    Ask the Gemini API a question grounded in the given data context.

    Returns (answer_text, error_text). Exactly one of the two is None.
    Tries `model` first, then FALLBACK_MODEL once if that specific model
    name is unavailable (e.g. retired/renamed on Google's side).
    """
    if not _GENAI_AVAILABLE:
        return None, (
            "The `google-genai` package isn't installed. Run "
            "`pip install google-genai` and restart the app to enable AI mode."
        )
    if not api_key:
        return None, "No Gemini API key configured. Add one in the sidebar or set GEMINI_API_KEY."

    history_text = ""
    if chat_history:
        # Keep only the last few turns so the prompt stays small/cheap.
        recent = chat_history[-6:]
        history_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in recent)

    prompt = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"=== DATA SUMMARY ===\n{data_context}\n\n"
        f"=== RECENT CONVERSATION ===\n{history_text}\n\n"
        f"=== QUESTION ===\n{question}"
    )

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:  # noqa: BLE001
        return None, f"Couldn't connect to the Gemini API: {e}"

    last_error = None
    for attempt_model in [model, FALLBACK_MODEL] if model != FALLBACK_MODEL else [model]:
        try:
            response = client.models.generate_content(model=attempt_model, contents=prompt)
            text = getattr(response, "text", None)
            if not text:
                last_error = "The AI returned an empty response. Try rephrasing the question."
                continue
            return text.strip(), None
        except Exception as e:  # noqa: BLE001 - surface the error, try the fallback model next
            last_error = str(e)
            continue

    return None, f"AI request failed: {last_error}"

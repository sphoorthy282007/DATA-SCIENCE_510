import io
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads GEMINI_API_KEY from a local .env file, if present
except ImportError:
    pass  # python-dotenv not installed - GEMINI_API_KEY can still be set as a real env var

# ============================================================
# PROJECT PATH
# ============================================================

# Project root (so `src.*` imports keep working, same as before)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

# This file's own folder (so the sibling `theme.py` is importable
# no matter what directory `streamlit run` is launched from)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from theme import (  # noqa: E402
    CUSTOM_CSS,
    kpi_card,
    product_card,
    progress_row,
    section_header,
)

# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from src.ai_assistant import ask_ai  # noqa: E402
from src.ai_assistant import build_ai_context as ai_build_context  # noqa: E402
from src.ai_assistant import get_api_key as ai_get_key  # noqa: E402
from src.ai_assistant import is_library_installed as ai_is_installed  # noqa: E402
from src.chatbot import answer as chatbot_answer  # noqa: E402
from src.chatbot import build_context as chatbot_context  # noqa: E402
from src.chatbot import set_currency as chatbot_set_currency  # noqa: E402
from src.customer_analysis import calculate_customer_kpis, calculate_rfm  # noqa: E402
from src.data_cleaning import clean_data, load_data as load_raw_data  # noqa: E402
from src.feature_engineering import create_date_features, create_revenue  # noqa: E402
from src.forecasting import (  # noqa: E402
    create_monthly_sales,
    forecast_future,
    train_forecasting_model,
)
from src.product_analysis import (  # noqa: E402
    calculate_country_performance,
    calculate_product_performance,
)
from src.currency import get_currency_for_countries  # noqa: E402
from src.product_icons import get_icon_for_description  # noqa: E402
from src.product_images import get_image_b64_for_description  # noqa: E402
from src.retention import get_recommendations, get_segment_summary  # noqa: E402
from src.segmentation import assign_customer_segments, calculate_rfm_scores  # noqa: E402

ACCENT = "#10B981"

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RetailIQ | Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# DATA SOURCE — drag & drop uploader (top of sidebar, rendered
# before anything that depends on the data)
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">
            <div style="width:34px;height:34px;border-radius:9px;
                        background:{ACCENT};display:flex;align-items:center;
                        justify-content:center;color:white;font-weight:700;">R</div>
            <div>
                <div style="font-weight:700;font-size:16px;line-height:1.1;">RetailIQ</div>
                <div style="font-size:11px;color:#6B7280;">Retail Analytics Suite</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Data source**")
    uploaded_file = st.file_uploader(
        "Drag and drop a dataset",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
        help=(
            "Drop the UCI 'Online Retail' or 'Online Retail II' file "
            "(.csv/.xlsx), or any similarly-shaped transactional export. "
            "The app runs the full cleaning + analytics pipeline on it "
            "automatically. Leave empty to use the bundled sample dataset."
        ),
    )
    st.caption("📁 Drop a file to run the pipeline on your own data, or leave empty for the bundled sample.")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(show_spinner="Running cleaning + analytics pipeline on the uploaded file…")
def load_data(uploaded_bytes=None, uploaded_name=None):
    if uploaded_bytes is not None:
        raw = load_raw_data(io.BytesIO(uploaded_bytes), filename=uploaded_name)
        df = clean_data(raw)
    else:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "processed", "clean_sales_data.csv"
        )
        df = pd.read_csv(file_path)

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    if "Revenue" not in df.columns:
        df = create_revenue(df)

    df = create_date_features(df)
    df["MonthPeriod"] = df["InvoiceDate"].dt.to_period("M")
    df["MonthLabel"] = df["InvoiceDate"].dt.strftime("%b %Y")

    return df


data_source_label = "Bundled sample dataset"
if uploaded_file is not None:
    try:
        df_full = load_data(uploaded_file.getvalue(), uploaded_file.name)
        if df_full.empty:
            raise ValueError(
                "After cleaning, this file had no usable rows left "
                "(check it has valid CustomerID, positive Quantity and Price)."
            )
        data_source_label = uploaded_file.name
    except ValueError as e:
        st.sidebar.error(f"⚠️ {e}")
        st.sidebar.caption("Falling back to the bundled sample dataset.")
        df_full = load_data()
else:
    df_full = load_data()

MIN_DATE = df_full["InvoiceDate"].min().date()
MAX_DATE = df_full["InvoiceDate"].max().date()
ALL_COUNTRIES = sorted(df_full["Country"].dropna().unique().tolist())


# ============================================================
# SIDEBAR — BRANDING, NAVIGATION & FILTERS
# ============================================================

with st.sidebar:
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠  Dashboard",
            "📈  Sales Analytics",
            "👥  Customers",
            "📦  Products & Countries",
            "🔮  Forecast",
            "🤖  Assistant",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Filters**")

    date_range = st.date_input(
        "Date range",
        value=(MIN_DATE, MAX_DATE),
        min_value=MIN_DATE,
        max_value=MAX_DATE,
    )

    selected_countries = st.multiselect(
        "Country",
        options=ALL_COUNTRIES,
        default=[],
        placeholder="All countries",
    )

    st.markdown("---")
    st.caption(f"Source: {data_source_label}")
    st.caption(f"Dataset rows: {len(df_full):,}")
    st.caption(f"Customers: {df_full['CustomerID'].nunique():,}")
    st.caption(f"Products: {df_full['StockCode'].nunique():,}")
    st.caption(f"Countries: {df_full['Country'].nunique():,}")


# ============================================================
# APPLY FILTERS
# ============================================================

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = MIN_DATE, MAX_DATE

mask = (
    (df_full["InvoiceDate"].dt.date >= start_date)
    & (df_full["InvoiceDate"].dt.date <= end_date)
)

if selected_countries:
    mask &= df_full["Country"].isin(selected_countries)

df = df_full.loc[mask].copy()

if df.empty:
    st.warning("No transactions match the selected filters. Showing the full dataset instead.")
    df = df_full.copy()

# ---- Currency: switches to the selected country's currency when exactly
# one country is filtered; falls back to base (GBP) otherwise. Applied by
# scaling Revenue once here so every downstream calculation (KPIs, RFM,
# forecast, chatbot) is already in the right currency - no rate math needed
# anywhere else, just the right symbol. ----
currency_code, currency_symbol, fx_rate = get_currency_for_countries(selected_countries)
df["Revenue"] = df["Revenue"] * fx_rate


# ============================================================
# TOP BAR
# ============================================================

top_left, top_right = st.columns([3, 2])

with top_left:
    page_titles = {
        "🏠  Dashboard": ("Overview", "Store performance at a glance"),
        "📈  Sales Analytics": ("Sales Analytics", "Revenue trends over time"),
        "👥  Customers": ("Customers", "RFM segmentation & customer value"),
        "📦  Products & Countries": ("Products & Countries", "What sells, and where"),
        "🔮  Forecast": ("Revenue Forecast", "Projected performance"),
        "🤖  Assistant": ("Analytics Assistant", "Ask questions about this data"),
    }
    title, sub = page_titles[page]
    st.markdown(f'<div class="riq-topbar-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="riq-topbar-sub">{sub}</div>', unsafe_allow_html=True)

with top_right:
    st.text_input(
        "Search",
        placeholder="🔍  Search products, customers, orders…",
        label_visibility="collapsed",
    )

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption(
    f"💱 Currency: {currency_code} ({currency_symbol.strip()}) — "
    + ("auto-selected from country filter" if len(selected_countries) == 1 else "base currency")
)


# ============================================================
# SHARED HELPERS
# ============================================================

def month_over_month(df_in: pd.DataFrame, value_col: str, agg="sum"):
    """Return (current, previous, pct_change) for the last two months present."""
    monthly = (
        df_in.groupby("MonthPeriod")[value_col]
        .agg(agg)
        .sort_index()
    )
    if len(monthly) < 2:
        return monthly.iloc[-1] if len(monthly) else 0, None, None
    current, previous = monthly.iloc[-1], monthly.iloc[-2]
    pct = ((current - previous) / previous * 100) if previous else None
    return current, previous, pct


def fmt_money(x):
    return f"{currency_symbol}{x:,.0f}"


# ============================================================
# KPI ROW (shown on every page — same story, one glance)
# ============================================================

total_revenue = df["Revenue"].sum()
total_orders = df["InvoiceNo"].nunique()
total_customers = df["CustomerID"].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0

rev_cur, rev_prev, rev_pct = month_over_month(df, "Revenue", "sum")
ord_cur, ord_prev, ord_pct = month_over_month(
    df.drop_duplicates("InvoiceNo"), "InvoiceNo", "count"
)
cust_monthly = df.groupby("MonthPeriod")["CustomerID"].nunique().sort_index()
cust_pct = None
if len(cust_monthly) >= 2 and cust_monthly.iloc[-2]:
    cust_pct = (cust_monthly.iloc[-1] - cust_monthly.iloc[-2]) / cust_monthly.iloc[-2] * 100

aov_pct = None
try:
    monthly_aov = df.groupby("MonthPeriod").agg(
        Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique")
    ).sort_index()
    monthly_aov["AOV"] = monthly_aov["Revenue"] / monthly_aov["Orders"]
    if len(monthly_aov) >= 2 and monthly_aov["AOV"].iloc[-2]:
        aov_pct = (
            (monthly_aov["AOV"].iloc[-1] - monthly_aov["AOV"].iloc[-2])
            / monthly_aov["AOV"].iloc[-2] * 100
        )
except Exception:
    aov_pct = None

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        kpi_card(
            "💰", "Total Revenue", fmt_money(total_revenue),
            f"{abs(rev_pct):.1f}%" if rev_pct is not None else None,
            positive=(rev_pct or 0) >= 0,
        ),
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        kpi_card(
            "🛒", "Total Orders", f"{total_orders:,}",
            f"{abs(ord_pct):.1f}%" if ord_pct is not None else None,
            positive=(ord_pct or 0) >= 0,
        ),
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        kpi_card(
            "👥", "Total Customers", f"{total_customers:,}",
            f"{abs(cust_pct):.1f}%" if cust_pct is not None else None,
            positive=(cust_pct or 0) >= 0,
        ),
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        kpi_card(
            "🎯", "Avg. Order Value", fmt_money(avg_order_value),
            f"{abs(aov_pct):.1f}%" if aov_pct is not None else None,
            positive=(aov_pct or 0) >= 0,
        ),
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


# ============================================================
# CACHED ANALYTICS (recomputed whenever filters change)
# ============================================================

@st.cache_data
def get_monthly_sales(df_in):
    return create_monthly_sales(df_in)


@st.cache_data
def get_rfm_segments(df_in):
    rfm = calculate_rfm(df_in)
    try:
        rfm = calculate_rfm_scores(rfm)
        rfm = assign_customer_segments(rfm)
    except ValueError:
        # Not enough distinct values to build 5 quantile bins (small filtered sample)
        rfm["Segment"] = "Regular Customers"
    return rfm


@st.cache_data
def get_product_performance(df_in):
    return calculate_product_performance(df_in)


@st.cache_data
def get_country_performance(df_in):
    return calculate_country_performance(df_in)


monthly_sales = get_monthly_sales(df)
rfm = get_rfm_segments(df)
product_perf = get_product_performance(df)
country_perf = get_country_performance(df)


# ============================================================
# PAGE: DASHBOARD (OVERVIEW)
# ============================================================

if page == "🏠  Dashboard":

    left, right = st.columns([2, 1])

    # ---------------- Sales Analytic (area chart) ----------------
    with left:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(
            section_header("Sales Analytic", "Revenue trend across the selected period"),
            unsafe_allow_html=True,
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=monthly_sales["Month"],
                y=monthly_sales["Revenue"],
                mode="lines",
                line=dict(color=ACCENT, width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(16,185,129,0.12)",
                hovertemplate="%{x|%b %Y}<br>" + currency_symbol + "%{y:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F0F2F6", tickprefix=currency_symbol),
            showlegend=False,
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Sales Target (donut) ----------------
    with right:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Sales Target"), unsafe_allow_html=True)

        default_target = float(rev_cur) * 1.15 if rev_cur else float(total_revenue) * 0.1
        target = st.number_input(
            f"Monthly target ({currency_symbol})",
            min_value=1000.0,
            value=round(default_target, -2) if default_target else 10000.0,
            step=1000.0,
            label_visibility="collapsed",
        )
        achieved_pct = min(100, (rev_cur / target * 100) if target else 0)

        donut = go.Figure(
            go.Pie(
                values=[achieved_pct, max(0, 100 - achieved_pct)],
                hole=0.78,
                sort=False,
                direction="clockwise",
                marker=dict(colors=[ACCENT, "#EEF1F6"]),
                textinfo="none",
                hoverinfo="skip",
            )
        )
        donut.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            annotations=[
                dict(text=f"{achieved_pct:.0f}%", x=0.5, y=0.5, font_size=24,
                     font_color="#1F2A37", showarrow=False)
            ],
        )
        st.plotly_chart(donut, width="stretch", config={"displayModeBar": False})

        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-top:4px;">
                <div>
                    <div style="color:#6B7280;">This month</div>
                    <div style="font-weight:700;">{fmt_money(rev_cur)}</div>
                </div>
                <div style="text-align:right;">
                    <div style="color:#6B7280;">Target</div>
                    <div style="font-weight:700;">{fmt_money(target)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    left2, right2 = st.columns([2, 1])

    # ---------------- Top Selling Products ----------------
    with left2:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(
            section_header("Top Selling Products", "By total revenue"),
            unsafe_allow_html=True,
        )

        top5 = product_perf.head(5).reset_index(drop=True)
        cols = st.columns(len(top5)) if len(top5) else []
        for i, (col, row) in enumerate(zip(cols, top5.itertuples())):
            with col:
                desc = str(row.Description) if pd.notna(row.Description) else row.StockCode
                st.markdown(
                    product_card(
                        i,
                        desc,
                        f"{int(row.Quantity):,} units",
                        icon=get_icon_for_description(desc),
                        image_b64=get_image_b64_for_description(desc),
                    ),
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Customer Segments ("Current Offer" style) ----------------
    with right2:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Customer Segments"), unsafe_allow_html=True)

        seg_summary = (
            rfm.groupby("Segment")["Monetary"]
            .agg(["count", "sum"])
            .sort_values("sum", ascending=False)
            .head(4)
        )
        total_seg_revenue = seg_summary["sum"].sum()

        for seg, row in seg_summary.iterrows():
            share = (row["sum"] / total_seg_revenue * 100) if total_seg_revenue else 0
            st.markdown(
                progress_row(
                    seg,
                    f"{int(row['count'])} customers",
                    share,
                ),
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: SALES ANALYTICS
# ============================================================

elif page == "📈  Sales Analytics":

    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Monthly Revenue Trend"), unsafe_allow_html=True)
        fig = px.area(monthly_sales, x="Month", y="Revenue")
        fig.update_traces(line_color=ACCENT, fillcolor="rgba(16,185,129,0.12)")
        fig.update_layout(
            height=340, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis_tickprefix=currency_symbol, xaxis_title=None, yaxis_title=None,
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Orders by Day of Week"), unsafe_allow_html=True)
        dow = df.copy()
        dow["DayName"] = dow["InvoiceDate"].dt.day_name()
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_counts = (
            dow.drop_duplicates("InvoiceNo")
            .groupby("DayName")["InvoiceNo"]
            .count()
            .reindex(order)
            .fillna(0)
        )
        fig2 = px.bar(x=dow_counts.index, y=dow_counts.values)
        fig2.update_traces(marker_color=ACCENT)
        fig2.update_layout(
            height=340, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title=None, yaxis_title=None,
        )
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="riq-card">', unsafe_allow_html=True)
    st.markdown(section_header("Sales by Hour of Day"), unsafe_allow_html=True)
    hourly = (
        df.drop_duplicates("InvoiceNo")
        .groupby("Hour")["InvoiceNo"]
        .count()
        .reindex(range(24), fill_value=0)
    )
    fig3 = px.bar(x=hourly.index, y=hourly.values)
    fig3.update_traces(marker_color=ACCENT)
    fig3.update_layout(
        height=280, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title="Hour", yaxis_title="Orders",
    )
    st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: CUSTOMERS
# ============================================================

elif page == "👥  Customers":

    customer_kpis = calculate_customer_kpis(df)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            kpi_card("💷", "Avg Customer Revenue", fmt_money(customer_kpis["average_customer_revenue"])),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            kpi_card("📊", "Median Customer Revenue", fmt_money(customer_kpis["median_customer_revenue"])),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            kpi_card("🔁", "Avg Orders / Customer", f"{customer_kpis['average_orders_per_customer']:.2f}"),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c4, c5 = st.columns([1, 2])

    with c4:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Segment Breakdown"), unsafe_allow_html=True)
        seg_counts = rfm["Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Customers"]
        fig4 = px.pie(seg_counts, names="Segment", values="Customers", hole=0.55)
        fig4.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), showlegend=True)
        st.plotly_chart(fig4, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("RFM Customer Table", "Recency, Frequency, Monetary + segment"), unsafe_allow_html=True)
        st.dataframe(
            rfm[["CustomerID", "Recency", "Frequency", "Monetary", "Segment"]]
            .sort_values("Monetary", ascending=False)
            .head(50),
            width="stretch",
            height=320,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ---------------- Retention & Win-Back Recommendations ----------------
    st.markdown('<div class="riq-card">', unsafe_allow_html=True)
    st.markdown(
        section_header(
            "Retention & Win-Back Recommendations",
            "What to actually do about each customer segment — not just labels",
        ),
        unsafe_allow_html=True,
    )

    available_segments = [s for s in
        ["At Risk", "Lost Customers", "Champions", "Loyal Customers", "Regular Customers", "New Customers"]
        if s in rfm["Segment"].unique()
    ]
    default_idx = 0 if available_segments else None
    chosen_segment = st.selectbox(
        "Segment", available_segments, index=default_idx if default_idx is not None else 0
    ) if available_segments else None

    if chosen_segment:
        summary = get_segment_summary(rfm, chosen_segment)
        rec = get_recommendations(chosen_segment)

        tone_colors = {
            "critical": ("#FEE2E2", "#B91C1C"),
            "urgent": ("#FEF3C7", "#B45309"),
            "reward": ("#D1FAE5", "#067A55"),
            "grow": ("#DBEAFE", "#1D4ED8"),
            "nudge": ("#EDE9FE", "#6D28D9"),
            "onboard": ("#E0F2FE", "#0369A1"),
            "neutral": ("#EEF1F6", "#6B7280"),
        }
        bg, fg = tone_colors.get(rec["tone"], tone_colors["neutral"])

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(kpi_card("👥", f"{chosen_segment}", f"{summary['count']:,}", None), unsafe_allow_html=True)
        with m2:
            st.markdown(kpi_card("💷", "Revenue at stake", fmt_money(summary["total_monetary"])), unsafe_allow_html=True)
        with m3:
            st.markdown(kpi_card("⏱️", "Avg. days since last order", f"{summary['avg_recency']:.0f}"), unsafe_allow_html=True)

        st.markdown(
            f"""<div style="background:{bg};color:{fg};padding:10px 14px;
                        border-radius:10px;font-weight:600;margin:14px 0 10px;">
                {rec['headline']}
            </div>""",
            unsafe_allow_html=True,
        )
        for tip in rec["tips"]:
            st.markdown(f"- {tip}")
    else:
        st.caption("No segments available for the current filters.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: PRODUCTS & COUNTRIES
# ============================================================

elif page == "📦  Products & Countries":

    st.markdown('<div class="riq-card">', unsafe_allow_html=True)
    st.markdown(
        section_header("Product Gallery", "Real photos where available, icons otherwise"),
        unsafe_allow_html=True,
    )
    gallery = product_perf.head(12).reset_index(drop=True)
    gallery_cols = st.columns(6)
    for i, row in enumerate(gallery.itertuples()):
        desc = str(row.Description) if pd.notna(row.Description) else row.StockCode
        with gallery_cols[i % 6]:
            st.markdown(
                product_card(
                    i,
                    desc,
                    fmt_money(row.Revenue),
                    icon=get_icon_for_description(desc),
                    image_b64=get_image_b64_for_description(desc),
                ),
                unsafe_allow_html=True,
            )
        if i % 6 == 5 and i != len(gallery) - 1:
            gallery_cols = st.columns(6)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Top 10 Products by Revenue"), unsafe_allow_html=True)
        st.dataframe(product_perf.head(10), width="stretch", height=360)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Top 10 Countries by Revenue"), unsafe_allow_html=True)
        top_countries = country_perf.head(10)
        fig5 = px.bar(top_countries, x="Revenue", y="Country", orientation="h")
        fig5.update_traces(marker_color=ACCENT)
        fig5.update_layout(
            height=360, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(autorange="reversed"), xaxis_title=None, yaxis_title=None,
        )
        st.plotly_chart(fig5, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="riq-card">', unsafe_allow_html=True)
    st.markdown(section_header("Full Country Performance"), unsafe_allow_html=True)
    st.dataframe(country_perf, width="stretch", height=320)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: FORECAST
# ============================================================

elif page == "🔮  Forecast":

    if len(monthly_sales) < 3:
        st.info("Select a wider date range to generate a reliable forecast (at least 3 months of data).")
    else:
        horizon = st.slider("Forecast horizon (months)", 1, 6, 3)

        model, historical = train_forecasting_model(monthly_sales)
        future_forecast = forecast_future(model, monthly_sales, periods=horizon)

        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(
            section_header("Historical vs Predicted Revenue", "Linear trend model"),
            unsafe_allow_html=True,
        )

        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            x=historical["Month"], y=historical["Revenue"],
            name="Actual", mode="lines+markers", line=dict(color=ACCENT, width=3),
        ))
        fig6.add_trace(go.Scatter(
            x=historical["Month"], y=historical["PredictedRevenue"],
            name="Trend", mode="lines", line=dict(color="#6366F1", width=2, dash="dash"),
        ))
        fig6.add_trace(go.Scatter(
            x=future_forecast["Month"], y=future_forecast["ForecastRevenue"],
            name="Forecast", mode="lines+markers",
            line=dict(color="#F59E0B", width=3, dash="dot"),
        ))
        fig6.update_layout(
            height=360, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis_tickprefix=currency_symbol, legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig6, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        cols = st.columns(horizon)
        for col, row in zip(cols, future_forecast.itertuples()):
            with col:
                st.markdown(
                    kpi_card("🔮", row.Month.strftime("%b %Y"), fmt_money(row.ForecastRevenue)),
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown(section_header("Forecast Table"), unsafe_allow_html=True)
        st.dataframe(future_forecast, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: ASSISTANT (chatbot)
# ============================================================

elif page == "🤖  Assistant":

    st.markdown('<div class="riq-card">', unsafe_allow_html=True)

    ai_col, toggle_col = st.columns([3, 1])
    with ai_col:
        st.markdown(
            section_header(
                "Ask RetailIQ",
                "Rule-based mode needs no API key. AI mode answers open-ended "
                "questions using your own Gemini API key.",
            ),
            unsafe_allow_html=True,
        )
    with toggle_col:
        ai_mode = st.toggle("🧠 AI Mode", value=False)

    api_key_input = ""
    if ai_mode:
        if not ai_is_installed():
            st.warning(
                "AI mode needs the `google-genai` package. Run "
                "`pip install google-genai` (already in requirements.txt) and restart the app."
            )
        env_key = ai_get_key()
        if env_key:
            st.caption("✅ Using GEMINI_API_KEY from environment / .env — no need to paste a key.")
        else:
            api_key_input = st.text_input(
                "Gemini API key (used for this session only, never saved to disk)",
                type="password",
                placeholder="Paste your free Gemini API key here…",
            )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Hi! Ask me things like “top 5 products”, “revenue in "
                    "Germany”, “best month”, or “customer segments”. "
                    "Turn on AI Mode above for open-ended business questions."
                ),
            }
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    suggestion_cols = st.columns(4)
    if ai_mode:
        suggestions = [
            "What's driving revenue growth?",
            "Which products should we discount?",
            "Any risks in this data?",
            "How's customer retention looking?",
        ]
    else:
        suggestions = ["Top 5 products", "Customer segments", "Best month", "Average order value"]
    clicked = None
    for col, s in zip(suggestion_cols, suggestions):
        with col:
            if st.button(s, width="stretch"):
                clicked = s

    placeholder = (
        "Ask anything about this dataset…" if ai_mode
        else "Ask about revenue, products, countries, customers…"
    )
    user_question = st.chat_input(placeholder) or clicked

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        if ai_mode:
            key = ai_get_key(api_key_input)
            data_ctx = ai_build_context(df, rfm, product_perf, country_perf, monthly_sales, currency_symbol)
            reply, err = ask_ai(key, user_question, data_ctx, st.session_state.chat_history)
            reply = reply or f"⚠️ {err}"
        else:
            ctx = chatbot_context(df, rfm, product_perf, country_perf, monthly_sales)
            chatbot_set_currency(currency_symbol)
            reply = chatbot_answer(user_question, ctx)

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.caption("RetailIQ | Full-Cycle E-Commerce Customer & Sales Analytics")

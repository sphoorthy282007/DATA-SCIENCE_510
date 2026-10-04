"""
RetailIQ - Dashboard Theme & UI Components

Holds the injected CSS and small HTML-card helpers used to give the
Streamlit dashboard the polished "admin panel" look (rounded white
cards, soft shadows, teal accent, pill-style sidebar navigation)
instead of the default Streamlit look.

Nothing here touches the analytics - it is purely presentational.
"""

from typing import Optional

ACCENT = "#10B981"
ACCENT_SOFT = "#D1FAE5"
INK = "#1F2A37"
MUTED = "#6B7280"
DANGER = "#EF4444"

CUSTOM_CSS = f"""
<style>
    /* ---------- Global ---------- */
    html, body, [class*="css"] {{
        font-family: "Inter", "Segoe UI", sans-serif;
    }}

    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }}

    #MainMenu, footer {{visibility: hidden;}}

    /* Keep the header element itself in the layout (so its sidebar
       toggle control still works) but make it visually blend away. */
    header[data-testid="stHeader"] {{
        background: transparent;
        box-shadow: none;
    }}

    /* Belt-and-braces: force the collapsed-sidebar re-expand button
       visible regardless of which Streamlit version nests it where. */
    [data-testid="collapsedControl"] {{
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF;
        border-right: 1px solid #EEF1F6;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.2rem;
    }}

    div[role="radiogroup"] {{
        gap: 2px;
    }}

    div[role="radiogroup"] label {{
        padding: 9px 14px;
        border-radius: 10px;
        width: 100%;
        color: {MUTED};
        font-weight: 500;
        transition: background-color .15s ease;
    }}

    div[role="radiogroup"] label:hover {{
        background-color: #F4F7FB;
    }}

    div[role="radiogroup"] label:has(input:checked) {{
        background-color: {ACCENT};
    }}

    div[role="radiogroup"] label:has(input:checked) p {{
        color: white !important;
        font-weight: 600;
    }}

    div[role="radiogroup"] input[type="radio"] {{
        display: none;
    }}

    /* ---------- Cards ---------- */
    .riq-card {{
        background: #FFFFFF;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
        border: 1px solid #EEF1F6;
        height: 100%;
    }}

    .riq-kpi-icon {{
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: {ACCENT_SOFT};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 10px;
    }}

    .riq-kpi-label {{
        color: {MUTED};
        font-size: 12.5px;
        margin-bottom: 2px;
    }}

    .riq-kpi-value {{
        color: {INK};
        font-size: 24px;
        font-weight: 700;
        line-height: 1.2;
    }}

    .riq-badge {{
        display: inline-block;
        font-size: 11.5px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 20px;
        margin-top: 6px;
    }}

    .riq-badge-up {{
        background: {ACCENT_SOFT};
        color: #067A55;
    }}

    .riq-badge-down {{
        background: #FEE2E2;
        color: #B91C1C;
    }}

    .riq-section-title {{
        font-size: 16px;
        font-weight: 700;
        color: {INK};
        margin-bottom: 2px;
    }}

    .riq-section-sub {{
        font-size: 12px;
        color: {MUTED};
        margin-bottom: 14px;
    }}

    /* ---------- Product card ---------- */
    .riq-product-card {{
        background: #FFFFFF;
        border: 1px solid #EEF1F6;
        border-radius: 14px;
        padding: 14px;
        text-align: left;
        height: 100%;
    }}

    .riq-product-tile {{
        width: 100%;
        height: 64px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 20px;
        color: white;
        margin-bottom: 10px;
    }}

    .riq-product-name {{
        font-size: 13px;
        font-weight: 600;
        color: {INK};
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .riq-product-meta {{
        font-size: 11.5px;
        color: {MUTED};
    }}

    /* ---------- Progress rows (segments / "offers") ---------- */
    .riq-progress-row {{
        margin-bottom: 14px;
    }}

    .riq-progress-top {{
        display: flex;
        justify-content: space-between;
        font-size: 12.5px;
        margin-bottom: 6px;
    }}

    .riq-progress-title {{
        font-weight: 600;
        color: {INK};
    }}

    .riq-progress-sub {{
        color: {MUTED};
    }}

    .riq-progress-track {{
        width: 100%;
        height: 7px;
        background: #EEF1F6;
        border-radius: 8px;
        overflow: hidden;
    }}

    .riq-progress-fill {{
        height: 100%;
        border-radius: 8px;
        background: {ACCENT};
    }}

    /* ---------- Top header ---------- */
    .riq-topbar-title {{
        font-size: 22px;
        font-weight: 700;
        color: {INK};
        margin-bottom: 0;
    }}

    .riq-topbar-sub {{
        font-size: 12.5px;
        color: {MUTED};
    }}

    div[data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid #EEF1F6;
        border-radius: 14px;
        padding: 12px 16px;
    }}
</style>
"""

TILE_COLORS = [
    "linear-gradient(135deg,#10B981,#059669)",
    "linear-gradient(135deg,#6366F1,#4338CA)",
    "linear-gradient(135deg,#F59E0B,#D97706)",
    "linear-gradient(135deg,#EC4899,#BE185D)",
    "linear-gradient(135deg,#0EA5E9,#0369A1)",
    "linear-gradient(135deg,#8B5CF6,#6D28D9)",
]


def kpi_card(icon: str, label: str, value: str, delta: Optional[str] = None,
             positive: bool = True) -> str:
    """Return HTML for a single KPI card."""
    badge_html = ""
    if delta is not None:
        arrow = "↑" if positive else "↓"
        cls = "riq-badge-up" if positive else "riq-badge-down"
        badge_html = f'<div class="riq-badge {cls}">{arrow} {delta}</div>'

    return f"""
    <div class="riq-card">
        <div class="riq-kpi-icon">{icon}</div>
        <div class="riq-kpi-label">{label}</div>
        <div class="riq-kpi-value">{value}</div>
        {badge_html}
    </div>
    """


def section_header(title: str, subtitle: str = "") -> str:
    sub_html = f'<div class="riq-section-sub">{subtitle}</div>' if subtitle else ""
    return f'<div class="riq-section-title">{title}</div>{sub_html}'


def product_card(rank: int, name: str, meta: str, icon: Optional[str] = None,
                  image_b64: Optional[str] = None) -> str:
    color = TILE_COLORS[rank % len(TILE_COLORS)]
    safe_name = (name[:22] + "…") if len(str(name)) > 22 else name

    if image_b64:
        tile_html = (
            f'<div class="riq-product-tile" style="padding:0;overflow:hidden;">'
            f'<img src="data:image/jpeg;base64,{image_b64}" '
            f'style="width:100%;height:100%;object-fit:cover;border-radius:10px;" />'
            f'</div>'
        )
    else:
        tile_content = icon if icon else (
            "".join([w[0] for w in str(name).split()[:2]]).upper() or "P"
        )
        tile_font = "28px" if icon else "20px"
        tile_html = (
            f'<div class="riq-product-tile" style="background:{color};font-size:{tile_font};">'
            f'{tile_content}</div>'
        )

    return f"""
    <div class="riq-product-card">
        {tile_html}
        <div class="riq-product-name" title="{name}">{safe_name}</div>
        <div class="riq-product-meta">{meta}</div>
    </div>
    """


def progress_row(title: str, sub: str, pct: float) -> str:
    pct = max(0, min(100, pct))
    return f"""
    <div class="riq-progress-row">
        <div class="riq-progress-top">
            <span class="riq-progress-title">{title}</span>
            <span class="riq-progress-sub">{sub}</span>
        </div>
        <div class="riq-progress-track">
            <div class="riq-progress-fill" style="width:{pct}%;"></div>
        </div>
    </div>
    """

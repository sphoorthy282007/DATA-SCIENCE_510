"""
RetailIQ - Data Cleaning Module
"""

import pandas as pd

# Column names used everywhere downstream in RetailIQ (src/, dashboard/).
# Different releases of the "Online Retail" dataset use different headers
# (e.g. UCI's "Online Retail II" uses "Invoice", "Customer ID", "Price"
# instead of "InvoiceNo", "CustomerID", "UnitPrice"). This map lets any of
# those variants be normalized to the one schema the rest of the project
# expects, so the same pipeline runs unchanged regardless of which file
# was uploaded.
COLUMN_ALIASES = {
    "invoice": "InvoiceNo",
    "invoiceno": "InvoiceNo",
    "invoice_no": "InvoiceNo",
    "stockcode": "StockCode",
    "stock_code": "StockCode",
    "description": "Description",
    "quantity": "Quantity",
    "invoicedate": "InvoiceDate",
    "invoice_date": "InvoiceDate",
    "unitprice": "UnitPrice",
    "unit_price": "UnitPrice",
    "price": "UnitPrice",
    "customerid": "CustomerID",
    "customer_id": "CustomerID",
    "customer id": "CustomerID",
    "country": "Country",
}

REQUIRED_COLUMNS = [
    "InvoiceNo", "StockCode", "Description", "Quantity",
    "InvoiceDate", "UnitPrice", "CustomerID", "Country",
]


def normalize_columns(df):
    """
    Rename whatever headers the source file uses to RetailIQ's standard
    schema, so Online Retail I, Online Retail II, or any similarly-shaped
    export can all be fed through the same pipeline.
    """

    df = df.copy()

    rename_map = {}
    for col in df.columns:
        key = str(col).strip().lower()
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]

    df = df.rename(columns=rename_map)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "This file is missing column(s) RetailIQ needs: "
            f"{', '.join(missing)}. Expected a transactional export with "
            "invoice, product, quantity, price, customer and country "
            "columns (like the UCI 'Online Retail' dataset)."
        )

    return df[REQUIRED_COLUMNS]


def load_data(file_path_or_buffer, filename=None):
    """
    Load a retail dataset from a path (str) or an in-memory buffer, e.g.
    the object returned by Streamlit's st.file_uploader. `filename` is
    only needed when passing a buffer, to detect csv vs excel.
    """

    name = filename or (
        file_path_or_buffer if isinstance(file_path_or_buffer, str) else ""
    )

    if str(name).lower().endswith(".csv"):
        df = pd.read_csv(file_path_or_buffer)
    else:
        df = pd.read_excel(file_path_or_buffer)

    return normalize_columns(df)


def clean_data(df):
    """Clean the retail transaction dataset."""

    df = df.copy()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove rows without CustomerID
    df = df.dropna(subset=["CustomerID"])

    # Remove returns / negative quantities
    df = df[df["Quantity"] > 0]

    # Remove zero or negative prices
    df = df[df["UnitPrice"] > 0]

    return df
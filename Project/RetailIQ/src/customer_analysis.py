"""
RetailIQ - Customer Analysis Module

Functions for customer-level KPIs and RFM analysis.
"""

import pandas as pd


def calculate_customer_kpis(df):
    """Calculate overall customer KPIs."""

    total_customers = df["CustomerID"].nunique()

    customer_revenue = df.groupby("CustomerID")["Revenue"].sum()

    average_customer_revenue = customer_revenue.mean()
    median_customer_revenue = customer_revenue.median()

    orders_per_customer = (
        df.groupby("CustomerID")["InvoiceNo"]
        .nunique()
    )

    average_orders_per_customer = orders_per_customer.mean()

    return {
        "total_customers": total_customers,
        "average_customer_revenue": average_customer_revenue,
        "median_customer_revenue": median_customer_revenue,
        "average_orders_per_customer": average_orders_per_customer
    }


def calculate_rfm(df, analysis_date=None):
    """Calculate Recency, Frequency and Monetary values."""

    df = df.copy()

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    if analysis_date is None:
        analysis_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("CustomerID")
        .agg(
            Recency=("InvoiceDate",
                     lambda x: (analysis_date - x.max()).days),
            Frequency=("InvoiceNo", "nunique"),
            Monetary=("Revenue", "sum")
        )
        .reset_index()
    )

    return rfm
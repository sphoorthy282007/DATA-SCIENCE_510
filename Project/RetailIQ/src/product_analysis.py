"""
RetailIQ - Product Analysis Module

Functions for product and country-level sales analysis.
"""

import pandas as pd


def calculate_product_performance(df):
    """Calculate product-level sales performance."""

    product_performance = (
        df.groupby(["StockCode", "Description"])
        .agg(
            Quantity=("Quantity", "sum"),
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique")
        )
        .reset_index()
    )

    product_performance = product_performance.sort_values(
        "Revenue",
        ascending=False
    )

    return product_performance


def calculate_country_performance(df):
    """Calculate country-level sales performance."""

    country_performance = (
        df.groupby("Country")
        .agg(
            Quantity=("Quantity", "sum"),
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique")
        )
        .reset_index()
    )

    country_performance = country_performance.sort_values(
        "Revenue",
        ascending=False
    )

    return country_performance
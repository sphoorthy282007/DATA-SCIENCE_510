"""
RetailIQ - Feature Engineering Module

This module creates useful features for sales analysis.
"""

import pandas as pd


def create_revenue(df):
    """
    Create Revenue from Quantity and UnitPrice.
    """

    df = df.copy()

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    return df


def create_date_features(df):
    """
    Create useful date-based features.
    """

    df = df.copy()

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.month
    df["Day"] = df["InvoiceDate"].dt.day
    df["Hour"] = df["InvoiceDate"].dt.hour

    return df
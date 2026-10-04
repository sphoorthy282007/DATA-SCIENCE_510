"""
RetailIQ - Customer Segmentation Module

Functions for scoring and segmenting customers using RFM analysis.
"""

import pandas as pd


def calculate_rfm_scores(rfm):
    """Create RFM scores from Recency, Frequency and Monetary values."""

    rfm = rfm.copy()

    rfm["R_Score"] = pd.qcut(
        rfm["Recency"],
        5,
        labels=[5, 4, 3, 2, 1],
        duplicates="drop"
    ).astype(int)

    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(str)
        + rfm["F_Score"].astype(str)
        + rfm["M_Score"].astype(str)
    )

    return rfm


def assign_customer_segments(rfm):
    """Assign customers to business-oriented segments."""

    rfm = rfm.copy()

    def segment_customer(row):

        r = row["R_Score"]
        f = row["F_Score"]
        m = row["M_Score"]

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"

        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"

        elif r >= 4 and f <= 2:
            return "New Customers"

        elif r <= 2 and f >= 3:
            return "At Risk"

        elif r <= 2 and f <= 2:
            return "Lost Customers"

        else:
            return "Regular Customers"

    rfm["Segment"] = rfm.apply(segment_customer, axis=1)

    return rfm
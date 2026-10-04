"""
RetailIQ - Sales Forecasting Module

Functions for preparing monthly sales data
and generating revenue forecasts.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def create_monthly_sales(df):
    """Create monthly revenue dataset."""

    df = df.copy()

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    monthly_sales = (
        df.set_index("InvoiceDate")
        .resample("ME")["Revenue"]
        .sum()
        .reset_index()
    )

    monthly_sales.columns = ["Month", "Revenue"]

    return monthly_sales


def train_forecasting_model(monthly_sales):
    """Train a baseline linear regression forecasting model."""

    data = monthly_sales.copy()

    data["TimeIndex"] = np.arange(len(data))

    X = data[["TimeIndex"]]
    y = data["Revenue"]

    model = LinearRegression()

    model.fit(X, y)

    data["PredictedRevenue"] = model.predict(X)

    return model, data


def forecast_future(model, monthly_sales, periods=3):
    """Forecast future monthly revenue."""

    last_index = len(monthly_sales) - 1

    future_indices = np.arange(
        last_index + 1,
        last_index + periods + 1
    )

    predictions = model.predict(
        future_indices.reshape(-1, 1)
    )

    future_dates = pd.date_range(
        start=monthly_sales["Month"].max() + pd.offsets.MonthEnd(1),
        periods=periods,
        freq="ME"
    )

    forecast = pd.DataFrame({
        "Month": future_dates,
        "ForecastRevenue": predictions
    })

    return forecast
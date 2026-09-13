import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

def compute_latest_arbitrage(df: pd.DataFrame, commodity: str) -> Dict[str, Any]:
    comm_df = df[df["commodity"].str.lower() == commodity.lower()].copy()
    if comm_df.empty:
        return {"error": f"No data found for commodity '{commodity}'"}
    
    latest_date = comm_df["arrival_date"].max()
    latest_slice = comm_df[comm_df["arrival_date"] == latest_date]
    if latest_slice.empty:
        return {"error": f"No recent records for commodity '{commodity}'"}
        
    highest_row = latest_slice.loc[latest_slice["modal_price"].idxmax()]
    lowest_row = latest_slice.loc[latest_slice["modal_price"].idxmin()]
    
    spread = float(highest_row["modal_price"] - lowest_row["modal_price"])
    pct = round((spread / lowest_row["modal_price"]) * 100, 2) if lowest_row["modal_price"] > 0 else 0.0
    
    return {
        "commodity": commodity,
        "date": latest_date.strftime("%Y-%m-%d"),
        "highest_mandi": {
            "market": highest_row["market"],
            "district": highest_row["district"],
            "division": highest_row.get("division", "Maharashtra"),
            "modal_price": float(highest_row["modal_price"]),
            "min_price": float(highest_row["min_price"]),
            "max_price": float(highest_row["max_price"]),
            "arrivals_tonnes": float(highest_row["arrivals_in_tonnes"])
        },
        "lowest_mandi": {
            "market": lowest_row["market"],
            "district": lowest_row["district"],
            "division": lowest_row.get("division", "Maharashtra"),
            "modal_price": float(lowest_row["modal_price"]),
            "min_price": float(lowest_row["min_price"]),
            "max_price": float(lowest_row["max_price"]),
            "arrivals_tonnes": float(lowest_row["arrivals_in_tonnes"])
        },
        "spread_rs": spread,
        "spread_pct": pct,
        "total_mandis_reporting": int(len(latest_slice))
    }

def compute_district_timeseries(df: pd.DataFrame, commodity: str, district: str) -> pd.DataFrame:
    sub = df[(df["commodity"].str.lower() == commodity.lower()) & (df["district"].str.lower() == district.lower())].copy()
    if sub.empty:
        return pd.DataFrame()
    grouped = sub.groupby("arrival_date").agg({
        "modal_price": "mean",
        "min_price": "min",
        "max_price": "max",
        "arrivals_in_tonnes": "sum"
    }).reset_index()
    return grouped.sort_values("arrival_date")

def detect_price_anomalies(df: pd.DataFrame, commodity: Optional[str] = None, z_threshold: float = 2.0) -> pd.DataFrame:
    data = df.copy()
    if commodity:
        data = data[data["commodity"].str.lower() == commodity.lower()]
    if data.empty:
        return pd.DataFrame()
    
    mean = data["modal_price"].mean()
    std = data["modal_price"].std()
    if std == 0 or np.isnan(std):
        return pd.DataFrame()
    
    data["z_score"] = (data["modal_price"] - mean) / std
    anomalies = data[data["z_score"].abs() >= z_threshold].copy()
    anomalies["arrival_date"] = anomalies["arrival_date"].dt.strftime("%Y-%m-%d")
    return anomalies.sort_values(by="z_score", ascending=False)

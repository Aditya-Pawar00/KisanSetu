from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

def compute_latest_arbitrage(df: pd.DataFrame, commodity: str) -> Dict[str, Any]:
    comm_df = df[df["commodity"].str.lower() == commodity.lower()].copy()
    if comm_df.empty:
        return {"error": f"No data found for commodity '{commodity}'"}

    latest_date = comm_df["arrival_date"].max()
    latest_records = comm_df[comm_df["arrival_date"] == latest_date].copy()

    district_summary = (
        latest_records.groupby("district")
        .agg(
            avg_modal=("modal_price", "mean"),
            min_modal=("modal_price", "min"),
            max_modal=("modal_price", "max"),
            total_arrivals=("arrivals_in_tonnes", "sum"),
            markets=("market", lambda x: list(x.unique())),
        )
        .reset_index()
    )

    district_summary["avg_modal"] = district_summary["avg_modal"].round(2)
    district_summary = district_summary.sort_values(by="avg_modal", ascending=False)

    cheapest = district_summary.iloc[-1]
    costliest = district_summary.iloc[0]

    spread_abs = round(costliest["avg_modal"] - cheapest["avg_modal"], 2)
    spread_pct = round((spread_abs / cheapest["avg_modal"]) * 100, 2) if cheapest["avg_modal"] > 0 else 0.0

    return {
        "commodity": commodity,
        "date": latest_date.strftime("%Y-%m-%d"),
        "spread_abs_rs_quintal": spread_abs,
        "spread_pct": spread_pct,
        "cheapest_district": cheapest["district"],
        "cheapest_price": cheapest["avg_modal"],
        "costliest_district": costliest["district"],
        "costliest_price": costliest["avg_modal"],
        "rankings": district_summary.to_dict(orient="records"),
    }

def compute_district_timeseries(df: pd.DataFrame, commodity: str, district: str) -> pd.DataFrame:
    subset = df[
        (df["commodity"].str.lower() == commodity.lower())
        & (df["district"].str.lower() == district.lower())
    ].copy()

    if subset.empty:
        return pd.DataFrame()

    daily = (
        subset.groupby("arrival_date")
        .agg(
            modal_price=("modal_price", "mean"),
            min_price=("min_price", "min"),
            max_price=("max_price", "max"),
            arrivals_tonnes=("arrivals_in_tonnes", "sum"),
        )
        .reset_index()
        .sort_values("arrival_date")
    )

    daily["modal_price"] = daily["modal_price"].round(2)
    daily["sma_7"] = daily["modal_price"].rolling(window=7, min_periods=3).mean().round(2)
    daily["sma_30"] = daily["modal_price"].rolling(window=30, min_periods=7).mean().round(2)
    daily["volatility_7d"] = daily["modal_price"].rolling(window=7, min_periods=3).std().round(2)
    return daily

def detect_price_anomalies(
    df: pd.DataFrame, commodity: Optional[str] = None, z_threshold: float = 2.0, window: int = 14
) -> pd.DataFrame:
    data = df.copy()
    if commodity:
        data = data[data["commodity"].str.lower() == commodity.lower()]

    anomaly_records = []
    for (dist, mkt, comm), group in data.groupby(["district", "market", "commodity"]):
        grp = group.sort_values("arrival_date").copy()
        if len(grp) < window:
            continue

        rolling_mean = grp["modal_price"].rolling(window=window, min_periods=7).mean()
        rolling_std = grp["modal_price"].rolling(window=window, min_periods=7).std().replace(0, np.nan)

        grp["z_score"] = (grp["modal_price"] - rolling_mean) / rolling_std
        grp["expected_price"] = rolling_mean.round(2)

        anomalies = grp[grp["z_score"].abs() >= z_threshold].copy()
        for _, row in anomalies.iterrows():
            z_val = round(row["z_score"], 2)
            alert_type = "PRICE_SURGE" if z_val > 0 else "PRICE_CRASH"
            anomaly_records.append({
                "arrival_date": row["arrival_date"].strftime("%Y-%m-%d"),
                "state": row["state"],
                "district": dist,
                "market": mkt,
                "commodity": comm,
                "modal_price": row["modal_price"],
                "expected_price": row["expected_price"],
                "z_score": z_val,
                "alert_type": alert_type,
                "percentage_deviation": round(
                    ((row["modal_price"] - row["expected_price"]) / row["expected_price"]) * 100, 2
                ),
            })

    if not anomaly_records:
        return pd.DataFrame()
    return pd.DataFrame(anomaly_records).sort_values(by="arrival_date", ascending=False).reset_index(drop=True)

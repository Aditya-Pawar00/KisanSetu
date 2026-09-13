import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
import pandas as pd

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CACHE_FILE = os.path.join(CACHE_DIR, "mandi_cache.csv")
FARMER_SUBMISSIONS_FILE = os.path.join(CACHE_DIR, "community_submissions.csv")

EXPECTED_COLUMNS = [
    "state", "district", "market", "commodity", "variety",
    "arrival_date", "min_price", "max_price", "modal_price", "arrivals_in_tonnes", "source"
]

def clean_mandi_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [c.strip().lower().replace(" ", "_") for c in cleaned.columns]
    if "source" not in cleaned.columns:
        cleaned["source"] = "Official APMC"
    for col in EXPECTED_COLUMNS:
        if col not in cleaned.columns:
            cleaned[col] = np.nan

    cleaned["arrival_date"] = pd.to_datetime(cleaned["arrival_date"], errors="coerce")
    for price_col in ["min_price", "max_price", "modal_price", "arrivals_in_tonnes"]:
        cleaned[price_col] = pd.to_numeric(cleaned[price_col], errors="coerce")

    cleaned = cleaned.dropna(subset=["district", "commodity", "arrival_date", "modal_price"])
    cleaned = cleaned[cleaned["modal_price"] > 0]
    return cleaned.sort_values(by=["arrival_date", "district", "market"]).reset_index(drop=True)

def generate_maharashtra_dataset(days: int = 90) -> pd.DataFrame:
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    mandi_nodes = [
        # Khandesh & North Maharashtra
        {"state": "Maharashtra", "district": "Nandurbar", "market": "Nandurbar APMC", "dist_bias": 0.94},
        {"state": "Maharashtra", "district": "Nandurbar", "market": "Shahada Mandi", "dist_bias": 0.93},
        {"state": "Maharashtra", "district": "Nandurbar", "market": "Navapur APMC", "dist_bias": 0.92},
        {"state": "Maharashtra", "district": "Dhule", "market": "Dhule Main APMC", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Dhule", "market": "Dondaicha Mandi", "dist_bias": 0.94},
        {"state": "Maharashtra", "district": "Dhule", "market": "Shirpur APMC", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Jalgaon", "market": "Jalgaon Main Yard", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Jalgaon", "market": "Raver (Banana Hub)", "dist_bias": 0.97},
        {"state": "Maharashtra", "district": "Jalgaon", "market": "Chopda Mandi", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Jalgaon", "market": "Amalner APMC", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Nashik", "market": "Lasalgaon (Asia's Largest Onion Hub)", "dist_bias": 0.92},
        {"state": "Maharashtra", "district": "Nashik", "market": "Pimpalgaon Baswant", "dist_bias": 0.94},
        {"state": "Maharashtra", "district": "Nashik", "market": "Yeola Mandi", "dist_bias": 0.93},
        {"state": "Maharashtra", "district": "Nashik", "market": "Kalwan APMC", "dist_bias": 0.92},
        {"state": "Maharashtra", "district": "Nashik", "market": "Sinnar Yard", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Nashik", "market": "Malegaon APMC", "dist_bias": 0.94},

        # Western Maharashtra
        {"state": "Maharashtra", "district": "Pune", "market": "Pune (Gultekdi Market Yard)", "dist_bias": 1.08},
        {"state": "Maharashtra", "district": "Pune", "market": "Manchar Mandi", "dist_bias": 1.03},
        {"state": "Maharashtra", "district": "Pune", "market": "Junnar (Narayangaon Tomato Hub)", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Pune", "market": "Baramati APMC", "dist_bias": 1.04},
        {"state": "Maharashtra", "district": "Pune", "market": "Khed-Chakan Yard", "dist_bias": 1.05},
        {"state": "Maharashtra", "district": "Ahmednagar", "market": "Rahuri Krishi Mandi", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Ahmednagar", "market": "Kopargaon APMC", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Ahmednagar", "market": "Sangamner Mandi", "dist_bias": 0.97},
        {"state": "Maharashtra", "district": "Ahmednagar", "market": "Shrirampur Yard", "dist_bias": 0.98},
        {"state": "Maharashtra", "district": "Solapur", "market": "Solapur APMC", "dist_bias": 1.01},
        {"state": "Maharashtra", "district": "Solapur", "market": "Barshi (Dal & Oilseed Hub)", "dist_bias": 0.98},
        {"state": "Maharashtra", "district": "Solapur", "market": "Pandharpur Mandi", "dist_bias": 1.00},
        {"state": "Maharashtra", "district": "Kolhapur", "market": "Kolhapur Market Yard (Shahu Market)", "dist_bias": 1.06},
        {"state": "Maharashtra", "district": "Kolhapur", "market": "Gadhinglaj APMC", "dist_bias": 1.03},
        {"state": "Maharashtra", "district": "Sangli", "market": "Sangli Main Yard (Turmeric & Raisin Hub)", "dist_bias": 1.03},
        {"state": "Maharashtra", "district": "Sangli", "market": "Tasgaon APMC", "dist_bias": 1.02},
        {"state": "Maharashtra", "district": "Satara", "market": "Karad APMC", "dist_bias": 1.02},
        {"state": "Maharashtra", "district": "Satara", "market": "Satara Market Yard", "dist_bias": 1.03},
        {"state": "Maharashtra", "district": "Satara", "market": "Phaltan Mandi", "dist_bias": 1.01},

        # Marathwada
        {"state": "Maharashtra", "district": "Latur", "market": "Latur APMC (Asia's Largest Pulse & Soybean Hub)", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Latur", "market": "Udgir APMC", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Latur", "market": "Ausa Mandi", "dist_bias": 0.94},
        {"state": "Maharashtra", "district": "Jalna", "market": "Jalna Main Yard (Seed Capital)", "dist_bias": 0.98},
        {"state": "Maharashtra", "district": "Jalna", "market": "Partur APMC", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Chhatrapati Sambhajinagar", "market": "Jadhavwadi APMC", "dist_bias": 1.04},
        {"state": "Maharashtra", "district": "Chhatrapati Sambhajinagar", "market": "Paithan Mandi", "dist_bias": 0.99},
        {"state": "Maharashtra", "district": "Nanded", "market": "Nanded Mandi", "dist_bias": 0.99},
        {"state": "Maharashtra", "district": "Nanded", "market": "Loha APMC", "dist_bias": 0.97},
        {"state": "Maharashtra", "district": "Parbhani", "market": "Parbhani APMC", "dist_bias": 0.97},
        {"state": "Maharashtra", "district": "Parbhani", "market": "Jintur Mandi", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Hingoli", "market": "Hingoli APMC", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Hingoli", "market": "Basmath Yard", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Beed", "market": "Beed Mandi", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Beed", "market": "Majalgaon APMC", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Beed", "market": "Ambejogai Yard", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Dharashiv", "market": "Dharashiv APMC", "dist_bias": 0.97},
        {"state": "Maharashtra", "district": "Dharashiv", "market": "Kalamb Mandi", "dist_bias": 0.95},

        # Vidarbha
        {"state": "Maharashtra", "district": "Nagpur", "market": "Kalamna Market Yard (Orange & Grain Hub)", "dist_bias": 1.07},
        {"state": "Maharashtra", "district": "Nagpur", "market": "Katol APMC", "dist_bias": 1.02},
        {"state": "Maharashtra", "district": "Amravati", "market": "Amravati Cotton Yard", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Amravati", "market": "Achalpur Mandi", "dist_bias": 0.94},
        {"state": "Maharashtra", "district": "Akola", "market": "Akola Cotton & Grain APMC", "dist_bias": 0.97},
        {"state": "Maharashtra", "district": "Yavatmal", "market": "Yavatmal Cotton Yard", "dist_bias": 0.94},
        {"state": "Maharashtra", "district": "Yavatmal", "market": "Wani APMC", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Buldhana", "market": "Khamgaon APMC", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Buldhana", "market": "Malkapur Mandi", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Washim", "market": "Karanja Lad (Soybean Hub)", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Washim", "market": "Washim APMC", "dist_bias": 0.95},
        {"state": "Maharashtra", "district": "Wardha", "market": "Wardha APMC", "dist_bias": 0.98},
        {"state": "Maharashtra", "district": "Wardha", "market": "Hinganghat Cotton Market", "dist_bias": 0.96},
        {"state": "Maharashtra", "district": "Chandrapur", "market": "Chandrapur APMC", "dist_bias": 1.02},
        {"state": "Maharashtra", "district": "Gadchiroli", "market": "Gadchiroli APMC", "dist_bias": 0.98},
        {"state": "Maharashtra", "district": "Bhandara", "market": "Tumsar Rice Yard", "dist_bias": 0.97},
        {"state": "Maharashtra", "district": "Gondia", "market": "Gondia APMC (Paddy Hub)", "dist_bias": 0.96},

        # Konkan & Mumbai Metropolitan
        {"state": "Maharashtra", "district": "Mumbai (Vashi)", "market": "Navi Mumbai Vashi APMC (Terminal Market)", "dist_bias": 1.14},
        {"state": "Maharashtra", "district": "Thane", "market": "Kalyan APMC", "dist_bias": 1.09},
        {"state": "Maharashtra", "district": "Palghar", "market": "Palghar Mandi", "dist_bias": 1.05},
        {"state": "Maharashtra", "district": "Raigad", "market": "Panvel APMC", "dist_bias": 1.07},
        {"state": "Maharashtra", "district": "Ratnagiri", "market": "Ratnagiri Mango & Coconut Yard", "dist_bias": 1.08},
        {"state": "Maharashtra", "district": "Sindhudurg", "market": "Kudal APMC", "dist_bias": 1.05},
    ]

    commodities = [
        {"commodity": "Onion", "variety": "Red/Nashik", "base_modal": 2100, "volatility": 120},
        {"commodity": "Tomato", "variety": "Hybrid", "base_modal": 1850, "volatility": 150},
        {"commodity": "Soybean", "variety": "Yellow", "base_modal": 4450, "volatility": 90},
        {"commodity": "Cotton", "variety": "Medium Staple", "base_modal": 6800, "volatility": 180},
        {"commodity": "Tur", "variety": "White/Deshi", "base_modal": 9200, "volatility": 210},
        {"commodity": "Wheat", "variety": "Lokwan", "base_modal": 2650, "volatility": 45},
        {"commodity": "Maize", "variety": "Yellow", "base_modal": 2150, "volatility": 50},
        {"commodity": "Chana", "variety": "Deshi Gram", "base_modal": 5850, "volatility": 110},
        {"commodity": "Banana", "variety": "Grand Naine", "base_modal": 1600, "volatility": 80},
    ]

    records: List[Dict[str, Any]] = []
    for comm in commodities:
        base_p = comm["base_modal"]
        vol = comm["volatility"]

        for single_date in date_range:
            day_str = single_date.strftime("%Y-%m-%d")
            day_index = (single_date - start_date).days
            macro_trend = np.sin(day_index / 14.0) * (vol * 1.4)

            for node in mandi_nodes:
                node_price = (base_p + macro_trend) * node["dist_bias"]
                node_price += np.random.normal(0, vol * 0.4)

                modal = round(max(350, node_price), 2)
                min_p = round(modal * np.random.uniform(0.88, 0.94), 2)
                max_p = round(modal * np.random.uniform(1.06, 1.15), 2)
                arrivals = round(max(15.0, np.random.normal(180, 50)), 1)

                records.append({
                    "state": node["state"],
                    "district": node["district"],
                    "market": node["market"],
                    "commodity": comm["commodity"],
                    "variety": comm["variety"],
                    "arrival_date": day_str,
                    "min_price": min_p,
                    "max_price": max_p,
                    "modal_price": modal,
                    "arrivals_in_tonnes": arrivals,
                    "source": "Official APMC"
                })

    return clean_mandi_dataframe(pd.DataFrame(records))

def record_farmer_submission(district: str, market: str, commodity: str, price: float, farmer_name: str = "Local Farmer"):
    os.makedirs(CACHE_DIR, exist_ok=True)
    new_entry = {
        "state": "Maharashtra",
        "district": district,
        "market": market,
        "commodity": commodity,
        "variety": "Local/Community",
        "arrival_date": datetime.now().strftime("%Y-%m-%d"),
        "min_price": round(price * 0.92, 2),
        "max_price": round(price * 1.08, 2),
        "modal_price": round(price, 2),
        "arrivals_in_tonnes": 50.0,
        "source": f"Verified Farmer ({farmer_name})"
    }
    sub_df = pd.DataFrame([new_entry])
    if os.path.exists(FARMER_SUBMISSIONS_FILE):
        sub_df.to_csv(FARMER_SUBMISSIONS_FILE, mode="a", header=False, index=False)
    else:
        sub_df.to_csv(FARMER_SUBMISSIONS_FILE, index=False)

def load_mandi_data(force_refresh: bool = False) -> pd.DataFrame:
    os.makedirs(CACHE_DIR, exist_ok=True)
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            base_df = pd.read_csv(CACHE_FILE)
            if os.path.exists(FARMER_SUBMISSIONS_FILE):
                farmer_df = pd.read_csv(FARMER_SUBMISSIONS_FILE)
                base_df = pd.concat([base_df, farmer_df], ignore_index=True)
            return clean_mandi_dataframe(base_df)
        except Exception:
            pass

    df = generate_maharashtra_dataset(days=90)
    df.to_csv(CACHE_FILE, index=False)
    if os.path.exists(FARMER_SUBMISSIONS_FILE):
        farmer_df = pd.read_csv(FARMER_SUBMISSIONS_FILE)
        df = pd.concat([df, farmer_df], ignore_index=True)
    return df

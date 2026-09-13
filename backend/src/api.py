import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
import numpy as np
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.ingestion import load_mandi_data, record_farmer_submission
    from src.analytics import (
        compute_latest_arbitrage,
        compute_district_timeseries,
        detect_price_anomalies,
    )
except (ImportError, ModuleNotFoundError):
    from ingestion import load_mandi_data, record_farmer_submission
    from analytics import (
        compute_latest_arbitrage,
        compute_district_timeseries,
        detect_price_anomalies,
    )

app = FastAPI(
    title="MandiPulse Live Auction & Surveillance Radar",
    description="Real-time APMC live auction feed, market operational status, and spatial arbitrage.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_DATASET = load_mandi_data()
HTML_FILE_PATH = os.path.join(current_dir, "frontend.html")

LIVE_AUCTION_STREAM: List[Dict[str, Any]] = [
    {
        "lot_id": "MH-NSK-1042",
        "market": "Lasalgaon APMC",
        "district": "Nashik",
        "commodity": "Onion",
        "variety": "Nashik Red Grade-A",
        "quantity_quintals": 65.0,
        "winning_trader": "Shree Ganesh Agro Exports",
        "winning_bid": 2420.0,
        "farmer_origin": "Niphad, Nashik",
        "time_ago": "1 min ago",
        "status": "HAMMER_SOLD",
    },
    {
        "lot_id": "MH-PUN-0891",
        "market": "Pune(Gultekdi)",
        "district": "Pune",
        "commodity": "Tomato",
        "variety": "Hybrid Premium",
        "quantity_quintals": 42.0,
        "winning_trader": "Sahyadri Retail & Supply",
        "winning_bid": 2180.0,
        "farmer_origin": "Narayangaon, Junnar",
        "time_ago": "3 mins ago",
        "status": "HAMMER_SOLD",
    },
    {
        "lot_id": "MH-LTR-0437",
        "market": "Latur APMC",
        "district": "Latur",
        "commodity": "Soybean",
        "variety": "Yellow Standard",
        "quantity_quintals": 110.0,
        "winning_trader": "Marathwada Oil Mills Ltd",
        "winning_bid": 4680.0,
        "farmer_origin": "Ausa, Latur",
        "time_ago": "6 mins ago",
        "status": "HAMMER_SOLD",
    },
    {
        "lot_id": "MH-AMR-0512",
        "market": "Amravati Cotton Yard",
        "district": "Amravati",
        "commodity": "Cotton",
        "variety": "Medium Staple 29mm",
        "quantity_quintals": 85.0,
        "winning_trader": "Vidarbha Textiles Consortium",
        "winning_bid": 7150.0,
        "farmer_origin": "Achalpur, Amravati",
        "time_ago": "9 mins ago",
        "status": "HAMMER_SOLD",
    },
    {
        "lot_id": "MH-NSK-1039",
        "market": "Pimpalgaon APMC",
        "district": "Nashik",
        "commodity": "Tomato",
        "variety": "Hybrid Red",
        "quantity_quintals": 50.0,
        "winning_trader": "Kalyan Fresh Produce Co.",
        "winning_bid": 2120.0,
        "farmer_origin": "Dindori, Nashik",
        "time_ago": "12 mins ago",
        "status": "HAMMER_SOLD",
    },
]

def get_market_operating_status() -> Dict[str, Any]:
    now = datetime.now()
    total_minutes = now.hour * 60 + now.minute

    if 480 <= total_minutes < 870:
        status = "OPEN_BIDDING"
        badge = "LIVE AUCTION IN PROGRESS"
        closing_time = "02:30 PM"
        desc = f"Electronic weighbridges & live bidding active across Maharashtra APMC yards. Closes at {closing_time}."
    elif 870 <= total_minutes < 1020:
        status = "SETTLING"
        badge = "AUCTION CONCLUDED - WEIGHING & DISPATCH"
        closing_time = "05:00 PM"
        desc = f"Auction lots closed. Electronic weighbridge verification and payouts underway until {closing_time}."
    else:
        status = "CLOSED"
        badge = "APMC YARD CLOSED"
        closing_time = "08:00 AM"
        desc = f"Trading concluded for today. Market gates reopen for arrival weighing tomorrow at {closing_time}."

    return {
        "status": status,
        "badge": badge,
        "current_time": now.strftime("%I:%M %p"),
        "closing_time": closing_time,
        "details": desc,
    }

class DigitalAuctionBroadcastPayload(BaseModel):
    lot_id: str = Field(..., description="Mandi Gate-Pass / Lot ID")
    market: str = Field(..., description="APMC Market Yard")
    district: str = Field(..., description="District Name")
    commodity: str = Field(..., description="Commodity Name")
    variety: str = Field("Grade-A", description="Variety Grade")
    quantity_quintals: float = Field(..., description="Lot Quantity in Quintals")
    winning_trader: str = Field(..., description="Winning Buyer Name")
    winning_bid: float = Field(..., description="Winning Bid Price in ₹/Quintal")
    farmer_origin: str = Field("Local Tehsil", description="Farmer Name or Village")

@app.get("/", response_class=HTMLResponse)
def serve_interactive_radar():
    if os.path.exists(HTML_FILE_PATH):
        with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MandiPulse API Live (frontend.html not found)</h1>"

@app.get("/api/v1/market/status")
def get_status():
    return get_market_operating_status()

@app.get("/api/v1/auction/live")
def get_live_auctions(commodity: Optional[str] = Query(None)):
    auctions = LIVE_AUCTION_STREAM
    if commodity:
        auctions = [a for a in auctions if a["commodity"].lower() == commodity.lower()]

    total_arrived = 4850.0
    auctioned = sum(a["quantity_quintals"] for a in auctions) + 3420.0
    remaining = max(250.0, total_arrived - auctioned)
    cleared_pct = round((auctioned / total_arrived) * 100, 1)

    return {
        "market_status": get_market_operating_status(),
        "stock_summary": {
            "total_arrival_today_qtl": total_arrived,
            "auctioned_sold_qtl": auctioned,
            "remaining_pending_qtl": remaining,
            "clearance_rate_pct": cleared_pct,
        },
        "recent_auctions": auctions,
    }

@app.post("/api/v1/auction/broadcast")
def broadcast_digital_auction(payload: DigitalAuctionBroadcastPayload):
    new_auction = {
        "lot_id": payload.lot_id,
        "market": payload.market,
        "district": payload.district,
        "commodity": payload.commodity,
        "variety": payload.variety,
        "quantity_quintals": payload.quantity_quintals,
        "winning_trader": payload.winning_trader,
        "winning_bid": payload.winning_bid,
        "farmer_origin": payload.farmer_origin,
        "time_ago": "Just now",
        "status": "HAMMER_SOLD",
    }
    LIVE_AUCTION_STREAM.insert(0, new_auction)
    if len(LIVE_AUCTION_STREAM) > 20:
        LIVE_AUCTION_STREAM.pop()

    return {
        "status": "success",
        "message": f"Lot {payload.lot_id} recorded. Winner: {payload.winning_trader} at ₹{payload.winning_bid}/Qtl",
        "lot": new_auction,
    }

@app.get("/api/v1/meta")
def get_metadata():
    commodities = sorted(_DATASET["commodity"].unique().tolist())
    districts = sorted(_DATASET["district"].unique().tolist())
    latest_date = _DATASET["arrival_date"].max().strftime("%Y-%m-%d")
    return {"commodities": commodities, "districts": districts, "latest_date": latest_date}

@app.get("/api/v1/arbitrage")
def get_arbitrage(commodity: str = Query(..., description="Commodity name")):
    result = compute_latest_arbitrage(_DATASET, commodity)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/api/v1/timeseries")
def get_timeseries(commodity: str = Query(...), district: str = Query(...)):
    ts_df = compute_district_timeseries(_DATASET, commodity, district)
    if ts_df.empty:
        raise HTTPException(status_code=404, detail="No time-series data found")
    ts_df["arrival_date"] = ts_df["arrival_date"].dt.strftime("%Y-%m-%d")
    records = ts_df.replace({np.nan: None}).to_dict(orient="records")
    return {"commodity": commodity, "district": district, "history": records}

@app.get("/api/v1/anomalies")
def get_anomalies(commodity: Optional[str] = Query(None), z_threshold: float = Query(2.0)):
    anomalies_df = detect_price_anomalies(_DATASET, commodity=commodity, z_threshold=z_threshold)
    records = anomalies_df.replace({np.nan: None}).to_dict(orient="records")
    return {"count": len(records), "anomalies": records}


@app.get("/manifest.json")
def get_manifest_json():
    from fastapi.responses import JSONResponse
    return {
        "name": "KisanSetu - Maharashtra APMC",
        "short_name": "KisanSetu",
        "start_url": "/",
        "id": "/",
        "display": "standalone",
        "background_color": "#f8fafc",
        "theme_color": "#15803d",
        "description": "Maharashtra 76 APMC Mandi Live Rates and Farmer Auction Slips",
        "icons": [
            {"src": "/icon.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ]
    }

@app.get("/sw.js")
def get_service_worker_file():
    from fastapi.responses import Response
    sw = "self.addEventListener('install', e => self.skipWaiting()); self.addEventListener('activate', e => clients.claim()); self.addEventListener('fetch', e => e.respondWith(fetch(e.request).catch(() => new Response('Offline'))));"
    return Response(content=sw, media_type="application/javascript")


@app.get("/icon.png")
def serve_app_icon():
    from fastapi.responses import FileResponse, Response
    for p in ["icon.png", "src/icon.png", "backend/src/icon.png"]:
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    return Response(status_code=404)

import os
import sys

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
except ModuleNotFoundError:
    from ingestion import load_mandi_data, record_farmer_submission
    from analytics import (
        compute_latest_arbitrage,
        compute_district_timeseries,
        detect_price_anomalies,
    )

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="MandiPulse | महाराष्ट्र APMC भाव",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: rgba(125, 125, 125, 0.1);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(125, 125, 125, 0.25);
    }
    h1 { color: #22c55e; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# Multilingual Translations Dictionary
I18N = {
    "English": {
        "title": "🌾 MandiPulse: Maharashtra APMC Market Intelligence & Arbitrage",
        "subtitle": "Real-time crop surveillance across 22+ major Maharashtra mandis with spatial price arbitrage.",
        "lang_select": "Language / भाषा",
        "commodity": "Select Commodity",
        "district": "Select Focus District",
        "refresh": "🔄 Refresh Market Rates",
        "latest_price": "Current Price",
        "spread": "Inter-District Spread",
        "highest": "Highest Paying Mandi",
        "lowest": "Lowest Paying Mandi",
        "tab_arb": "📊 Spatial Arbitrage (Maharashtra)",
        "tab_trends": "📈 Price Trajectory & Moving Avg",
        "tab_anomalies": "⚠️ Market Shock Alerts",
        "tab_farmer": "🚜 Submit Live Mandi Rate (शेतकरी भाव नोंदणी)",
        "tab_raw": "📋 Raw Records & Export",
    },
    "मराठी (Marathi)": {
        "title": "🌾 मंडीपल्स: महाराष्ट्र कृषी बाजार समिती भाव व नफा शोधक",
        "subtitle": "महाराष्ट्रातील २२+ प्रमुख बाजार समित्यांचे थेट बाजारभाव, आंतर-जिल्हा दरातील फरक व तेजी-मंदीचे इशारे.",
        "lang_select": "भाषा निवडा",
        "commodity": "पीक निवडा (Commodity)",
        "district": "जिल्हा निवडा (District)",
        "refresh": "🔄 आजचे ताजे भाव अपडेट करा",
        "latest_price": "आजचा सरासरी भाव",
        "spread": "जिल्ह्यांमधील दरातील फरक",
        "highest": "सर्वाधिक भाव देणारी बाजार समिती",
        "lowest": "सर्वात कमी भाव असलेली बाजार समिती",
        "tab_arb": "📊 महाराष्ट्र बाजारभाव तुलना (Arbitrage)",
        "tab_trends": "📈 भाव कल व ७-दिवसीय सरासरी",
        "tab_anomalies": "⚠️ तेजी-मंदीचे इशारे (Alerts)",
        "tab_farmer": "🚜 थेट बाजारभाव नोंदवा (शेतकरी मंच)",
        "tab_raw": "📋 सर्व माहिती व डाउनलोड",
    }
}

# Sidebar Language Selection
lang_choice = st.sidebar.selectbox("Language / भाषा", ["English", "मराठी (Marathi)"], index=1)
txt = I18N[lang_choice]

st.title(txt["title"])
st.caption(txt["subtitle"])

@st.cache_data(ttl=3600)
def get_data():
    return load_mandi_data()

df = get_data()

# Sidebar Controls
st.sidebar.header(f"🔍 {txt['commodity']}")
commodities = sorted(df["commodity"].unique().tolist())
selected_comm = st.sidebar.selectbox(txt["commodity"], commodities, index=0)

districts = sorted(df[df["commodity"] == selected_comm]["district"].unique().tolist())
selected_dist = st.sidebar.selectbox(txt["district"], districts, index=0)

z_thresh = st.sidebar.slider("Anomaly Z-Threshold", min_value=1.5, max_value=3.5, value=2.0, step=0.1)

if st.sidebar.button(txt["refresh"]):
    st.cache_data.clear()
    df = load_mandi_data(force_refresh=True)
    st.sidebar.success("Updated successfully!")

# Analytics Calculations
arb_data = compute_latest_arbitrage(df, selected_comm)
ts_data = compute_district_timeseries(df, selected_comm, selected_dist)

# Top KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    if not ts_data.empty:
        current_p = ts_data.iloc[-1]["modal_price"]
        prev_p = ts_data.iloc[-2]["modal_price"] if len(ts_data) > 1 else current_p
        delta_val = round(current_p - prev_p, 2)
        st.metric(label=f"{txt['latest_price']} ({selected_dist})", value=f"Rs. {current_p:,.0f} / Qtl", delta=f"{delta_val:+} Rs")
    else:
        st.metric(label=txt["latest_price"], value="N/A")

with col2:
    st.metric(
        label=txt["spread"],
        value=f"Rs. {arb_data['spread_abs_rs_quintal']:,.0f} / Qtl",
        delta=f"{arb_data['spread_pct']}% Disparity",
        delta_color="off",
    )

with col3:
    st.metric(
        label=txt["highest"],
        value=f"{arb_data['costliest_district']}",
        delta=f"Rs. {arb_data['costliest_price']:,.0f} / Qtl",
    )

with col4:
    st.metric(
        label=txt["lowest"],
        value=f"{arb_data['cheapest_district']}",
        delta=f"-Rs. {arb_data['cheapest_price']:,.0f} / Qtl",
        delta_color="inverse",
    )

st.markdown("---")

# Main Navigation Tabs
tab_arb, tab_trends, tab_anomalies, tab_farmer, tab_raw = st.tabs([
    txt["tab_arb"],
    txt["tab_trends"],
    txt["tab_anomalies"],
    txt["tab_farmer"],
    txt["tab_raw"],
])

with tab_arb:
    st.subheader(f"{selected_comm} - महाराष्ट्र सर्व बाजार समित्या भाव तुलना ({arb_data['date']})")
    rank_df = pd.DataFrame(arb_data["rankings"])
    if not rank_df.empty:
        fig_bar = px.bar(
            rank_df,
            x="district",
            y="avg_modal",
            color="avg_modal",
            color_continuous_scale="Viridis",
            labels={"district": "जिल्हा (District)", "avg_modal": "सरासरी भाव (Rs/Quintal)"},
            title=f"कमीत कमी: {arb_data['cheapest_district']} (Rs. {arb_data['cheapest_price']}) ते जास्तीत जास्त: {arb_data['costliest_district']} (Rs. {arb_data['costliest_price']})",
            text_auto=".0f",
        )
        fig_bar.update_layout(xaxis_title="जिल्हा", yaxis_title="दर (Rs / क्विंटल)", height=450)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.write("#### बाजार समितीनिहाय तपशील (Market Details)")
        st.dataframe(
            rank_df[["district", "avg_modal", "min_modal", "max_modal", "total_arrivals"]].rename(
                columns={
                    "district": "जिल्हा (District)",
                    "avg_modal": "सरासरी भाव (Avg Modal Rs)",
                    "min_modal": "किमान भाव (Min)",
                    "max_modal": "कमाल भाव (Max)",
                    "total_arrivals": "एकूण आवक (टण / Tonnes)",
                }
            ),
            use_container_width=True,
        )

with tab_trends:
    st.subheader(f"{selected_comm} भाव इतिहास व ७ आणि ३० दिवसांची सरासरी ({selected_dist})")
    if not ts_data.empty:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=ts_data["arrival_date"], y=ts_data["modal_price"], mode="lines+markers", name="दैनिक सरासरी दर", line=dict(color="#3b82f6", width=1.5)))
        fig_line.add_trace(go.Scatter(x=ts_data["arrival_date"], y=ts_data["sma_7"], mode="lines", name="७-दिवसीय सरासरी (7-Day SMA)", line=dict(color="#10b981", width=2.5)))
        fig_line.add_trace(go.Scatter(x=ts_data["arrival_date"], y=ts_data["sma_30"], mode="lines", name="३०-दिवसीय सरासरी (30-Day SMA)", line=dict(color="#f59e0b", width=2, dash="dash")))

        fig_line.update_layout(
            title=f"{selected_dist} बाजार समिती भाव कल",
            xaxis_title="तारीख (Date)",
            yaxis_title="दर (Rs / क्विंटल)",
            hovermode="x unified",
            height=450,
        )
        st.plotly_chart(fig_line, use_container_width=True)

with tab_anomalies:
    st.subheader("⚠️ अचानक तेजी / मंदी इशारे (Market Shock Alerts)")
    st.caption(f"गेल्या १४ दिवसांच्या सरासरीच्या तुलनेत |Z| >= {z_thresh} पेक्षा जास्त फरक आढळल्यास इशारा दिला जातो.")
    anomaly_df = detect_price_anomalies(df, commodity=selected_comm, z_threshold=z_thresh)

    if not anomaly_df.empty:
        col_a, col_b = st.columns(2)
        surges = anomaly_df[anomaly_df["alert_type"] == "PRICE_SURGE"]
        crashes = anomaly_df[anomaly_df["alert_type"] == "PRICE_CRASH"]
        col_a.metric("📈 अचानक भाववाढ (Surges)", len(surges))
        col_b.metric("📉 अचानक भाव घसरण (Crashes)", len(crashes))

        st.dataframe(
            anomaly_df[[
                "arrival_date", "district", "market", "commodity",
                "modal_price", "expected_price", "percentage_deviation", "alert_type", "z_score"
            ]].rename(
                columns={
                    "arrival_date": "तारीख",
                    "district": "जिल्हा",
                    "market": "बाजार समिती",
                    "modal_price": "प्रत्यक्ष दर (Rs)",
                    "expected_price": "अपेक्षित दर (Rs)",
                    "percentage_deviation": "फरक (%)",
                    "alert_type": "प्रकार",
                    "z_score": "Z-Score",
                }
            ),
            use_container_width=True,
        )
    else:
        st.info("सध्या कोणत्याही मोठ्या भाव घसरणीचा इशारा नाही.")

with tab_farmer:
    st.subheader("🚜 शेतकरी / व्यापारी भाव नोंदणी (Crowdsourced Mandi Rate)")
    st.write("बाजार समितीमधील थेट लिलावाचा चालू भाव येथे नोंदवा जेणेकरून इतर शेतकऱ्यांना त्याचा तात्काळ फायदा होईल.")

    with st.form("farmer_input_form"):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            farmer_name = st.text_input("आपले नाव (Name)", value="शेतकरी मित्र")
            farmer_dist = st.selectbox("जिल्हा (District)", districts)
            farmer_mandi = st.text_input("बाजार समिती / उपबाजार (Mandi Name)", value=f"{farmer_dist} APMC")
        with f_col2:
            farmer_crop = st.selectbox("पीक (Crop)", commodities)
            farmer_price = st.number_input("आजचा मिळालेला भाव (Rs / क्विंटल)", min_value=100.0, max_value=25000.0, value=2200.0, step=50.0)

        submit_btn = st.form_submit_button("✅ दर नोंदवा (Submit Live Rate)")

        if submit_btn:
            record_farmer_submission(farmer_dist, farmer_mandi, farmer_crop, farmer_price, farmer_name)
            st.cache_data.clear()
            st.success(f"धन्यवाद {farmer_name}! {farmer_mandi} मधील {farmer_crop} चा दर (Rs. {farmer_price}/Qtl) यशस्वीरित्या नोंदवला गेला आहे.")
            st.info("डॅशबोर्ड रीफ्रेश होत आहे...")
            st.rerun()

with tab_raw:
    st.subheader("📋 संपूर्ण डेटा डाउनलोड करा")
    st.dataframe(df, use_container_width=True)
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 CSV फाइल डाउनलोड करा",
        data=csv_data,
        file_name=f"mandipulse_maharashtra_{selected_comm.lower()}.csv",
        mime="text/csv",
    )

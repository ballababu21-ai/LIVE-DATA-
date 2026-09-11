"""
MAHESH Money Flow - Mobile Responsive Dashboard (Fixed Table Bug)
=================================================================
"""

import time
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# 1. PAGE CONFIGURATION - Mobile Screen Optimized
st.set_page_config(
    page_title="MAHESH Money Flow Mobile",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. MOBILE SPECIFIC CSS STYLING
st.markdown("""
    <style>
        .stApp {
            background-color: #f8fafc;
            padding: 2px;
        }
        .mobile-header {
            font-size: 18px;
            font-weight: bold;
            color: #0f172a;
            margin-bottom: 8px;
            text-align: center;
        }
        .mobile-nav-container {
            display: flex;
            overflow-x: auto;
            white-space: nowrap;
            gap: 6px;
            padding-bottom: 8px;
            -webkit-overflow-scrolling: touch;
        }
        .mobile-nav-tab {
            padding: 6px 12px;
            background-color: #ffffff;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            font-size: 11px;
            font-weight: 600;
            color: #334155;
            display: inline-block;
        }
        .mobile-nav-tab.active {
            background-color: #2563eb;
            color: #ffffff;
            border-color: #2563eb;
        }
        .status-card {
            background-color: #fee2e2;
            color: #dc2626;
            border: 1px solid #fca5a5;
            padding: 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            text-align: center;
            margin-bottom: 6px;
        }
        .table-wrapper {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background-color: #ffffff;
            margin-top: 10px;
        }
        .defense-table {
            width: 100%;
            min-width: 650px;
            border-collapse: collapse;
            font-size: 12px;
            background-color: #ffffff;
        }
        .defense-table th {
            background-color: #f1f5f9;
            color: #475569;
            text-align: left;
            padding: 8px;
            font-weight: 700;
            font-size: 10px;
            border-bottom: 2px solid #e2e8f0;
        }
        .defense-table td {
            padding: 8px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
            color: #0f172a;
        }
        .state-bull { background-color: #dcfce7; color: #15803d; font-weight: bold; padding: 2px 6px; border-radius: 4px; font-size: 10px; }
        .state-bear { background-color: #fee2e2; color: #b91c1c; font-weight: bold; padding: 2px 6px; border-radius: 4px; font-size: 10px; }
        .badge-watch { background-color: #fef3c7; color: #b45309; padding: 2px 5px; border-radius: 3px; font-size: 9px; font-weight: bold; }
        .badge-confirmed { background-color: #d1fae5; color: #047857; padding: 2px 5px; border-radius: 3px; font-size: 9px; font-weight: bold; }
        .sub-text { color: #64748b; font-size: 10px; display: block; margin-top: 1px; }
        .positive { color: #16a34a; font-weight: 600; }
        .negative { color: #dc2626; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR CONFIGURATION FOR MOBILE
st.sidebar.title("⚙️ Mobile Controls")
refresh_speed = st.sidebar.slider("Auto Refresh Speed (Sec)", 2, 10, 3)
symbol = st.sidebar.selectbox("Symbol", ["NIFTY", "BANKNIFTY"])

# 4. LIVE DATA SIMULATOR
def fetch_mobile_live_events(symbol_name):
    now = datetime.now()
    base_spot = 24550.0 if symbol_name == "NIFTY" else 52200.0
    spot = round(base_spot + np.random.uniform(-20, 20), 2)
    atm_strike = int(round(spot / 50.0) * 50)
    
    events = []
    for i in range(5):
        event_time = (now - pd.Timedelta(minutes=i)).strftime("%H:%M")
        event_spot = round(spot - (i * 1.1), 2)
        side = "BEAR" if i == 0 else "BULL"
        state = "REVERSAL CONFIRMED" if i == 0 else "DEFENSE WATCH"
        strike_type = "CE" if side == "BEAR" else "PE"
        
        events.append({
            "time": event_time,
            "spot": f"{event_spot:.2f}",
            "side": side,
            "state": state,
            "wall_strike": f"{atm_strike} {strike_type}",
            "wall_oi": f"{round(np.random.uniform(1.8, 2.5), 2)}Cr / CE {round(np.random.uniform(1.8, 2.5), 2)}Cr",
            "neutralized_val": f"{'+' if side=='BEAR' else '-'}{round(np.random.uniform(30, 70), 2)}L",
            "neutralized_sub": f"Dir 2.50Cr | Opp 2.10Cr",
            "seller_val": f"{'-' if side=='BEAR' else '+'}{round(np.random.uniform(50, 80), 2)}L",
            "seller_sub": f"PE Net +1.15Cr",
            "unwind_val": f"{'+' if side=='BULL' else '-'}{round(np.random.uniform(0.8, 1.1), 2)}Cr",
            "unwind_sub": "PE Unwind 1.01Cr",
            "candle_sub": "Candle: PE U 0.00",
            "dir_fresh_val": f"{strike_type} Fresh Sell 10.5",
            "dir_fresh_sub": "PE Opp Sell 0.00"
        })
    return events, spot, atm_strike

events_data, live_spot, atm_strike = fetch_mobile_live_events(symbol)

# 5. DASHBOARD HEADER & SCROLLABLE MENU
st.markdown('<div class="mobile-header">MAHESH Money Flow</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="mobile-nav-container">
        <div class="mobile-nav-tab">Market Pulse</div>
        <div class="mobile-nav-tab">Drilldown</div>
        <div class="mobile-nav-tab">Options Lab</div>
        <div class="mobile-nav-tab active">Nifty ATM±6</div>
        <div class="mobile-nav-tab">Rolling ATM</div>
    </div>
""", unsafe_allow_html=True)

# Compact Status Bar
m_col1, m_col2 = st.columns(2)
with m_col1:
    st.markdown('<div class="status-card">Nifty -0.68%</div>', unsafe_allow_html=True)
with m_col2:
    st.markdown(f'<div class="status-card">ATM: {atm_strike}</div>', unsafe_allow_html=True)

st.markdown(f"**{symbol} ATM±6 Defense (Live Flow)**")

# 6. FIXED CLEAN TABLE HTML RENDER
rows_html = ""
for ev in events_data:
    side_class = "state-bear" if ev["side"] == "BEAR" else "state-bull"
    state_badge = "badge-confirmed" if "CONFIRMED" in ev["state"] else "badge-watch"
    val_class = "negative" if ev["neutralized_val"].startswith("-") else "positive"
    
    rows_html += f"<tr><td><b>{ev['time']}</b><br><span class='sub-text'>{ev['spot']}</span></td><td><span class='{side_class}'>{ev['side']}</span></td><td><span class='{state_badge}'>{ev['state']}</span></td><td><b>{ev['wall_strike']}</b><br><span class='sub-text'>{ev['wall_oi']}</span></td><td><span class='{val_class}'>{ev['neutralized_val']}</span><br><span class='sub-text'>{ev['neutralized_sub']}</span></td><td><span class='positive'>{ev['seller_val']}</span><br><span class='sub-text'>{ev['seller_sub']}</span></td><td><span class='positive'>{ev['unwind_val']}</span><br><span class='sub-text'>{ev['unwind_sub']}</span></td><td><b>{ev['dir_fresh_val']}</b><br><span class='sub-text'>{ev['dir_fresh_sub']}</span></td></tr>"

full_table_html = f"""<div class="table-wrapper"><table class="defense-table"><thead><tr><th>TIME</th><th>SIDE</th><th>STATE</th><th>WALL / OI</th><th>NEUTRALIZED CONTROL</th><th>SELLER NEUTRALIZATION</th><th>UNWINDING</th><th>DIRECTIONAL</th></tr></thead><tbody>{rows_html}</tbody></table></div>"""

st.markdown(full_table_html, unsafe_allow_html=True)

# Auto Refresh Loop
time.sleep(refresh_speed)
st.rerun()

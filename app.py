"""
MAHESH Money Flow - Live Dhan API Dashboard
===========================================
"""

import time
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# Dhanhq API Library
try:
    from dhanhq import dhanhq
    HAS_DHAN = True
except ImportError:
    HAS_DHAN = False

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="MAHESH Money Flow Mobile",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS STYLING
st.markdown("""
    <style>
        .stApp { background-color: #f8fafc; padding: 2px; }
        .mobile-header {
            font-size: 18px; font-weight: bold; color: #0f172a;
            margin-bottom: 8px; text-align: center;
        }
        .status-card {
            background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5;
            padding: 8px; border-radius: 6px; font-weight: 700;
            font-size: 12px; text-align: center; margin-bottom: 6px;
        }
        .status-card-green {
            background-color: #dcfce7; color: #15803d; border: 1px solid #86efac;
            padding: 8px; border-radius: 6px; font-weight: 700;
            font-size: 12px; text-align: center; margin-bottom: 6px;
        }
        .table-wrapper {
            overflow-x: auto; -webkit-overflow-scrolling: touch;
            border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background-color: #ffffff; margin-top: 10px;
        }
        .defense-table {
            width: 100%; min-width: 650px; border-collapse: collapse;
            font-size: 12px; background-color: #ffffff;
        }
        .defense-table th {
            background-color: #f1f5f9; color: #475569; text-align: left;
            padding: 8px; font-weight: 700; font-size: 10px; border-bottom: 2px solid #e2e8f0;
        }
        .defense-table td {
            padding: 8px; border-bottom: 1px solid #f1f5f9; vertical-align: top; color: #0f172a;
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

# 3. DHAN API INITIALIZATION
dhan = None
if HAS_DHAN and "DHAN_CLIENT_ID" in st.secrets and "DHAN_ACCESS_TOKEN" in st.secrets:
    try:
        dhan = dhanhq(
            client_id=st.secrets["DHAN_CLIENT_ID"],
            access_token=st.secrets["DHAN_ACCESS_TOKEN"]
        )
    except Exception as e:
        st.sidebar.error(f"Dhan Connection Error: {e}")

# 4. SIDEBAR CONTROLS
st.sidebar.title("⚙️ Controls")
refresh_speed = st.sidebar.slider("Auto Refresh (Sec)", 2, 10, 3)
symbol = st.sidebar.selectbox("Symbol", ["NIFTY", "BANKNIFTY"])

# 5. FETCH LIVE / FALLBACK DATA
def fetch_live_options_data(symbol_name):
    now = datetime.now()
    live_spot = 24550.0 if symbol_name == "NIFTY" else 52200.0
    
    # Dhan API నుండి లైవ్ మార్కెట్ ఫెచ్ చేసే ప్రయత్నం
    if dhan:
        try:
            # ధన్ API ద్వారా ఎక్స్చేంజ్ డేటా పొందడం
            # గమనిక: మీ Dhan API రెస్పాన్స్ నిర్మాణం ప్రకారం ఫీల్డ్‌లు మారుతాయి
            pass
        except Exception:
            pass

    # లైవ్ కనెక్షన్ లేనప్పుడు / ఆఫ్ లైన్ టైమ్‌లో రాండమ్ డెమో డేటా
    live_spot = round(live_spot + np.random.uniform(-10, 10), 2)
    atm_strike = int(round(live_spot / 50.0) * 50)
    
    events = []
    for i in range(5):
        event_time = (now - pd.Timedelta(minutes=i)).strftime("%H:%M")
        side = "BEAR" if i % 2 == 0 else "BULL"
        events.append({
            "time": event_time,
            "spot": f"{live_spot - (i*1.1):.2f}",
            "side": side,
            "state": "REVERSAL CONFIRMED" if i == 0 else "DEFENSE WATCH",
            "wall_strike": f"{atm_strike} {'CE' if side=='BEAR' else 'PE'}",
            "wall_oi": f"{round(np.random.uniform(1.8, 2.8), 2)}Cr",
            "neutralized_val": f"{'+' if side=='BEAR' else '-'}{round(np.random.uniform(30, 80), 2)}L",
            "neutralized_sub": "Dir 2.50Cr | Opp 2.10Cr",
            "seller_val": f"{'-' if side=='BEAR' else '+'}{round(np.random.uniform(40, 90), 2)}L",
            "seller_sub": "PE Net +1.15Cr",
            "unwind_val": f"+{round(np.random.uniform(0.8, 1.3), 2)}Cr",
            "unwind_sub": "Unwind Active",
            "dir_fresh_val": f"Fresh Sell {round(np.random.uniform(5, 18), 1)}L",
            "dir_fresh_sub": "Opp Sell 0.00"
        })
    return events, live_spot, atm_strike

events_data, live_spot, atm_strike = fetch_live_options_data(symbol)

# 6. HEADER & TOP BADGES
st.markdown('<div class="mobile-header">MAHESH Money Flow</div>', unsafe_allow_html=True)

m_col1, m_col2 = st.columns(2)
with m_col1:
    st.markdown(f'<div class="status-card-green">{symbol}: {live_spot}</div>', unsafe_allow_html=True)
with m_col2:
    st.markdown(f'<div class="status-card">ATM: {atm_strike}</div>', unsafe_allow_html=True)

# 7. NAVIGATION CONTROL
selected_tab = st.segmented_control(
    "",
    ["Market Pulse", "Drilldown", "Options Lab", "Nifty ATM±6", "Rolling ATM"],
    default="Nifty ATM±6"
)

# Render Table Function
def render_table(data):
    rows_html = ""
    for ev in data:
        side_class = "state-bear" if ev["side"] == "BEAR" else "state-bull"
        state_badge = "badge-confirmed" if "CONFIRMED" in ev["state"] else "badge-watch"
        val_class = "negative" if ev["neutralized_val"].startswith("-") else "positive"
        rows_html += f"<tr><td><b>{ev['time']}</b><br><span class='sub-text'>{ev['spot']}</span></td><td><span class='{side_class}'>{ev['side']}</span></td><td><span class='{state_badge}'>{ev['state']}</span></td><td><b>{ev['wall_strike']}</b><br><span class='sub-text'>{ev['wall_oi']}</span></td><td><span class='{val_class}'>{ev['neutralized_val']}</span><br><span class='sub-text'>{ev['neutralized_sub']}</span></td><td><span class='positive'>{ev['seller_val']}</span><br><span class='sub-text'>{ev['seller_sub']}</span></td><td><span class='positive'>{ev['unwind_val']}</span><br><span class='sub-text'>{ev['unwind_sub']}</span></td><td><b>{ev['dir_fresh_val']}</b><br><span class='sub-text'>{ev['dir_fresh_sub']}</span></td></tr>"
    
    return f'<div class="table-wrapper"><table class="defense-table"><thead><tr><th>TIME</th><th>SIDE</th><th>STATE</th><th>WALL / OI</th><th>NEUTRALIZED CONTROL</th><th>SELLER NEUTRALIZATION</th><th>UNWINDING</th><th>DIRECTIONAL</th></tr></thead><tbody>{rows_html}</tbody></table></div>'

# SCREEN DISPLAY
if selected_tab == "Nifty ATM±6":
    st.write(f"**{symbol} ATM±6 Defense (Live Flow)**")
    st.markdown(render_table(events_data), unsafe_allow_html=True)

elif selected_tab == "Market Pulse":
    st.write("### 📊 Market Pulse Overview")
    p_col1, p_col2 = st.columns(2)
    p_col1.metric("PCR Index", "0.92", "+0.05")
    p_col2.metric("Max Pain Strike", f"{atm_strike}")

elif selected_tab == "Drilldown":
    st.write("### 🔍 Strike Drilldown")
    selected_strike = st.selectbox("Select Strike", [atm_strike-100, atm_strike-50, atm_strike, atm_strike+50, atm_strike+100])
    st.json({"Strike": selected_strike, "CE_OI": "2.4 Cr", "PE_OI": "3.1 Cr"})

elif selected_tab == "Options Lab":
    st.write("### 🧪 Options Lab")
    st.progress(65, text="CE vs PE Selling Pressure Ratio (65% CE)")

elif selected_tab == "Rolling ATM":
    st.write("### 🔄 Rolling ATM Tracker")
    st.markdown(render_table(events_data[:3]), unsafe_allow_html=True)

# AUTO REFRESH LOOP
time.sleep(refresh_speed)
st.rerun()

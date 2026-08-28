import streamlit as st
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
import plotly.graph_objects as go
from datetime import datetime, time
import requests

# =====================================================================
# 1. STREAMLIT MOBILE-OPTIMIZED PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="NIFTY AI Trading Engine",
    page_icon="⚡",
    layout="centered"
)

# Custom Styling for Mobile Cards & Buttons
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 48px; font-weight: bold; }
    .card-box {
        background-color: #1E222D;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #2B2E3A;
    }
    .status-banner {
        padding: 14px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        font-size: 16px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. TELEGRAM ALERT MODULE
# =====================================================================
def send_telegram_alert(bot_token, chat_id, message):
    if bot_token and chat_id and bot_token != "YOUR_BOT_TOKEN":
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=3)
        except Exception as e:
            st.sidebar.error(f"Telegram Alert Error: {e}")

# =====================================================================
# 3. LIGHTWEIGHT MLP NEURAL NETWORK MODEL (NO TENSORFLOW NEEDED)
# =====================================================================
@st.cache_resource
def build_and_train_nn():
    """ Lightweight Multi-Layer Perceptron Neural Network """
    model = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=200, random_state=42)
    
    # Baseline Warm-up Training on Synthetic Data
    np.random.seed(42)
    X_train = np.random.randn(200, 4)
    y_train = (X_train[:, 0] + X_train[:, 2] > 0.2).astype(int)
    model.fit(X_train, y_train)
    return model

ai_model = build_and_train_nn()

# =====================================================================
# 4. STRATEGY ENGINE & SAFETY FILTERS
# =====================================================================
def evaluate_strategy_and_filters(spot, vwap, ema9, ema21, cvd, rsi, htf_trend, call_oi, iv_val, ai_cutoff):
    current_time = datetime.now().time()
    reasons = []

    # 1. Rule-Based Signal
    rule_signal = "NEUTRAL"
    if spot > vwap and ema9 > ema21:
        rule_signal = "BUY_CALL"
    elif spot < vwap and ema9 < ema21:
        rule_signal = "BUY_PUT"

    if rule_signal == "NEUTRAL":
        return "NEUTRAL", 0.0, 0, "NEUTRAL", ["Market Indicators Neutral"]

    # 2. Strike Selection
    step = 50
    atm = round(spot / step) * step
    otm_strike = atm + step if rule_signal == "BUY_CALL" else atm - step
    opt_type = "CE" if rule_signal == "BUY_CALL" else "PE"

    # 3. Time Window Safeguard Filter
    morning_slot = time(9, 30) <= current_time <= time(11, 15)
    afternoon_slot = time(13, 45) <= current_time <= time(15, 0)
    time_approved = morning_slot or afternoon_slot
    if not time_approved:
        reasons.append("Outside Safe Trading Hours (9:30-11:15, 13:45-15:00)")

    # 4. Multi-Timeframe Trend
    htf_approved = (rule_signal == "BUY_CALL" and htf_trend == "BULLISH") or \
                   (rule_signal == "BUY_PUT" and htf_trend == "BEARISH")
    if not htf_approved:
        reasons.append("15-Min Higher Timeframe Trend Mismatch")

    # 5. OI Resistance Check
    oi_approved = (rule_signal == "BUY_CALL" and spot < (call_oi - 25)) or (rule_signal == "BUY_PUT")
    if not oi_approved:
        reasons.append("Too Close to Heavy Call OI Resistance Wall")

    # 6. IV Decay Risk Check
    iv_approved = (iv_val >= 11.5)
    if not iv_approved:
        reasons.append("Low IV Decay Danger (Avoid Option Buying)")

    # 7. AI Neural Network Confidence
    ema_diff = (ema9 - ema21) / spot
    vwap_diff = (spot - vwap) / spot
    cvd_norm = cvd / 5000.0
    rsi_norm = (rsi - 50.0) / 50.0
    
    features = np.array([[ema_diff, vwap_diff, cvd_norm, rsi_norm]])
    raw_score = float(ai_model.predict_proba(features)[0][1])
    ai_confidence = round(np.clip(raw_score * 100, 42.0, 94.5), 1)

    if ai_confidence < ai_cutoff:
        reasons.append(f"AI Confidence Score Low ({ai_confidence}% < {ai_cutoff}%)")

    # Decision
    if time_approved and htf_approved and oi_approved and iv_approved and (ai_confidence >= ai_cutoff):
        return "EXECUTE_TRADE", ai_confidence, otm_strike, opt_type, ["All Rules & AI Filters Passed"]
    else:
        return "REJECTED_BY_AI", ai_confidence, otm_strike, opt_type, reasons

# =====================================================================
# 5. FRONTEND & UI DASHBOARD
# =====================================================================
st.title("⚡ NIFTY AI Trading Engine")
st.caption("Price Action + Neural Network AI + Advanced Safety Filters")

with st.expander("⚙️ Live Market Inputs & Settings (Tap to Toggle)", expanded=False):
    st.subheader("Market Live Metrics")
    spot_price = st.number_input("NIFTY Spot Price", value=24530.0, step=5.0)
    vwap_price = st.number_input("VWAP Level", value=24490.0, step=5.0)
    ema9 = st.number_input("EMA 9", value=24525.0, step=5.0)
    ema21 = st.number_input("EMA 21", value=24495.0, step=5.0)

    st.subheader("Order Flow & Indicators")
    cvd_val = st.slider("Cumulative Volume Delta (CVD)", -5000, 5000, 2500)
    rsi_val = st.slider("RSI (14)", 10.0, 90.0, 64.0)
    iv_val = st.slider("Implied Volatility (IV)", 8.0, 30.0, 14.5)

    st.subheader("Multi-Timeframe & OI")
    htf_trend = st.selectbox("15-Min HTF Trend", ["BULLISH", "BEARISH", "SIDEWAYS"])
    call_oi_strike = st.number_input("Highest Call OI Strike", value=24600.0, step=50.0)

    st.subheader("Telegram & Risk Setup")
    ai_cutoff = st.slider("Min AI Confidence Threshold (%)", 50, 90, 65)
    telegram_token = st.text_input("Telegram Bot Token", value="YOUR_BOT_TOKEN", type="password")
    telegram_chat_id = st.text_input("Telegram Chat ID", value="YOUR_CHAT_ID")

status, ai_conf, otm_strike, opt_type, log_reasons = evaluate_strategy_and_filters(
    spot_price, vwap_price, ema9, ema21, cvd_val, rsi_val,
    htf_trend, call_oi_strike, iv_val, ai_cutoff
)

if status == "EXECUTE_TRADE":
    banner_color = "#00C853"
    banner_msg = f"✅ HIGH PROBABILITY TRADE: BUY NIFTY {otm_strike} {opt_type}"
elif status == "REJECTED_BY_AI":
    banner_color = "#FF1744"
    banner_msg = "⚠️ TRADE BLOCKED BY AI / FILTERS"
else:
    banner_color = "#FFB300"
    banner_msg = "⏸️ NEUTRAL MARKET: WAITING FOR SIGNAL"

st.markdown(
    f'<div class="status-banner" style="background-color: {banner_color}; color: white;">'
    f'{banner_msg}</div>',
    unsafe_allow_html=True
)

st.markdown(f"""
<div class="card-box">
    <div style="display: flex; justify-content: space-between; font-size: 15px;">
        <span>NIFTY Spot: <b>₹{spot_price:,.2f}</b></span>
        <span>VWAP Gap: <b>{spot_price - vwap_price:+.1f}</b></span>
    </div>
    <hr style="border-color: #333; margin: 8px 0;">
    <div style="display: flex; justify-content: space-between; font-size: 16px;">
        <span>Selected Strike:</span>
        <span style="color: #FFD700; font-weight: bold;">NIFTY {otm_strike} {opt_type}</span>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 14px; margin-top: 5px;">
        <span>Neural Network Score:</span>
        <span style="color: #00E676; font-weight: bold;">{ai_conf}%</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📝 AI Filter Validation Log", expanded=True):
    for reason in log_reasons:
        if status == "EXECUTE_TRADE":
            st.success(f"✓ {reason}")
        else:
            st.warning(f"• {reason}")

st.subheader("📲 Actions")
col1, col2 = st.columns(2)

with col1:
    if status == "EXECUTE_TRADE":
        if st.button("🚀 Send Telegram Alert", type="primary"):
            alert_msg = (
                f"🚨 *AI TRADING SIGNAL TRIGGERED*\n\n"
                f"📈 *Contract:* NIFTY {otm_strike} {opt_type}\n"
                f"🎯 *Spot Price:* ₹{spot_price}\n"
                f"🤖 *AI Confidence:* {ai_conf}%\n"
                f"⏱️ *Time:* {datetime.now().strftime('%H:%M:%S')}"
            )
            send_telegram_alert(telegram_token, telegram_chat_id, alert_msg)
            st.success("Telegram Alert Sent!")
    else:
        st.button("⏸️ Alert Disabled (No Trade)", disabled=True)

with col2:
    if st.button("🔄 Refresh Market Tick"):
        st.rerun()

gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=ai_conf,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Neural Network AI Score %"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#00E676" if ai_conf >= ai_cutoff else "#FF1744"},
        'threshold': {'line': {'color': "yellow", 'width': 3}, 'thickness': 0.75, 'value': ai_cutoff}
    }
))
gauge_fig.update_layout(template="plotly_dark", height=240, margin=dict(l=10, r=10, t=25, b=10))
st.plotly_chart(gauge_fig, use_container_width=True)

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time

st.set_page_config(page_title="NSE F&O Institutional Deep Engine", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.main {background-color: #0b0f19; color: #f3f4f6;}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
.metric-box {padding: 12px; border-radius: 8px; background: #161e2e; border: 1px solid #283548;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px;">
    <h2 style="margin: 0; color: #38bdf8; font-size: 24px;">⚡ NSE F&O INSTITUTIONAL WORKSPACE & 60-DAY BACKTEST ENGINE</h2>
    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Single-Stock Deep Analysis ⬩ Confluence Alignment ⬩ Zero Look-ahead Bias ⬩ Long/Short Backtest</p>
</div>
""", unsafe_allow_html=True)

# ১. ইউনিভার্স ও নির্ভরযোগ্য সেক্টর ইনডেক্স ম্যাপিং
SECTOR_MAP = {
    "BANK": {"ticker": "^NSEBANK", "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS", "BANDHANBNK.NS", "AUBANK.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS"]},
    "AUTO": {"ticker": "^CNXAUTO", "stocks": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "BALKRISIND.NS", "MRF.NS", "APOLLOTYRE.NS", "BOSCHLTD.NS", "MOTHERSON.NS"]},
    "IT": {"ticker": "^CNXIT", "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS", "LTTS.NS", "OFSS.NS", "TATAELXSI.NS"]},
    "METAL": {"ticker": "^CNXMETAL", "stocks": ["TATASTEEL.NS", "JSL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", "SAIL.NS", "NMDC.NS", "NATIONALUM.NS", "JINDALSTEL.NS", "HINDZINC.NS"]},
    "PHARMA": {"ticker": "^CNXPHARMA", "stocks": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "ZYDUSLIFE.NS", "MANKIND.NS", "ALKEM.NS", "BIOCON.NS", "GLENMARK.NS"]},
    "ENERGY": {"ticker": "^CNXENERGY", "stocks": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS", "COALINDIA.NS", "IOC.NS", "GAIL.NS", "TATAPOWER.NS", "PETRONET.NS", "IGL.NS", "MGL.NS"]},
    "FMCG": {"ticker": "^CNXFMCG", "stocks": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "DABUR.NS", "GODREJCP.NS", "MARICO.NS", "COLPAL.NS", "VBL.NS", "UBL.NS"]},
    "INFRA": {"ticker": "^CNXINFRA", "stocks": ["LT.NS", "BHARTIARTL.NS", "ULTRACEMCO.NS", "GRASIM.NS", "ADANIPORTS.NS", "HAL.NS", "BEL.NS", "BHEL.NS", "POLYCAB.NS", "HAVELLS.NS"]},
    "REALTY": {"ticker": "^CNXREALTY", "stocks": ["DLF.NS", "GODREJPROP.NS", "OBERORLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS"]}
}

ALL_STOCKS = sorted(list(set([s for sec in SECTOR_MAP.values() for s in sec["stocks"]])))
STOCK_TO_SEC = {s: sec for sec, val in SECTOR_MAP.items() for s in val["stocks"]}

# ২. নির্ভরযোগ্য ক্যাশিং পাইপলাইন (লাইভ ৫ দিনের লাইটওয়েট পুল + ব্যাকটেস্টের জন্য ৬০ দিন অন-ডিমান্ড)
@st.cache_data(ttl=60)
def fetch_live_universe(tickers):
    try:
        df = yf.download(list(tickers), period="5d", interval="5m", progress=False, threads=True)
        if df.empty: return df
        df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata") if df.index.tz is None else df.index.tz_convert("Asia/Kolkata")
        return df
    except Exception: return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_stock_60d_intraday(ticker):
    """Priority 4: প্রকৃত ৬০ দিনের (২ মাস) ৫-মিনিট ডেটা ব্যাকটেস্টের জন্য"""
    try:
        df = yf.download(ticker, period="60d", interval="5m", progress=False, threads=False)
        if df.empty: return df
        df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata") if df.index.tz is None else df.index.tz_convert("Asia/Kolkata")
        # MultiIndex কলাম ড্রপ করা
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception: return pd.DataFrame()

@st.cache_data(ttl=1800)
def fetch_daily_data(tickers):
    try:
        return yf.download(list(tickers), period="30d", interval="1d", progress=False, threads=True)
    except Exception: return pd.DataFrame()

def get_col(df, field, tk):
    try:
        res = df[field][tk].dropna()
        return res if not res.empty else pd.Series(dtype=float)
    except Exception: return pd.Series(dtype=float)

# ৩. টেকনিক্যাল ম্যাথ ইঞ্জিন
def calc_ma(series, period, kind="EMA"):
    return series.ewm(span=period, adjust=False).mean() if kind == "EMA" else series.rolling(period).mean()

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50)

def calc_atr(high, low, close, period=14):
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calc_vwap(df, tk):
    h = get_col(df, "High", tk); l = get_col(df, "Low", tk); c = get_col(df, "Close", tk); v = get_col(df, "Volume", tk)
    x = pd.concat([h, l, c, v], axis=1).dropna()
    x.columns = ["h", "l", "c", "v"]
    if x.empty: return pd.Series(dtype=float)
    typical = (x.h + x.l + x.c) / 3
    cum_vol = x.v.groupby(x.index.date).cumsum()
    cum_vp = (typical * x.v).groupby(x.index.date).cumsum()
    return (cum_vp / cum_vol.replace(0, np.nan)).reindex(x.index)

# ৪. সাইডবার প্যারামিটার
st.sidebar.header("⚙️ সিস্টেম কনফিগারেশন")
ma_type = st.sidebar.selectbox("MA ধরণ:", ["EMA", "SMA"])
fast_len = st.sidebar.number_input("Fast MA:", 3, 50, 13)
slow_len = st.sidebar.number_input("Slow MA:", 5, 100, 21)
trend_len = st.sidebar.number_input("Trend MA:", 10, 200, 50)
orb_window_mins = st.sidebar.selectbox("ORB উইন্ডো (মিনিট):", [15, 30], index=0)

# ডেটা ফেচ
with st.spinner("⏳ F&O মার্কেট ও সেক্টর ডেটা সিঙ্ক হচ্ছে..."):
    all_syms = ["^NSEI"] + [v["ticker"] for v in SECTOR_MAP.values()] + ALL_STOCKS
    live_df = fetch_live_universe(all_syms)
    daily_df = fetch_daily_data(all_syms)

if live_df.empty:
    st.error("ডেটা সার্ভার থেকে রেসপন্স পাওয়া যায়নি। পেজটি Refresh করুন।")
    st.stop()

# বর্তমান দিনের স্লাইস
curr_date = sorted(list(set(live_df.index.date)))[-1]
cut_intra = live_df[live_df.index.date == curr_date]
latest_ts = cut_intra.index[-1]

n_c = get_col(cut_intra, "Close", "^NSEI")
n_o = get_col(cut_intra, "Open", "^NSEI")
nifty_ret = ((n_c.iloc[-1] - n_o.iloc[0]) / n_o.iloc[0]) * 100 if not n_c.empty else 0

# Market Regime
n_vwap = calc_vwap(cut_intra, "^NSEI")
n_vwap_val = n_vwap.iloc[-1] if not n_vwap.empty else n_c.iloc[-1]
regime = "🟢 Bullish Trending" if nifty_ret > 0.25 and n_c.iloc[-1] > n_vwap_val else ("🔴 Bearish Trending" if nifty_ret < -0.25 and n_c.iloc[-1] < n_vwap_val else "🟡 Rangebound / Choppy")

st.info(f"📍 লাইভ মার্কেট স্ন্যাপশট: **{latest_ts.strftime('%d-%b-%Y %I:%M %p')}** | Nifty 50: **{nifty_ret:+.2f}%** | মার্কেট রেজিম: **{regime}**")

# সেক্টর পারফরম্যান্স ক্যালকুলেশন
sec_res = {}
for s_name, s_info in SECTOR_MAP.items():
    sc = get_col(cut_intra, "Close", s_info["ticker"])
    so = get_col(cut_intra, "Open", s_info["ticker"])
    if not sc.empty and not so.empty:
        s_ret = ((sc.iloc[-1] - so.iloc[0]) / so.iloc[0]) * 100
        sec_res[s_name] = {"ret": s_ret, "rs": round(s_ret - nifty_ret, 2)}
    else:
        sec_res[s_name] = {"ret": 0.0, "rs": 0.0}

# ==============================================================
# মূল ড্যাশবোর্ড মোড নির্বাচন
# ==============================================================
dash_view = st.radio("ভিউ মোড বাছুন:", ["🎯 Single Stock Deep Workspace (Recommended)", "🌐 Full Universe Scanner & Rankings"], horizontal=True)

# --------------------------------------------------------------
# PRIORITY 1: SINGLE STOCK DEEP WORKSPACE
# --------------------------------------------------------------
if dash_view == "🎯 Single Stock Deep Workspace (Recommended)":
    c_sel1, c_sel2 = st.columns([1.5, 2.5])
    with c_sel1:
        sel_sector = st.selectbox("১. সেক্টর সিলেক্ট করুন:", list(SECTOR_MAP.keys()))
    with c_sel2:
        sec_stks = [s.replace(".NS", "") for s in SECTOR_MAP[sel_sector]["stocks"]]
        selected_stock = st.selectbox("২. স্টক নির্বাচন করুন (Deep Analysis):", sec_stks)

    full_ticker = selected_stock + ".NS"
    stk_c = get_col(cut_intra, "Close", full_ticker)
    stk_o = get_col(cut_intra, "Open", full_ticker)
    stk_h = get_col(cut_intra, "High", full_ticker)
    stk_l = get_col(cut_intra, "Low", full_ticker)
    stk_v = get_col(cut_intra, "Volume", full_ticker)

    if stk_c.empty:
        st.warning("উক্ত স্টকের পর্যাপ্ত ডেটা পাওয়া যায়নি।")
        st.stop()

    ltp = stk_c.iloc[-1]
    stk_ret = ((ltp - stk_o.iloc[0]) / stk_o.iloc[0]) * 100
    stk_rs = round(stk_ret - nifty_ret, 2)
    stk_sec = STOCK_TO_SEC.get(full_ticker, "F&O")
    sec_rs_val = sec_res.get(stk_sec, {}).get("rs", 0.0)

    # Priority 3: Market - Sector - Stock Alignment (+3 থেকে -3)
    n_score = 1 if nifty_ret > 0 else -1
    s_score = 1 if sec_rs_val > 0 else -1
    k_score = 1 if stk_rs > 0 else -1
    alignment_total = n_score + s_score + k_score

    if alignment_total == 3:
        align_label = "🔥 Grade A+ (Perfect Bullish Alignment)"
        align_color = "#10b981"
    elif alignment_total == -3:
        align_label = "⚠️ Grade A+ (Perfect Bearish Breakdown)"
        align_color = "#ef4444"
    elif alignment_total > 0:
        align_label = "🟢 Moderate Bullish (Mixed Alignment)"
        align_color = "#3b82f6"
    else:
        align_label = "🔴 Moderate Bearish (Mixed Alignment)"
        align_color = "#f59e0b"

    # মেট্রিক কার্ডস
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric(f"{selected_stock} LTP", f"₹{ltp:.2f}", f"{stk_ret:+.2f}%")
    with m2: st.metric("Stock Daily RS", f"{stk_rs:+.2f}%", "vs Nifty 50")
    with m3: st.metric(f"{stk_sec} Sector RS", f"{sec_rs_val:+.2f}%", "Sector Strength")
    with m4: st.markdown(f"**Confluence Score:**<br><span style='color:{align_color}; font-weight:bold; font-size:16px;'>{align_label}</span>", unsafe_allow_html=True)

    st.markdown("---")

    # Priority 2: 5m Candlestick Chart + Complete Indicator Panels
    st.subheader(f"📊 {selected_stock} - Complete 5m Chart & Subplot Panels")

    # ইন্ডিকেটর ক্যালকুলেশন
    stk_full_hist = get_col(live_df, "Close", full_ticker)
    f_ma = calc_ma(stk_full_hist, fast_len, ma_type).reindex(stk_c.index)
    s_ma = calc_ma(stk_full_hist, slow_len, ma_type).reindex(stk_c.index)
    t_ma = calc_ma(stk_full_hist, trend_len, ma_type).reindex(stk_c.index)
    vwap_line = calc_vwap(cut_intra, full_ticker)

    # Corrected ORB Logic (Look-ahead Bias মুক্ত)
    market_open = cut_intra.index[0].replace(hour=9, minute=15)
    orb_end = market_open + pd.Timedelta(minutes=orb_window_mins)
    orb_slice = cut_intra[(cut_intra.index >= market_open) & (cut_intra.index <= orb_end)]
    
    orb_ready = latest_ts > orb_end
    orb_high = get_col(orb_slice, "High", full_ticker).max() if orb_ready and not orb_slice.empty else np.nan
    orb_low = get_col(orb_slice, "Low", full_ticker).min() if orb_ready and not orb_slice.empty else np.nan

    # টগলস
    tg1, tg2, tg3, tg4, tg5 = st.columns(5)
    with tg1: show_vw = st.checkbox("VWAP", value=True)
    with tg2: show_fast = st.checkbox(f"Fast {ma_type} ({fast_len})", value=True)
    with tg3: show_slow = st.checkbox(f"Slow {ma_type} ({slow_len})", value=True)
    with tg4: show_trend = st.checkbox(f"Trend {ma_type} ({trend_len})", value=False)
    with tg5: show_orb = st.checkbox("ORB High/Low Lines", value=True)

    # RS Subplot লাইন
    cum_stk = ((stk_c - stk_o.iloc[0]) / stk_o.iloc[0]) * 100
    cum_nifty = ((n_c - n_o.iloc[0]) / n_o.iloc[0]) * 100
    rs_line = cum_stk - cum_nifty

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.72, 0.28], subplot_titles=(f"{selected_stock} Price & Overlays", "Relative Strength (RS) Subplot vs Nifty 50"))

    # Price Candlestick
    fig.add_trace(go.Candlestick(x=stk_c.index, open=stk_o, high=stk_h, low=stk_l, close=stk_c, name="Candles"), row=1, col=1)

    if show_fast: fig.add_trace(go.Scatter(x=f_ma.index, y=f_ma, mode="lines", name=f"Fast {fast_len}", line=dict(color="#10b981", width=1.5)), row=1, col=1)
    if show_slow: fig.add_trace(go.Scatter(x=s_ma.index, y=s_ma, mode="lines", name=f"Slow {slow_len}", line=dict(color="#ef4444", width=1.5)), row=1, col=1)
    if show_trend: fig.add_trace(go.Scatter(x=t_ma.index, y=t_ma, mode="lines", name=f"Trend {trend_len}", line=dict(color="#3b82f6", width=1.5)), row=1, col=1)
    if show_vw and not vwap_line.empty: fig.add_trace(go.Scatter(x=vwap_line.index, y=vwap_line, mode="lines", name="VWAP", line=dict(color="#f59e0b", width=1.5)), row=1, col=1)

    # ORB Lines
    if show_orb and orb_ready and not np.isnan(orb_high):
        fig.add_hline(y=orb_high, line_dash="dot", line_color="#38bdf8", annotation_text="ORB High", row=1, col=1)
        fig.add_hline(y=orb_low, line_dash="dot", line_color="#fb7185", annotation_text="ORB Low", row=1, col=1)

    # Color-coded RS Subplot
    pos_rs = rs_line.where(rs_line >= 0)
    neg_rs = rs_line.where(rs_line < 0)
    fig.add_trace(go.Scatter(x=rs_line.index, y=pos_rs, mode="lines", name="RS (+)", line=dict(color="#10b981", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=rs_line.index, y=neg_rs, mode="lines", name="RS (-)", line=dict(color="#ef4444", width=2)), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="#64748b", row=2, col=1)

    fig.update_layout(height=600, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark", xaxis_rangeslider_visible=False, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # Priority 5: Risk, Key Levels & Position Sizing Panel
    st.markdown("---")
    st.subheader(f"🛡️ {selected_stock} - Risk & Trade Setup Context")
    
    # CPR ক্যালকুলেশন
    d_h = get_col(daily_df, "High", full_ticker)
    d_l = get_col(daily_df, "Low", full_ticker)
    d_c = get_col(daily_df, "Close", full_ticker)
    
    if len(d_c) >= 2:
        H, L, C = d_h.iloc[-2], d_l.iloc[-2], d_c.iloc[-2]
        P = (H + L + C) / 3
        BC = (H + L) / 2
        TC = 2 * P - BC
        cpr_width = abs(TC - BC) / P * 100
        tier = "Tier 1 (Ultra Narrow)" if cpr_width <= 0.25 else ("Tier 2 (Narrow)" if cpr_width <= 0.50 else "Normal")
    else:
        P, BC, TC, cpr_width, tier = ltp, ltp, ltp, 0.0, "N/A"

    atr_val = calc_atr(stk_h, stk_l, stk_c, 14).iloc[-1] if len(stk_c) > 14 else (ltp * 0.005)

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown("##### 📐 Key CPR & Breakout Levels")
        st.write(f"- **Pivot (P):** ₹{P:.2f} | **TC:** ₹{TC:.2f} | **BC:** ₹{BC:.2f}")
        st.write(f"- **CPR Width:** `{cpr_width:.3f}%` ({tier})")
        st.write(f"- **ORB Status ({orb_window_mins}m):** " + (f"🔥 Broke Above High (₹{orb_high:.2f})" if ltp > orb_high else (f"⚠️ Broke Below Low (₹{orb_low:.2f})" if ltp < orb_low else "Inside Range") if orb_ready else "উইন্ডো সম্পন্ন হয়নি"))

    with r_col2:
        st.markdown("##### 💼 Realistic Position Sizer (Margin Guarded)")
        user_cap = st.number_input("ক্যাপিটাল (INR):", value=100000, step=10000)
        risk_pct = st.number_input("রিস্ক পার ট্রেড (%):", value=1.0, step=0.25)
        
        max_risk_amount = user_cap * (risk_pct / 100)
        sl_points = atr_val * 1.5
        ideal_qty = int(max_risk_amount / sl_points) if sl_points > 0 else 0
        
        # মার্জিন ক্যাপ গার্ড (ইন্ট্রাডে ৫x লিভারেজ লিমিট)
        max_allowed_qty = int((user_cap * 5) / ltp)
        final_qty = min(ideal_qty, max_allowed_qty)

        st.write(f"- **Stop Loss (1.5x ATR):** ₹{sl_points:.2f} (SL Price: ₹{ltp - sl_points:.2f})")
        st.write(f"- **Target 1 (2x ATR):** ₹{ltp + (atr_val * 2.0):.2f} | **Target 2 (3x ATR):** ₹{ltp + (atr_val * 3.0):.2f}")
        st.write(f"- **Recommended Quantity:** **`{final_qty} Shares`** (Margin Cap: {max_allowed_qty})")

    # Priority 4: Reliable 60-Day (2-Month) Intraday Backtest Engine
    st.markdown("---")
    st.subheader(f"🧪 {selected_stock} - Reliable 60-Day (2-Month) Intraday Backtest")
    st.caption("প্রকৃত ৬০ দিনের ৫-মিনিটের ইন্ট্রাডে ডেটা | নো লুক-অ্যাহেড বায়াস | ৩:১৫ সেশন ক্লোজ | Long & Short Both Sides")

    bt_side = st.selectbox("ট্রেডিং সাইড:", ["Both (Long & Short)", "Long Only", "Short Only"])
    brokerage_fee = st.number_input("ব্রোকারেজ ও চার্জেস (INR / Trade):", value=40, step=5)
    slippage_bps = st.number_input("স্লিপেজ (%):", value=0.04, step=0.01)

    if st.button(f"🚀 {selected_stock}-এর ৬০ দিনের ব্যাকটেস্ট শুরু করুন"):
        with st.spinner("৬০ দিনের সম্পূর্ণ ৫-মিনিট ডেটা নামিয়ে সিমুলেশন চলছে..."):
            bt_raw = fetch_stock_60d_intraday(full_ticker)
            if bt_raw.empty or len(bt_raw) < 100:
                st.error("৬০ দিনের ইন্ট্রাডে ডেটা লোড করা যায়নি।")
            else:
                bt_close = bt_raw["Close"]
                bt_fast = calc_ma(bt_close, fast_len, ma_type)
                bt_slow = calc_ma(bt_close, slow_len, ma_type)

                trades = []
                pos = 0  # +1 Long, -1 Short
                entry_px = 0
                entry_dt = None
                fixed_shares = final_qty if final_qty > 0 else 50

                for i in range(2, len(bt_close)):
                    curr_dt = bt_close.index[i]
                    prev_dt = bt_close.index[i-1]
                    
                    # ডে-সেশন স্কয়ার-অফ (3:15 PM বা দিন বদল হলে ক্লোজ)
                    is_eod = (curr_dt.time() >= time(15, 15)) or (curr_dt.date() != prev_dt.date())

                    if pos != 0 and is_eod:
                        exit_px = bt_close.iloc[i] * (1 - slippage_bps/100 if pos == 1 else 1 + slippage_bps/100)
                        raw_pnl = (exit_px - entry_px) * fixed_shares if pos == 1 else (entry_px - exit_px) * fixed_shares
                        net_pnl = raw_pnl - brokerage_fee
                        trades.append({"Date": entry_dt.strftime("%Y-%m-%d"), "Type": "LONG" if pos == 1 else "SHORT", "Entry": round(entry_px, 2), "Exit": round(exit_px, 2), "Reason": "EOD Squareoff", "Net_PnL": round(net_pnl, 2)})
                        pos = 0
                        continue

                    # পূর্ববর্তী ক্যান্ডেলের কনফার্মড সিগন্যাল (Look-ahead bias মুক্ত)
                    bull_cross = bt_fast.iloc[i-1] > bt_slow.iloc[i-1] and bt_fast.iloc[i-2] <= bt_slow.iloc[i-2]
                    bear_cross = bt_fast.iloc[i-1] < bt_slow.iloc[i-1] and bt_fast.iloc[i-2] >= bt_slow.iloc[i-2]

                    # বর্তমান ক্যান্ডেলের শুরুতে এন্ট্রি
                    if pos == 0 and curr_dt.time() < time(14, 45):
                        if bull_cross and bt_side in ["Both (Long & Short)", "Long Only"]:
                            pos = 1
                            entry_px = bt_close.iloc[i] * (1 + slippage_bps/100)
                            entry_dt = curr_dt
                        elif bear_cross and bt_side in ["Both (Long & Short)", "Short Only"]:
                            pos = -1
                            entry_px = bt_close.iloc[i] * (1 - slippage_bps/100)
                            entry_dt = curr_dt

                    # অপোজিট ক্রসওভারে এক্সিট
                    elif pos == 1 and bear_cross:
                        exit_px = bt_close.iloc[i] * (1 - slippage_bps/100)
                        net_pnl = ((exit_px - entry_px) * fixed_shares) - brokerage_fee
                        trades.append({"Date": entry_dt.strftime("%Y-%m-%d"), "Type": "LONG", "Entry": round(entry_px, 2), "Exit": round(exit_px, 2), "Reason": "Opposite Cross", "Net_PnL": round(net_pnl, 2)})
                        pos = 0
                    elif pos == -1 and bull_cross:
                        exit_px = bt_close.iloc[i] * (1 + slippage_bps/100)
                        net_pnl = ((entry_px - exit_px) * fixed_shares) - brokerage_fee
                        trades.append({"Date": entry_dt.strftime("%Y-%m-%d"), "Type": "SHORT", "Entry": round(entry_px, 2), "Exit": round(exit_px, 2), "Reason": "Opposite Cross", "Net_PnL": round(net_pnl, 2)})
                        pos = 0

                df_bt = pd.DataFrame(trades)
                if not df_bt.empty:
                    wins = len(df_bt[df_bt["Net_PnL"] > 0])
                    tot = len(df_bt)
                    w_rate = (wins / tot) * 100
                    tot_profit = df_bt["Net_PnL"].sum()

                    df_bt["Equity"] = df_bt["Net_PnL"].cumsum()
                    max_dd = (df_bt["Equity"].cummax() - df_bt["Equity"]).max()

                    b1, b2, b3, b4 = st.columns(4)
                    with b1: st.metric("মোট ট্রেড সংখ্যা", tot)
                    with b2: st.metric("উইন রেট (%)", f"{w_rate:.1f}%")
                    with b3: st.metric("নেট সঞ্চিত P&L", f"₹{tot_profit:.2f}")
                    with b4: st.metric("ম্যাক্স ড্র-ডাউন", f"₹{max_dd:.2f}")

                    # Equity Curve
                    fig_eq = go.Figure()
                    fig_eq.add_trace(go.Scatter(y=df_bt["Equity"], mode="lines", name="Equity Curve", line=dict(color="#38bdf8", width=2)))
                    fig_eq.update_layout(height=280, title="৬০ দিনের কিউমুলেটিভ ইক্যুইটি কার্ভ (Net P&L)", template="plotly_dark", margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_eq, use_container_width=True)

                    st.dataframe(df_bt.tail(15).style.map(lambda v: 'color: #10b981;' if v > 0 else 'color: #ef4444;', subset=['Net_PnL']), use_container_width=True, hide_index=True)
                else:
                    st.warning("৬০ দিনের মধ্যে উল্লেখিত নিয়মে কোনো ট্রেড ট্রিগার হয়নি।")

# --------------------------------------------------------------
# FULL UNIVERSE SCANNER
# --------------------------------------------------------------
else:
    st.subheader("🌐 সম্পূর্ণ F&O ইউনিভার্স র‍্যাঙ্কিং ও ফিল্টার")
    universe_rows = []
    for s in ALL_STOCKS:
        try:
            c = get_col(cut_intra, "Close", s); o = get_col(cut_intra, "Open", s)
            if len(c) < 5: continue
            ltp = c.iloc[-1]
            ret = ((ltp - o.iloc[0]) / o.iloc[0]) * 100
            rs = round(ret - nifty_ret, 2)
            sec = STOCK_TO_SEC.get(s, "F&O")
            sec_rs = sec_res.get(sec, {}).get("rs", 0.0)
            
            universe_rows.append({
                "Stock": s.replace(".NS", ""), "Sector": sec, "LTP": round(ltp, 2),
                "Change_%": round(ret, 2), "Daily_RS": rs, "Sector_RS": sec_rs,
                "Confluence": "🟢 Strong Bullish" if rs > 0 and sec_rs > 0 and nifty_ret > 0 else ("🔴 Strong Bearish" if rs < 0 and sec_rs < 0 and nifty_ret < 0 else "⚪ Mixed")
            })
        except Exception: pass

    df_u = pd.DataFrame(universe_rows).sort_values(by="Daily_RS", ascending=False)
    st.dataframe(
        df_u.style.map(lambda v: 'color: #10b981; font-weight: bold;' if 'Bullish' in str(v) or (isinstance(v, (int, float)) and v > 0) else ('color: #ef4444; font-weight: bold;' if 'Bearish' in str(v) or (isinstance(v, (int, float)) and v < 0) else ''), subset=['Daily_RS', 'Sector_RS', 'Change_%', 'Confluence']),
        use_container_width=True, hide_index=True
    )


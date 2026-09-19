import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="NSE Complete F&O Institutional Engine", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.main {background-color: #0b0f19; color: #f3f4f6;}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px;">
    <h2 style="margin: 0; color: #38bdf8; font-size: 24px;">⚡ COMPLETE NSE F&O INSTITUTIONAL ENGINE (180+ STOCKS)</h2>
    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Full F&O Universe ⬩ Sector RS Breakdown ⬩ Mechanical EMA Touch ⬩ Subplot RS Panels</p>
</div>
""", unsafe_allow_html=True)

# ১. সম্পূর্ণ ১৮০+ NSE F&O স্টক ও সেক্টর ম্যাপিং
SECTOR_MAP = {
    "BANK": {
        "ticker": "^NSEBANK",
        "stocks": [
            "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", 
            "INDUSINDBK.NS", "BANDHANBNK.NS", "AUBANK.NS", "BANKBARODA.NS", "PNB.NS", 
            "CANBK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "RBLBANK.NS"
        ]
    },
    "AUTO": {
        "ticker": "^CNXAUTO",
        "stocks": [
            "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", 
            "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "BALKRISIND.NS", 
            "MRF.NS", "APOLLOTYRE.NS", "BOSCHLTD.NS", "MOTHERSON.NS", "ESCORTS.NS"
        ]
    },
    "IT": {
        "ticker": "^CNXIT",
        "stocks": [
            "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", 
            "LTIM.NS", "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS", "LTTS.NS", 
            "OFSS.NS", "TATAELXSI.NS", "BSOFT.NS"
        ]
    },
    "METAL": {
        "ticker": "^CNXMETAL",
        "stocks": [
            "TATASTEEL.NS", "JSL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", 
            "SAIL.NS", "NMDC.NS", "NATIONALUM.NS", "JINDALSTEL.NS", "HINDZINC.NS", 
            "APLAPOLLO.NS"
        ]
    },
    "PHARMA": {
        "ticker": "^CNXPHARMA",
        "stocks": [
            "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", 
            "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "ZYDUSLIFE.NS", "MANKIND.NS", 
            "ALKEM.NS", "BIOCON.NS", "GLENMARK.NS", "GRANULES.NS", "IPCALAB.NS", "LAURUSLABS.NS", "ABBOTINDIA.NS"
        ]
    },
    "ENERGY": {
        "ticker": "^CNXENERGY",
        "stocks": [
            "RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS", 
            "COALINDIA.NS", "IOC.NS", "GAIL.NS", "TATAPOWER.NS", "ADANIGREEN.NS", 
            "ADANIENSOL.NS", "PETRONET.NS", "IGL.NS", "MGL.NS", "OIL.NS"
        ]
    },
    "FMCG": {
        "ticker": "^CNXFMCG",
        "stocks": [
            "ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", 
            "DABUR.NS", "GODREJCP.NS", "MARICO.NS", "COLPAL.NS", "MCDOWELL-N.NS", 
            "VBL.NS", "UBL.NS", "RADICO.NS", "BALRAMCHIN.NS"
        ]
    },
    "FIN_SERVICES": {
        "ticker": "NIFTY_FIN_SERVICE.NS",
        "stocks": [
            "BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "SHRIRAMFIN.NS", "MUTHOOTFIN.NS", 
            "M&MFIN.NS", "HDFCLIFE.NS", "SBILIFE.NS", "ICICIPRULI.NS", "ICICIGI.NS", 
            "PFC.NS", "RECLTD.NS", "LICHSGFIN.NS", "MANAPPURAM.NS", "L&TFH.NS", "HDFCAMC.NS"
        ]
    },
    "INFRA_CAPGOODS": {
        "ticker": "^CNXINFRA",
        "stocks": [
            "LT.NS", "BHARTIARTL.NS", "ULTRACEMCO.NS", "GRASIM.NS", "ADANIPORTS.NS", 
            "SIEMENS.NS", "ABB.NS", "HAL.NS", "BEL.NS", "BHEL.NS", 
            "CUMMINSIND.NS", "ASTRAL.NS", "POLYCAB.NS", "HAVELLS.NS", "VOLTAS.NS", "INDUSTOWER.NS"
        ]
    },
    "REALTY": {
        "ticker": "^CNXREALTY",
        "stocks": [
            "DLF.NS", "GODREJPROP.NS", "OBERORLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS", "BRIGADE.NS"
        ]
    },
    "CONSUMER_SERVICES_OTHERS": {
        "ticker": "^NSEI",
        "stocks": [
            "TRENT.NS", "NAUKRI.NS", "INDIGO.NS", "PIDILITIND.NS", "SRF.NS", 
            "CONCOR.NS", "PIIND.NS", "DEEPAKNTR.NS", "TATACHEM.NS", "GUJGASLTD.NS", 
            "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS", "JUBLFOOD.NS", "PAGEIND.NS", 
            "INDIAMART.NS", "IRCTC.NS", "ABCAPITAL.NS", "GMRINFRA.NS", "IDEA.NS"
        ]
    }
}

ALL_STOCKS = sorted(list(set([s for sec in SECTOR_MAP.values() for s in sec["stocks"]])))
STOCK_TO_SEC = {s: sec for sec, val in SECTOR_MAP.items() for s in val["stocks"]}

# ২. ডেটা ক্যাশিং পাইপলাইন
@st.cache_data(ttl=60)
def get_intraday_5m(tickers):
    try:
        df = yf.download(list(tickers), period="5d", interval="5m", progress=False, threads=True)
        if df.empty: return df
        df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata") if df.index.tz is None else df.index.tz_convert("Asia/Kolkata")
        return df
    except Exception: return pd.DataFrame()

@st.cache_data(ttl=600)
def get_daily_5y(tickers):
    try:
        return yf.download(list(tickers), period="5y", interval="1d", progress=False, threads=True)
    except Exception: return pd.DataFrame()

def get_col(df, field, tk):
    try:
        res = df[field][tk].dropna()
        return res if not res.empty else pd.Series(dtype=float)
    except Exception: return pd.Series(dtype=float)

def calc_ma(series, period, kind="EMA"):
    return series.ewm(span=period, adjust=False).mean() if kind == "EMA" else series.rolling(period).mean()

def calc_vwap(df, tk):
    h = get_col(df, "High", tk); l = get_col(df, "Low", tk); c = get_col(df, "Close", tk); v = get_col(df, "Volume", tk)
    x = pd.concat([h, l, c, v], axis=1).dropna()
    x.columns = ["h", "l", "c", "v"]
    if x.empty: return pd.Series(dtype=float)
    typical = (x.h + x.l + x.c) / 3
    cum_vol = x.v.groupby(x.index.date).cumsum()
    cum_vp = (typical * x.v).groupby(x.index.date).cumsum()
    return (cum_vp / cum_vol.replace(0, np.nan)).reindex(x.index)

def classify_touch(c, o, h, l, ma_s, tol=0.15, mom_lb=5, mom_thr=0.4):
    if len(c) < max(3, mom_lb + 2): return ('No Touch', 'None', 'None', 0.0)
    m = float(ma_s.iloc[-1]); price = float(c.iloc[-1]); hi = float(h.iloc[-1]); lo = float(l.iloc[-1])
    touched = (lo <= m * (1 + tol/100) and hi >= m * (1 - tol/100)) or abs(price - m) / abs(m) * 100 <= tol
    if not touched: return ('No Touch', 'None', 'None', 0.0)
    prev = float(c.iloc[-2]); prev_m = float(ma_s.iloc[-2])
    direction = 'From Above' if prev > prev_m else ('From Below' if prev < prev_m else 'At MA')
    base = float(c.iloc[-mom_lb-1]); end = float(c.iloc[-2]); move = (end - base) / base * 100 if base else 0
    prior = 'Bullish' if move >= mom_thr else ('Bearish' if move <= -mom_thr else 'Neutral')
    if prior == 'Bullish' and direction == 'From Above': typ = 'Bullish Momentum Pullback'
    elif prior == 'Bearish' and direction == 'From Below': typ = 'Bearish Momentum Pullback'
    elif prior == 'Bullish' and direction == 'From Below': typ = 'Bullish Reclaim/Retest'
    elif prior == 'Bearish' and direction == 'From Above': typ = 'Bearish Breakdown Retest'
    else: typ = f'Normal Touch ({direction})'
    return ('Touch', direction, typ, round(move, 2))

# ৩. সাইডবার সেটিংস
st.sidebar.header("⚙️ সিস্টেম কন্ট্রোল")
engine_mode = st.sidebar.radio("অপারেশন মোড:", ["🔴 Live Market Engine", "⏪ Historical Replay"])
ma_kind = st.sidebar.selectbox("MA ধরণ:", ["EMA", "SMA"])
fast_p = st.sidebar.number_input("Fast MA:", 3, 100, 13)
slow_p = st.sidebar.number_input("Slow MA:", 5, 200, 21)
trend_p = st.sidebar.number_input("Trend MA:", 10, 500, 50)
p1_val = st.sidebar.number_input("Swing RS 1 (দিন):", 5, 100, 21)
p2_val = st.sidebar.number_input("Swing RS 2 (দিন):", 10, 200, 50)

# ডেটা ফেচিং
with st.spinner(f"⏳ সম্পূর্ণ F&O ইউনিভার্সের ({len(ALL_STOCKS)} স্টক) ডেটা লোড হচ্ছে..."):
    all_syms = ["^NSEI"] + [v["ticker"] for v in SECTOR_MAP.values()] + ALL_STOCKS
    intra_data = get_intraday_5m(all_syms)
    daily_data = get_daily_5y(all_syms)

if intra_data.empty or daily_data.empty:
    st.error("ডেটা লোড করা যায়নি। অনুগ্রহ করে পেজটি Refresh করুন।")
    st.stop()

# টাইম কাট লজিক
avail_dates = sorted(list(set(intra_data.index.date)), reverse=True)
if engine_mode == "⏪ Historical Replay":
    sel_date = st.sidebar.date_input("তারিখ বাছুন:", avail_dates[0], min_value=min(avail_dates), max_value=max(avail_dates))
    day_df = intra_data[intra_data.index.date == sel_date]
    if day_df.empty: st.warning("উক্ত তারিখে ডেটা নেই।"); st.stop()
    cut_time = st.sidebar.select_slider("সময় নির্বাচন:", options=list(day_df.index), value=list(day_df.index)[-1], format_func=lambda x: x.strftime("%H:%M"))
else:
    sel_date = avail_dates[0]
    cut_time = intra_data[intra_data.index.date == sel_date].index[-1]

cut_intra = intra_data[(intra_data.index.date == sel_date) & (intra_data.index <= cut_time)]
nifty_c = get_col(cut_intra, "Close", "^NSEI")
nifty_o = get_col(cut_intra, "Open", "^NSEI")
nifty_ret = ((nifty_c.iloc[-1] - nifty_o.iloc[0]) / nifty_o.iloc[0]) * 100 if not nifty_c.empty else 0
n_hr_open = nifty_c.iloc[-12] if len(nifty_c) >= 12 else nifty_c.iloc[0]
nifty_hr_ret = ((nifty_c.iloc[-1] - n_hr_open) / n_hr_open) * 100 if n_hr_open > 0 else 0

st.info(f"📍 স্ন্যাপশট: **{cut_time.strftime('%d-%b-%Y %I:%M %p')}** | Nifty 50: **{nifty_ret:+.2f}%** | মোট স্টক: **{len(ALL_STOCKS)} টি**")

# ড্যাশবোর্ড ট্যাবসমূহ
tab_sec_rs, tab_ema_scanner, tab_swing = st.tabs([
    "🌐 Sector RS & Stock Drilldown",
    "🎯 EMA Momentum & Touch Scanner",
    "🚀 5Y Swing & Subplot RS Chart"
])

# --------------------------------------------------------------
# TAB 1: SECTOR RS & STOCK DRILLDOWN
# --------------------------------------------------------------
with tab_sec_rs:
    st.subheader("🏆 Sector Relative Strength (RS) Dashboard")
    sec_summary = []
    for s_name, s_info in SECTOR_MAP.items():
        sym = s_info["ticker"]
        sc = get_col(cut_intra, "Close", sym)
        so = get_col(cut_intra, "Open", sym)
        if not sc.empty and not so.empty:
            ret = ((sc.iloc[-1] - so.iloc[0]) / so.iloc[0]) * 100
            sec_summary.append({"Sector": s_name, "Return_%": round(ret, 2), "Daily_RS": round(ret - nifty_ret, 2)})
    
    sec_df = pd.DataFrame(sec_summary).sort_values(by="Daily_RS", ascending=False).reset_index(drop=True)
    c1, c2 = st.columns([1.2, 2.8])
    with c1:
        st.dataframe(sec_df.style.map(lambda v: 'color: #10b981; font-weight: bold;' if v > 0 else 'color: #ef4444; font-weight: bold;', subset=['Daily_RS', 'Return_%']), use_container_width=True, hide_index=True)
    with c2:
        selected_sec = st.radio("সেক্টর নির্বাচন করুন (ড্রিলডাউন ফিল্টারের জন্য):", sec_df["Sector"].tolist(), horizontal=True)

    st.markdown("---")
    st.subheader(f"📋 `{selected_sec}` সেক্টরের অভ্যন্তরীণ স্টকসমূহ (Daily & Hourly RS)")
    sec_stks = SECTOR_MAP[selected_sec]["stocks"]
    sec_stk_rows = []
    for s in sec_stks:
        c = get_col(cut_intra, "Close", s); o = get_col(cut_intra, "Open", s)
        if len(c) < 2: continue
        ltp = c.iloc[-1]; ret = ((ltp - o.iloc[0]) / o.iloc[0]) * 100
        hr_o = c.iloc[-12] if len(c) >= 12 else c.iloc[0]
        hr_ret = ((ltp - hr_o) / hr_o) * 100
        full_c = get_col(intra_data, "Close", s).loc[:cut_time]
        t_val = calc_ma(full_c, trend_p, ma_kind).iloc[-1]
        sec_stk_rows.append({
            "Stock": s.replace(".NS", ""), "LTP": round(ltp, 2), "Change_%": round(ret, 2),
            "Daily_RS": round(ret - nifty_ret, 2), "Hourly_RS": round(hr_ret - nifty_hr_ret, 2),
            f"Trend_{trend_p}": "Above" if ltp >= t_val else "Below"
        })
    df_sec_stks = pd.DataFrame(sec_stk_rows).sort_values(by="Daily_RS", ascending=False).reset_index(drop=True)
    st.dataframe(df_sec_stks.style.map(lambda v: 'color: #10b981; font-weight: bold;' if v > 0 else 'color: #ef4444; font-weight: bold;', subset=['Daily_RS', 'Hourly_RS', 'Change_%']), use_container_width=True, hide_index=True)

# --------------------------------------------------------------
# TAB 2: DEDICATED EMA SCANNER & TOUCH ENGINE
# --------------------------------------------------------------
with tab_ema_scanner:
    st.subheader(f"🎯 Mechanical EMA Scanner (১৮০+ F&O ইউনিভার্স)")
    
    scanner_rows = []
    for s in ALL_STOCKS:
        try:
            c = get_col(cut_intra, "Close", s); o = get_col(cut_intra, "Open", s); h = get_col(cut_intra, "High", s); l = get_col(cut_intra, "Low", s)
            if len(c) < max(5, slow_p + 2): continue
            ltp = c.iloc[-1]; ret = ((ltp - o.iloc[0]) / o.iloc[0]) * 100
            full_c = get_col(intra_data, "Close", s).loc[:cut_time]
            f_ma = calc_ma(full_c, fast_p, ma_kind); s_ma = calc_ma(full_c, slow_p, ma_kind); t_ma = calc_ma(full_c, trend_p, ma_kind)
            
            # Crossover
            if f_ma.iloc[-1] > s_ma.iloc[-1] and f_ma.iloc[-2] <= s_ma.iloc[-2]: cross = "Golden Cross"
            elif f_ma.iloc[-1] < s_ma.iloc[-1] and f_ma.iloc[-2] >= s_ma.iloc[-2]: cross = "Death Cross"
            elif f_ma.iloc[-1] > s_ma.iloc[-1]: cross = "Bullish Trend"
            else: cross = "Bearish Trend"
            
            # Touch Logic
            t_status, t_dir, t_type, mom_val = classify_touch(c, o, h, l, f_ma)
            
            scanner_rows.append({
                "Stock": s.replace(".NS", ""), "Sector": STOCK_TO_SEC.get(s, "F&O"), "LTP": round(ltp, 2),
                "Change_%": round(ret, 2), "Daily_RS": round(ret - nifty_ret, 2), "EMA_Cross": cross,
                "Touch_Status": t_status, "Touch_Direction": t_dir, "Touch_Setup": t_type, "Prior_Mom_%": mom_val,
                f"Trend_{trend_p}": "Above" if ltp >= t_ma.iloc[-1] else "Below"
            })
        except Exception: pass
        
    df_scan = pd.DataFrame(scanner_rows)
    f1, f2, f3, f4 = st.columns([1, 1, 1, 1])
    with f1: f_cross = st.selectbox("EMA ক্রসওভার:", ["All", "Golden Cross", "Death Cross", "Bullish Trend", "Bearish Trend"])
    with f2: f_touch = st.selectbox("EMA টাচ ফিল্টার:", ["All", "Touch", "No Touch"])
    with f3: f_setup = st.selectbox("মোমেন্টাম সেটআপ:", ["All", "Bullish Momentum Pullback", "Bearish Momentum Pullback", "Bullish Reclaim/Retest", "Bearish Breakdown Retest"])
    with f4: f_search = st.text_input("স্টক সার্চ:", key="scanner_srch")

    filt_df = df_scan.copy()
    if f_cross != "All": filt_df = filt_df[filt_df["EMA_Cross"] == f_cross]
    if f_touch != "All": filt_df = filt_df[filt_df["Touch_Status"] == f_touch]
    if f_setup != "All": filt_df = filt_df[filt_df["Touch_Setup"] == f_setup]
    if f_search: filt_df = filt_df[filt_df["Stock"].str.contains(f_search.strip().upper(), na=False)]

    st.dataframe(filt_df.style.map(lambda v: 'color: #10b981; font-weight: bold;' if v in ['Golden Cross', 'Bullish Momentum Pullback', 'Bullish Reclaim/Retest'] or (isinstance(v, (int, float)) and v > 0) else ('color: #ef4444; font-weight: bold;' if v in ['Death Cross', 'Bearish Momentum Pullback', 'Bearish Breakdown Retest'] or (isinstance(v, (int, float)) and v < 0) else ''), subset=['Daily_RS', 'Change_%', 'EMA_Cross', 'Touch_Setup']), use_container_width=True, hide_index=True)

# --------------------------------------------------------------
# TAB 3: 5Y SWING & INTERACTIVE SUBPLOT RS CHART
# --------------------------------------------------------------
with tab_swing:
    st.subheader("🚀 5-Year Swing Scanner & Multi-Toggled Subplot Chart")
    
    n_close = get_col(daily_data, "Close", "^NSEI")
    n1_ret = ((n_close.iloc[-1] - n_close.iloc[-p1_val]) / n_close.iloc[-p1_val]) * 100
    n2_ret = ((n_close.iloc[-1] - n_close.iloc[-p2_val]) / n_close.iloc[-p2_val]) * 100

    sw_rows = []
    for s in ALL_STOCKS:
        try:
            cd = get_col(daily_data, "Close", s)
            if len(cd) < max(slow_p, p2_val) + 2: continue
            r1 = round(((cd.iloc[-1] - cd.iloc[-p1_val]) / cd.iloc[-p1_val]) * 100 - n1_ret, 2)
            r2 = round(((cd.iloc[-1] - cd.iloc[-p2_val]) / cd.iloc[-p2_val]) * 100 - n2_ret, 2)
            fd = calc_ma(cd, fast_p, ma_kind); sd = calc_ma(cd, slow_p, ma_kind)
            c_status = "Golden Cross" if fd.iloc[-1] > sd.iloc[-1] and fd.iloc[-2] <= sd.iloc[-2] else ("Death Cross" if fd.iloc[-1] < sd.iloc[-1] and fd.iloc[-2] >= sd.iloc[-2] else ("Bullish" if fd.iloc[-1] > sd.iloc[-1] else "Bearish"))
            sw_rows.append({"Stock": s.replace(".NS", ""), "Sector": STOCK_TO_SEC.get(s, "F&O"), "LTP": round(cd.iloc[-1], 2), f"{p1_val}D_RS": r1, f"{p2_val}D_RS": r2, "Signal": c_status})
        except Exception: pass

    df_sw = pd.DataFrame(sw_rows).sort_values(by=f"{p1_val}D_RS", ascending=False).reset_index(drop=True)
    st.dataframe(df_sw.style.map(lambda v: 'color: #10b981; font-weight: bold;' if v in ['Golden Cross', 'Bullish'] or (isinstance(v, (int, float)) and v > 0) else ('color: #ef4444; font-weight: bold;' if v in ['Death Cross', 'Bearish'] or (isinstance(v, (int, float)) and v < 0) else ''), subset=[f"{p1_val}D_RS", f"{p2_val}D_RS", "Signal"]), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📈 Interactive Dual-Panel Chart (Price + Toggles on Top, Color-Coded RS Subplot Below)")
    
    c_stk, c_tf = st.columns([1.5, 1])
    with c_stk: chart_stk = st.selectbox("চার্ট বিশ্লেষণের জন্য স্টক নির্বাচন করুন:", df_sw["Stock"].tolist())
    with c_tf: tf_choice = st.radio("টাইমফ্রেম বাছুন:", ["5m Intraday (Current Day)", "Daily (5-Year Swing)"], horizontal=True)

    # চার্ট ইন্ডিকেটর টগলসমূহ
    st.markdown("##### 🎛️ চার্ট ইন্ডিকেটর লেয়ার অন/অফ টগল:")
    tg1, tg2, tg3, tg4, tg5 = st.columns(5)
    with tg1: show_candles = st.checkbox("ক্যান্ডেলস্টিক/লাইন", value=True)
    with tg2: show_fast = st.checkbox(f"Fast {ma_kind} ({fast_p})", value=True)
    with tg3: show_slow = st.checkbox(f"Slow {ma_kind} ({slow_p})", value=True)
    with tg4: show_trend = st.checkbox(f"Trend {ma_kind} ({trend_p})", value=False)
    with tg5: show_vwap = st.checkbox("VWAP", value=(tf_choice.startswith("5m")))

    if chart_stk:
        tk = chart_stk + ".NS"
        if tf_choice.startswith("5m"):
            c_series = get_col(cut_intra, "Close", tk)
            o_series = get_col(cut_intra, "Open", tk)
            h_series = get_col(cut_intra, "High", tk)
            l_series = get_col(cut_intra, "Low", tk)
            ref_ret = nifty_ret
            stk_cum_ret = ((c_series - o_series.iloc[0]) / o_series.iloc[0]) * 100
            rs_curve = stk_cum_ret - ref_ret
            vw_curve = calc_vwap(cut_intra, tk)
            full_series = get_col(intra_data, "Close", tk).loc[:cut_time]
        else:
            c_series = get_col(daily_data, "Close", tk)
            o_series = get_col(daily_data, "Open", tk)
            h_series = get_col(daily_data, "High", tk)
            l_series = get_col(daily_data, "Low", tk)
            n_close_full = get_col(daily_data, "Close", "^NSEI")
            stk_cum_ret = ((c_series - c_series.iloc[0]) / c_series.iloc[0]) * 100
            n_cum_ret = ((n_close_full - n_close_full.iloc[0]) / n_close_full.iloc[0]) * 100
            rs_curve = stk_cum_ret - n_cum_ret
            vw_curve = pd.Series(dtype=float)
            full_series = c_series

        f_curve = calc_ma(full_series, fast_p, ma_kind).reindex(c_series.index)
        s_curve = calc_ma(full_series, slow_p, ma_kind).reindex(c_series.index)
        t_curve = calc_ma(full_series, trend_p, ma_kind).reindex(c_series.index)

        # সাবপ্লট ফিগার (Row 1: প্রাইস, Row 2: কালার-কোডেড RS)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.72, 0.28], subplot_titles=(f"{chart_stk} প্রাইস ও ইন্ডিকেটর", "Relative Strength (RS) লাইন (Zero-Centric)"))

        if show_candles:
            fig.add_trace(go.Candlestick(x=c_series.index, open=o_series, high=h_series, low=l_series, close=c_series, name="Price"), row=1, col=1)
        if show_fast:
            fig.add_trace(go.Scatter(x=f_curve.index, y=f_curve, mode="lines", name=f"Fast {fast_p}", line=dict(color="#10b981", width=1.5)), row=1, col=1)
        if show_slow:
            fig.add_trace(go.Scatter(x=s_curve.index, y=s_curve, mode="lines", name=f"Slow {slow_p}", line=dict(color="#ef4444", width=1.5)), row=1, col=1)
        if show_trend:
            fig.add_trace(go.Scatter(x=t_curve.index, y=t_curve, mode="lines", name=f"Trend {trend_p}", line=dict(color="#3b82f6", width=1.5)), row=1, col=1)
        if show_vwap and not vw_curve.empty:
            fig.add_trace(go.Scatter(x=vw_curve.index, y=vw_curve, mode="lines", name="VWAP", line=dict(color="#f59e0b", width=1.5)), row=1, col=1)

        # সাবপ্লটে পজিটিভ (সবুজ) ও নেগেটিভ (লাল) RS লাইন
        rs_pos = rs_curve.where(rs_curve >= 0)
        rs_neg = rs_curve.where(rs_curve < 0)
        fig.add_trace(go.Scatter(x=rs_curve.index, y=rs_pos, mode="lines", name="RS Positive", line=dict(color="#10b981", width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=rs_curve.index, y=rs_neg, mode="lines", name="RS Negative", line=dict(color="#ef4444", width=2)), row=2, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", row=2, col=1)

        fig.update_layout(height=650, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark", xaxis_rangeslider_visible=False, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

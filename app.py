    import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time

st.set_page_config(page_title="NSE F&O Institutional Intraday Multi-Engine", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.main {background-color: #0b0f19; color: #f3f4f6;}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
.metric-card {padding: 12px; border-radius: 8px; background: #161e2e; border: 1px solid #283548;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px;">
    <h2 style="margin: 0; color: #38bdf8; font-size: 24px;">⚡ NSE F&O PURE INTRADAY INSTITUTIONAL DASHBOARD</h2>
    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Market Regime ⬩ Sector Rotation ⬩ MTF Confirmation ⬩ CPR/ORB ⬩ Mechanical Signals ⬩ Risk Matrix ⬩ Backtest</p>
</div>
""", unsafe_allow_html=True)

# ১. সম্পূর্ণ ১৮০+ F&O ইউনিভার্স ম্যাপিং
SECTOR_MAP = {
    "BANK": {
        "ticker": "^NSEBANK",
        "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS", "BANDHANBNK.NS", "AUBANK.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "RBLBANK.NS"]
    },
    "AUTO": {
        "ticker": "^CNXAUTO",
        "stocks": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "BALKRISIND.NS", "MRF.NS", "APOLLOTYRE.NS", "BOSCHLTD.NS", "MOTHERSON.NS", "ESCORTS.NS"]
    },
    "IT": {
        "ticker": "^CNXIT",
        "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS", "LTTS.NS", "OFSS.NS", "TATAELXSI.NS", "BSOFT.NS"]
    },
    "METAL": {
        "ticker": "^CNXMETAL",
        "stocks": ["TATASTEEL.NS", "JSL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", "SAIL.NS", "NMDC.NS", "NATIONALUM.NS", "JINDALSTEL.NS", "HINDZINC.NS", "APLAPOLLO.NS"]
    },
    "PHARMA": {
        "ticker": "^CNXPHARMA",
        "stocks": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "ZYDUSLIFE.NS", "MANKIND.NS", "ALKEM.NS", "BIOCON.NS", "GLENMARK.NS", "GRANULES.NS", "IPCALAB.NS", "LAURUSLABS.NS", "ABBOTINDIA.NS"]
    },
    "ENERGY": {
        "ticker": "^CNXENERGY",
        "stocks": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS", "COALINDIA.NS", "IOC.NS", "GAIL.NS", "TATAPOWER.NS", "ADANIGREEN.NS", "ADANIENSOL.NS", "PETRONET.NS", "IGL.NS", "MGL.NS", "OIL.NS"]
    },
    "FMCG": {
        "ticker": "^CNXFMCG",
        "stocks": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "DABUR.NS", "GODREJCP.NS", "MARICO.NS", "COLPAL.NS", "MCDOWELL-N.NS", "VBL.NS", "UBL.NS", "RADICO.NS", "BALRAMCHIN.NS"]
    },
    "FIN_SERVICES": {
        "ticker": "NIFTY_FIN_SERVICE.NS",
        "stocks": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "SHRIRAMFIN.NS", "MUTHOOTFIN.NS", "M&MFIN.NS", "HDFCLIFE.NS", "SBILIFE.NS", "ICICIPRULI.NS", "ICICIGI.NS", "PFC.NS", "RECLTD.NS", "LICHSGFIN.NS", "MANAPPURAM.NS", "L&TFH.NS", "HDFCAMC.NS"]
    },
    "INFRA_CAPGOODS": {
        "ticker": "^CNXINFRA",
        "stocks": ["LT.NS", "BHARTIARTL.NS", "ULTRACEMCO.NS", "GRASIM.NS", "ADANIPORTS.NS", "SIEMENS.NS", "ABB.NS", "HAL.NS", "BEL.NS", "BHEL.NS", "CUMMINSIND.NS", "ASTRAL.NS", "POLYCAB.NS", "HAVELLS.NS", "VOLTAS.NS", "INDUSTOWER.NS"]
    },
    "REALTY": {
        "ticker": "^CNXREALTY",
        "stocks": ["DLF.NS", "GODREJPROP.NS", "OBERORLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS", "BRIGADE.NS"]
    },
    "CONSUMER_SERVICES_OTHERS": {
        "ticker": "^NSEI",
        "stocks": ["TRENT.NS", "NAUKRI.NS", "INDIGO.NS", "PIDILITIND.NS", "SRF.NS", "CONCOR.NS", "PIIND.NS", "DEEPAKNTR.NS", "TATACHEM.NS", "GUJGASLTD.NS", "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS", "JUBLFOOD.NS", "PAGEIND.NS", "INDIAMART.NS", "IRCTC.NS", "ABCAPITAL.NS", "GMRINFRA.NS", "IDEA.NS"]
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
def get_daily_historical(tickers):
    try:
        return yf.download(list(tickers), period="60d", interval="1d", progress=False, threads=True)
    except Exception: return pd.DataFrame()

def get_col(df, field, tk):
    try:
        res = df[field][tk].dropna()
        return res if not res.empty else pd.Series(dtype=float)
    except Exception: return pd.Series(dtype=float)

# ৩. টেকনিক্যাল ম্যাথমেটিক্যাল ইঞ্জিন
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

def calc_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd_l = exp1 - exp2
    sig_l = macd_l.ewm(span=signal, adjust=False).mean()
    hist = macd_l - sig_l
    return macd_l, sig_l, hist

def calc_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
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

def classify_touch(c, o, h, l, ma_s, tol=0.15, mom_lb=5, mom_thr=0.3):
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

# ৪. সাইডবার প্যারামিটার
st.sidebar.header("⚙️ Intraday Controls")
dashboard_mode = st.sidebar.radio("অপারেশন মোড:", ["⚡ Live Intraday Engine", "⏪ Historical Replay Engine"])
ma_kind = st.sidebar.selectbox("MA ধরণ:", ["EMA", "SMA"])
fast_p = st.sidebar.number_input("Fast MA:", 3, 50, 13)
slow_p = st.sidebar.number_input("Slow MA:", 5, 100, 21)
trend_p = st.sidebar.number_input("Trend MA:", 10, 200, 50)
orb_period = st.sidebar.selectbox("ORB উইন্ডো (মিনিট):", [15, 30], index=0)

# ডেটা ফেচ
with st.spinner(f"⏳ সম্পূর্ণ F&O ইউনিভার্সের ({len(ALL_STOCKS)} স্টক) ইন্ট্রাডে ডেটা সিঙ্ক হচ্ছে..."):
    all_syms = ["^NSEI"] + [v["ticker"] for v in SECTOR_MAP.values()] + ALL_STOCKS
    intra_data = get_intraday_5m(all_syms)
    daily_data = get_daily_historical(all_syms)

# Feature 10: Data Quality Monitor
if intra_data.empty:
    st.error("⚠️ লাইভ ইন্ট্রাডে ডেটা পাওয়া যায়নি। মার্কেট অফ-আওয়ার্স বা Yahoo সার্ভার বিজি থাকলে পেজটি রিফ্রেশ করুন।")
    st.stop()

# টাইম কাট লজিক
avail_dates = sorted(list(set(intra_data.index.date)), reverse=True)
if dashboard_mode == "⏪ Historical Replay Engine":
    sel_date = st.sidebar.date_input("রিপ্লে তারিখ বাছুন:", avail_dates[0], min_value=min(avail_dates), max_value=max(avail_dates))
    day_df = intra_data[intra_data.index.date == sel_date]
    if day_df.empty: st.warning("উক্ত তারিখে ডেটা পাওয়া যায়নি।"); st.stop()
    cut_time = st.sidebar.select_slider("সময় নির্বাচন:", options=list(day_df.index), value=list(day_df.index)[-1], format_func=lambda x: x.strftime("%H:%M"))
else:
    sel_date = avail_dates[0]
    cut_time = intra_data[intra_data.index.date == sel_date].index[-1]

cut_intra = intra_data[(intra_data.index.date == sel_date) & (intra_data.index <= cut_time)]
nifty_c = get_col(cut_intra, "Close", "^NSEI")
nifty_o = get_col(cut_intra, "Open", "^NSEI")
nifty_h = get_col(cut_intra, "High", "^NSEI")
nifty_l = get_col(cut_intra, "Low", "^NSEI")
nifty_ret = ((nifty_c.iloc[-1] - nifty_o.iloc[0]) / nifty_o.iloc[0]) * 100 if not nifty_c.empty else 0
n_hr_open = nifty_c.iloc[-12] if len(nifty_c) >= 12 else nifty_c.iloc[0]
nifty_hr_ret = ((nifty_c.iloc[-1] - n_hr_open) / n_hr_open) * 100 if n_hr_open > 0 else 0

# Feature 1: Market Regime Detector
n_vwap = calc_vwap(cut_intra, "^NSEI")
n_vwap_val = n_vwap.iloc[-1] if not n_vwap.empty else nifty_c.iloc[-1]
n_atr = calc_atr(nifty_h, nifty_l, nifty_c, 14).iloc[-1] if len(nifty_c) > 14 else 0

if nifty_ret > 0.35 and nifty_c.iloc[-1] > n_vwap_val:
    regime = "🟢 Bullish Trending (Expansion)"
elif nifty_ret < -0.35 and nifty_c.iloc[-1] < n_vwap_val:
    regime = "🔴 Bearish Trending (Contraction)"
else:
    regime = "🟡 Sideways / Choppy Range"

# --------------------------------------------------------------
# ড্যাশবোর্ড মোড অনুযায়ী মূল ট্যাব বিন্যাস
# --------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 1. Market & Sector Overview",
    "🔍 2. F&O All Stocks Scanner",
    "🏭 3. Sector-Wise Scanner",
    "🎯 4. Momentum Touch Engine",
    "📐 5. CPR & ORB Key Levels",
    "📈 6. Chart & MTF Analysis",
    "🛡️ 7. Risk Management Calculator",
    "🧪 8. Intraday Backtest Engine"
])

# ==============================================================
# TAB 1: MARKET & SECTOR ANALYSIS
# ==============================================================
with tab1:
    st.subheader("🌐 Market Regime & Sector Relative Strength")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Nifty 50 LTP", f"{nifty_c.iloc[-1]:.2f}", f"{nifty_ret:+.2f}%")
    with c2: st.metric("Market Regime", regime.split()[1])
    with c3: st.metric("Nifty 5m ATR (14)", f"{n_atr:.2f}")
    with c4: st.metric("VWAP Relation", "Above VWAP" if nifty_c.iloc[-1] >= n_vwap_val else "Below VWAP")

    st.markdown("---")
    sec_summary = []
    for s_name, s_info in SECTOR_MAP.items():
        sym = s_info["ticker"]
        sc = get_col(cut_intra, "Close", sym)
        so = get_col(cut_intra, "Open", sym)
        if not sc.empty and not so.empty:
            ret = ((sc.iloc[-1] - so.iloc[0]) / so.iloc[0]) * 100
            daily_rs = round(ret - nifty_ret, 2)
            rot_state = "Leading" if daily_rs > 0 and ret > 0 else ("Improving" if daily_rs > 0 and ret <= 0 else ("Weakening" if daily_rs <= 0 and ret > 0 else "Lagging"))
            sec_summary.append({
                "Sector": s_name, "LTP": round(sc.iloc[-1], 2), "Return_%": round(ret, 2),
                "Daily_RS": daily_rs, "Rotation_Quadrant": rot_state,
                "Market_Alignment": "Aligned Bullish" if nifty_ret > 0 and ret > 0 else ("Aligned Bearish" if nifty_ret < 0 and ret < 0 else "Divergent")
            })

    sec_df = pd.DataFrame(sec_summary).sort_values(by="Daily_RS", ascending=False).reset_index(drop=True)
    st.dataframe(
        sec_df.style.map(lambda v: 'color: #10b981; font-weight: bold;' if v in ['Leading', 'Improving', 'Aligned Bullish'] or (isinstance(v, (int, float)) and v > 0) else ('color: #ef4444; font-weight: bold;' if v in ['Lagging', 'Weakening', 'Aligned Bearish'] or (isinstance(v, (int, float)) and v < 0) else ''), subset=['Daily_RS', 'Return_%', 'Rotation_Quadrant', 'Market_Alignment']),
        use_container_width=True, hide_index=True
    )

# ==============================================================
# TAB 2: F&O ALL STOCKS SCANNER & MECHANICAL SIGNAL ENGINE
# ==============================================================
with tab2:
    st.subheader(f"🌐 F&O Stock Universe Scanner ({len(ALL_STOCKS)} Stocks)")
    fno_rows = []
    market_open_time = cut_intra.index[0].replace(hour=9, minute=15)
    orb_cutoff = market_open_time + pd.Timedelta(minutes=orb_period)

    for s in ALL_STOCKS:
        try:
            c = get_col(cut_intra, "Close", s); o = get_col(cut_intra, "Open", s); h = get_col(cut_intra, "High", s); l = get_col(cut_intra, "Low", s); v = get_col(cut_intra, "Volume", s)
            if len(c) < max(5, slow_p + 2): continue
            ltp = c.iloc[-1]; ret = ((ltp - o.iloc[0]) / o.iloc[0]) * 100
            daily_rs = round(ret - nifty_ret, 2)
            hr_o = c.iloc[-12] if len(c) >= 12 else c.iloc[0]
            hourly_rs = round(((ltp - hr_o) / hr_o) * 100 - nifty_hr_ret, 2)

            full_c = get_col(intra_data, "Close", s).loc[:cut_time]
            f_ma = calc_ma(full_c, fast_p, ma_kind); s_ma = calc_ma(full_c, slow_p, ma_kind); t_ma = calc_ma(full_c, trend_p, ma_kind)
            
            # MA Cross
            cross = "Golden Cross" if f_ma.iloc[-1] > s_ma.iloc[-1] and f_ma.iloc[-2] <= s_ma.iloc[-2] else ("Death Cross" if f_ma.iloc[-1] < s_ma.iloc[-1] and f_ma.iloc[-2] >= s_ma.iloc[-2] else ("Bullish" if f_ma.iloc[-1] > s_ma.iloc[-1] else "Bearish"))
            
            # RSI & MACD
            rsi_val = round(calc_rsi(full_c, 14).iloc[-1], 1)
            ml, sl, hl = calc_macd(full_c)
            macd_stat = "Bullish" if hl.iloc[-1] > 0 else "Bearish"

            # RVOL
            v_roll = v.rolling(20).mean().iloc[-1]
            rvol = round(v.iloc[-1] / v_roll, 2) if v_roll > 0 else 1.0

            # ORB Breakout
            orb_slice = cut_intra[(cut_intra.index >= market_open_time) & (cut_intra.index <= orb_cutoff)]
            orb_h = get_col(orb_slice, "High", s).max() if not orb_slice.empty else np.nan
            orb_l = get_col(orb_slice, "Low", s).min() if not orb_slice.empty else np.nan
            orb_stat = "ORB High Break" if ltp > orb_h else ("ORB Low Break" if ltp < orb_l else "Inside ORB")

            # Signal Quality Checklist (Feature 7)
            sec_name = STOCK_TO_SEC.get(s, "F&O")
            sec_item = sec_df[sec_df.Sector == sec_name]
            sec_rs_val = sec_item["Daily_RS"].iloc[0] if not sec_item.empty else 0

            align_score = (1 if nifty_ret > 0 else -1) + (1 if sec_rs_val > 0 else -1) + (1 if daily_rs > 0 else -1)
            
            if align_score == 3 and rvol >= 1.5 and rsi_val >= 55 and ltp >= t_ma.iloc[-1]:
                sig_quality = "Grade A+ (Strong Bullish)"
            elif align_score == -3 and rvol >= 1.5 and rsi_val <= 45 and ltp < t_ma.iloc[-1]:
                sig_quality = "Grade A+ (Strong Bearish)"
            elif align_score >= 1 and rsi_val >= 50:
                sig_quality = "Grade A (Moderate Bullish)"
            elif align_score <= -1 and rsi_val <= 50:
                sig_quality = "Grade A (Moderate Bearish)"
            else:
                sig_quality = "Grade B/C (Conflicting)"

            fno_rows.append({
                "Stock": s.replace(".NS", ""), "Sector": sec_name, "LTP": round(ltp, 2),
                "Change_%": round(ret, 2), "Daily_RS": daily_rs, "Hourly_RS": hourly_rs,
                "RSI": rsi_val, "MACD": macd_stat, "RVOL": rvol, "ORB": orb_stat,
                "MA_Cross": cross, "Trend": "Above" if ltp >= t_ma.iloc[-1] else "Below",
                "Signal_Quality": sig_quality
            })
        except Exception: pass

    df_fno = pd.DataFrame(fno_rows)
    c_f1, c_f2, c_f3 = st.columns([1.5, 1, 1])
    with c_f1: search_fno = st.text_input("🔎 স্টক সার্চ:", key="fno_search")
    with c_f2: sig_filter = st.selectbox("সিগন্যাল গ্রেড ফিল্টার:", ["All", "Grade A+ Only", "Grade A & Above"])
    with c_f3: orb_filter = st.selectbox("ORB ফিল্টার:", ["All", "ORB High Break", "ORB Low Break"])

    filt_fno = df_fno.copy()
    if search_fno: filt_fno = filt_fno[filt_fno["Stock"].str.contains(search_fno.strip().upper(), na=False)]
    if sig_filter == "Grade A+ Only": filt_fno = filt_fno[filt_fno["Signal_Quality"].str.contains("Grade A+")]
    elif sig_filter == "Grade A & Above": filt_fno = filt_fno[filt_fno["Signal_Quality"].str.contains("Grade A")]
    if orb_filter != "All": filt_fno = filt_fno[filt_fno["ORB"] == orb_filter]

    st.dataframe(
        filt_fno.style.map(lambda v: 'color: #10b981; font-weight: bold;' if 'Bullish' in str(v) or v == 'ORB High Break' or (isinstance(v, (int, float)) and v > 0) else ('color: #ef4444; font-weight: bold;' if 'Bearish' in str(v) or v == 'ORB Low Break' or (isinstance(v, (int, float)) and v < 0) else ''), subset=['Daily_RS', 'Hourly_RS', 'Change_%', 'Signal_Quality', 'ORB', 'MACD']),
        use_container_width=True, hide_index=True
    )

# ==============================================================
# TAB 3: SECTOR-WISE SCANNER
# ==============================================================
with tab3:
    st.subheader("🏭 Sector Constituent Drilldown")
    chosen_sec = st.selectbox("সেক্টর বাছুন:", list(SECTOR_MAP.keys()))
    sec_stocks_list = SECTOR_MAP[chosen_sec]["stocks"]
    sec_sub_df = df_fno[df_fno["Stock"].isin([s.replace(".NS", "") for s in sec_stocks_list])].sort_values(by="Daily_RS", ascending=False)
    st.dataframe(
        sec_sub_df.style.map(lambda v: 'color: #10b981; font-weight: bold;' if (isinstance(v, (int, float)) and v > 0) else ('color: #ef4444; font-weight: bold;' if (isinstance(v, (int, float)) and v < 0) else ''), subset=['Daily_RS', 'Hourly_RS', 'Change_%']),
        use_container_width=True, hide_index=True
    )

# ==============================================================
# TAB 4: MOMENTUM TOUCH ENGINE
# ==============================================================
with tab4:
    st.subheader("🎯 Mechanical MA Momentum & Pullback Touch Engine")
    touch_rows = []
    for s in ALL_STOCKS:
        try:
            c = get_col(cut_intra, "Close", s); o = get_col(cut_intra, "Open", s); h = get_col(cut_intra, "High", s); l = get_col(cut_intra, "Low", s)
            if len(c) < max(5, slow_p + 2): continue
            full_c = get_col(intra_data, "Close", s).loc[:cut_time]
            f_ma = calc_ma(full_c, fast_p, ma_kind)
            t_status, t_dir, t_type, mom_val = classify_touch(c, o, h, l, f_ma)
            if t_status == "Touch":
                touch_rows.append({
                    "Stock": s.replace(".NS", ""), "Sector": STOCK_TO_SEC.get(s, "F&O"),
                    "LTP": round(c.iloc[-1], 2), f"Touch_MA_{fast_p}": round(f_ma.iloc[-1], 2),
                    "Touch_Direction": t_dir, "Touch_Setup": t_type, "Prior_Momentum_%": mom_val
                })
        except Exception: pass

    df_touch = pd.DataFrame(touch_rows)
    if not df_touch.empty:
        st.dataframe(df_touch.style.map(lambda v: 'color: #10b981; font-weight: bold;' if 'Bullish' in str(v) else ('color: #ef4444; font-weight: bold;' if 'Bearish' in str(v) else ''), subset=['Touch_Setup']), use_container_width=True, hide_index=True)
    else:
        st.info("বর্তমান ক্যান্ডেলে কোনো স্টকে নির্দিষ্ট টলারেন্সের ভেতর MA Touch ঘটেনি।")

# ==============================================================
# TAB 5: CPR & KEY LEVELS (PIVOT, CAMARILLA, NARROW CPR)
# ==============================================================
with tab5:
    st.subheader("📐 Daily CPR & Key S/R Levels")
    cpr_rows = []
    for s in ALL_STOCKS:
        try:
            hd = get_col(daily_data, "High", s); ld = get_col(daily_data, "Low", s); cd = get_col(daily_data, "Close", s)
            if len(cd) < 5: continue
            H, L, C = hd.iloc[-2], ld.iloc[-2], cd.iloc[-2]
            P = (H + L + C) / 3; BC = (H + L) / 2; TC = 2 * P - BC
            width = abs(TC - BC) / P * 100
            
            # Camarilla Levels
            diff = H - L
            h3 = C + diff * 1.1 / 4; l3 = C - diff * 1.1 / 4
            h4 = C + diff * 1.1 / 2; l4 = C - diff * 1.1 / 2

            tier = "Tier 1 (Narrow <=0.25%)" if width <= 0.25 else ("Tier 2 (<=0.50%)" if width <= 0.50 else "Normal")
            cpr_rows.append({
                "Stock": s.replace(".NS", ""), "Sector": STOCK_TO_SEC.get(s, "F&O"),
                "Pivot": round(P, 2), "BC": round(BC, 2), "TC": round(TC, 2),
                "CPR_Width_%": round(width, 3), "CPR_Tier": tier,
                "Cam_H3 (Breakout)": round(h3, 2), "Cam_L3 (Breakdown)": round(l3, 2),
                "Cam_H4": round(h4, 2), "Cam_L4": round(l4, 2)
            })
        except Exception: pass

    df_cpr = pd.DataFrame(cpr_rows).sort_values(by="CPR_Width_%")
    sel_tier = st.selectbox("CPR টিয়ার ফিল্টার:", ["All", "Tier 1 (Narrow <=0.25%)", "Tier 2 (<=0.50%)"])
    if sel_tier != "All": df_cpr = df_cpr[df_cpr["CPR_Tier"] == sel_tier]
    st.dataframe(df_cpr, use_container_width=True, hide_index=True)

# ==============================================================
# TAB 6: CHART & MULTI-TIMEFRAME ANALYSIS
# ==============================================================
with tab6:
    st.subheader("📈 Multi-Timeframe Confirmation & Interactive Chart")
    sel_chart_stk = st.selectbox("বিশ্লেষণের জন্য স্টক নির্বাচন করুন:", df_fno["Stock"].tolist() if not df_fno.empty else ALL_STOCKS)
    
    if sel_chart_stk:
        tk = sel_chart_stk + ".NS"
        full_stk_c = get_col(intra_data, "Close", tk).loc[:cut_time]
        
        # Multi-Timeframe Resampling (5m, 15m, 30m, 1H)
        tf_data = []
        for tf_name, rule in [("5m", "5min"), ("15m", "15min"), ("30m", "30min"), ("1H", "1h")]:
            res_c = full_stk_c.resample(rule).last().dropna()
            if len(res_c) > 10:
                tf_f = calc_ma(res_c, fast_p, ma_kind).iloc[-1]
                tf_s = calc_ma(res_c, slow_p, ma_kind).iloc[-1]
                tf_rsi = calc_rsi(res_c, 14).iloc[-1]
                tf_trend = "🟢 Bullish" if tf_f > tf_s else "🔴 Bearish"
                tf_data.append({"Timeframe": tf_name, "Trend": tf_trend, "RSI": round(tf_rsi, 1), f"Fast_{fast_p}": round(tf_f, 2), f"Slow_{slow_p}": round(tf_s, 2)})
        
        st.dataframe(pd.DataFrame(tf_data), use_container_width=True, hide_index=True)

        # চার্ট লেয়ার টগলস
        st.markdown("##### 🎛️ চার্ট ইন্ডিকেটর টগল অন/অফ:")
        tg1, tg2, tg3, tg4, tg5, tg6 = st.columns(6)
        with tg1: show_c = st.checkbox("ক্যান্ডেলস্টিক", value=True)
        with tg2: show_fast = st.checkbox(f"Fast {ma_kind} ({fast_p})", value=True)
        with tg3: show_slow = st.checkbox(f"Slow {ma_kind} ({slow_p})", value=True)
        with tg4: show_trend = st.checkbox(f"Trend {ma_kind} ({trend_p})", value=True)
        with tg5: show_vw = st.checkbox("VWAP", value=True)
        with tg6: show_rs = st.checkbox("RS সাবপ্লট", value=True)

        c_s = get_col(cut_intra, "Close", tk)
        o_s = get_col(cut_intra, "Open", tk)
        h_s = get_col(cut_intra, "High", tk)
        l_s = get_col(cut_intra, "Low", tk)
        vw_s = calc_vwap(cut_intra, tk)
        f_s = calc_ma(full_stk_c, fast_p, ma_kind).reindex(c_s.index)
        s_s = calc_ma(full_stk_c, slow_p, ma_kind).reindex(c_s.index)
        t_s = calc_ma(full_stk_c, trend_p, ma_kind).reindex(c_s.index)

        # RS Calculation
        stk_ret_curve = ((c_s - o_s.iloc[0]) / o_s.iloc[0]) * 100
        rs_curve = stk_ret_curve - nifty_ret

        rows_n = 2 if show_rs else 1
        heights = [0.72, 0.28] if show_rs else [1.0]
        fig = make_subplots(rows=rows_n, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=heights, subplot_titles=(f"{sel_chart_stk} প্রাইস ও ইন্ডিকেটর", "Intraday RS Line (Green=Positive / Red=Negative)"))

        if show_c: fig.add_trace(go.Candlestick(x=c_s.index, open=o_s, high=h_s, low=l_s, close=c_s, name="Candles"), row=1, col=1)
        if show_fast: fig.add_trace(go.Scatter(x=f_s.index, y=f_s, mode="lines", name=f"Fast {fast_p}", line=dict(color="#10b981", width=1.5)), row=1, col=1)
        if show_slow: fig.add_trace(go.Scatter(x=s_s.index, y=s_s, mode="lines", name=f"Slow {slow_p}", line=dict(color="#ef4444", width=1.5)), row=1, col=1)
        if show_trend: fig.add_trace(go.Scatter(x=t_s.index, y=t_s, mode="lines", name=f"Trend {trend_p}", line=dict(color="#3b82f6", width=1.5)), row=1, col=1)
        if show_vw and not vw_s.empty: fig.add_trace(go.Scatter(x=vw_s.index, y=vw_s, mode="lines", name="VWAP", line=dict(color="#f59e0b", width=1.5)), row=1, col=1)

        if show_rs:
            pos_rs = rs_curve.where(rs_curve >= 0)
            neg_rs = rs_curve.where(rs_curve < 0)
            fig.add_trace(go.Scatter(x=rs_curve.index, y=pos_rs, mode="lines", name="RS Positive", line=dict(color="#10b981", width=2)), row=2, col=1)
            fig.add_trace(go.Scatter(x=rs_curve.index, y=neg_rs, mode="lines", name="RS Negative", line=dict(color="#ef4444", width=2)), row=2, col=1)
            fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", row=2, col=1)

        fig.update_layout(height=650, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark", xaxis_rangeslider_visible=False, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# TAB 7: RISK MANAGEMENT CALCULATOR
# ==============================================================
with tab7:
    st.subheader("🛡️ Institutional Risk Management & Position Size Calculator")
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1: capital = st.number_input("ট্রেডিং ক্যাপিটাল (INR):", min_value=10000, value=200000, step=10000)
    with rc2: risk_pct = st.number_input("রিস্ক পার ট্রেড (%):", min_value=0.25, max_value=3.0, value=1.0, step=0.25)
    with rc3: target_rr = st.number_input("রিস্ক-টু-রিওয়ার্ড রেশিও (1 : X):", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
    with rc4: max_daily_loss = st.number_input("সর্বোচ্চ দৈনিক লস লিমিট (INR):", min_value=1000, value=6000, step=500)

    total_risk_val = capital * (risk_pct / 100)
    st.info(f"💡 আপনার ক্যাপিটালে প্রতি ট্রেডে সর্বোচ্চ রিস্ক: **₹{total_risk_val:.2f}** | দৈনিক লস লিমিট: **₹{max_daily_loss:.2f}**")

    risk_table = []
    for s in ALL_STOCKS[:30]:  # শীর্ষ ৩০ স্টকের প্রিভিউ
        try:
            h = get_col(cut_intra, "High", s); l = get_col(cut_intra, "Low", s); c = get_col(cut_intra, "Close", s)
            if len(c) < 15: continue
            atr_v = calc_atr(h, l, c, 14).iloc[-1]
            ltp = c.iloc[-1]
            sl_dist = atr_v * 1.5
            pos_size = int(total_risk_val / sl_dist) if sl_dist > 0 else 0
            risk_table.append({
                "Stock": s.replace(".NS", ""), "LTP": round(ltp, 2), "Intraday_ATR": round(atr_v, 2),
                "Stop Loss (INR)": round(ltp - sl_dist, 2), "Target (INR)": round(ltp + (sl_dist * target_rr), 2),
                "Position Size (Qty)": pos_size, "Total Trade Value": round(pos_size * ltp, 2)
            })
        except Exception: pass

    st.dataframe(pd.DataFrame(risk_table), use_container_width=True, hide_index=True)

# ==============================================================
# TAB 8: INTRADAY 2-MONTH BACKTEST ENGINE
# ==============================================================
with tab8:
    st.subheader("🧪 Mechanical Intraday Strategy Backtest Engine")
    st.caption("ইন্ট্রাডে ডেটার ওপর স্লিপেজ এবং ব্রোকারেজ ফি অন্তর্ভুক্ত করে মেকানিক্যাল এন্ট্রি/এক্সিট পারফরম্যান্স টেস্ট।")

    bc1, bc2, bc3 = st.columns(3)
    with bc1: test_stk = st.selectbox("ব্যাকটেস্ট স্টক নির্বাচন:", ALL_STOCKS)
    with bc2: brokerage_per_trade = st.number_input("ব্রোকারেজ ও ট্যাক্স (INR / Trade):", value=40, step=5)
    with bc3: slippage_pct = st.number_input("স্লিপেজ (%):", value=0.05, step=0.01)

    if st.button("🚀 ব্যাকটেস্ট এক্সিকিউট করুন"):
        with st.spinner("সিমুলেশন চলছে..."):
            bt_c = get_col(intra_data, "Close", test_stk)
            bt_o = get_col(intra_data, "Open", test_stk)
            bt_f = calc_ma(bt_c, fast_p, ma_kind)
            bt_s = calc_ma(bt_c, slow_p, ma_kind)

            trades = []
            position = 0
            entry_price = 0

            for i in range(1, len(bt_c)):
                # Golden Cross Buy Signal
                if position == 0 and bt_f.iloc[i] > bt_s.iloc[i] and bt_f.iloc[i-1] <= bt_s.iloc[i-1]:
                    position = 1
                    entry_price = bt_c.iloc[i] * (1 + slippage_pct / 100)
                    entry_time = bt_c.index[i]
                # Death Cross Sell / Square-off
                elif position == 1 and (bt_f.iloc[i] < bt_s.iloc[i] and bt_f.iloc[i-1] >= bt_s.iloc[i-1] or bt_c.index[i].time() >= time(15, 15)):
                    exit_price = bt_c.iloc[i] * (1 - slippage_pct / 100)
                    pnl = (exit_price - entry_price) - (brokerage_per_trade / 50)
                    trades.append({"Entry Time": entry_time, "Exit Time": bt_c.index[i], "Entry": round(entry_price, 2), "Exit": round(exit_price, 2), "Net PnL": round(pnl, 2)})
                    position = 0

            df_trades = pd.DataFrame(trades)
            if not df_trades.empty:
                win_trades = len(df_trades[df_trades["Net PnL"] > 0])
                total_trades = len(df_trades)
                win_rate = (win_trades / total_trades) * 100
                total_pnl = df_trades["Net PnL"].sum()

                m1, m2, m3 = st.columns(3)
                with m1: st.metric("Total Trades", total_trades)
                with m2: st.metric("Win Rate", f"{win_rate:.1f}%")
                with m3: st.metric("Net Cumulative PnL", f"₹{total_pnl:.2f}")

                st.dataframe(df_trades.style.map(lambda v: 'color: #10b981;' if v > 0 else 'color: #ef4444;', subset=['Net PnL']), use_container_width=True, hide_index=True)
            else:
                st.warning("উক্ত টাইমফ্রেমে কোনো ট্রেড ট্রিগার হয়নি।")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Top-Down F&O RS & Intraday Engine", page_icon="⚡", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); padding: 16px; border-radius: 12px; color: white; margin-bottom: 20px;">
    <h2 style="margin: 0; font-size: 24px;">⚡ TOP-DOWN RS, CPR, VWAP & DUAL EMA SCANNER</h2>
    <p style="margin: 4px 0 0 0; opacity: 0.85; font-size: 13px;">Live Market ⬩ F&O Universe ⬩ Dynamic Crossover Alerts ⬩ Full F&O Filter & Search</p>
</div>
""", unsafe_allow_html=True)

# ১. সম্পূর্ণ F&O সেক্টর ও স্টক ম্যাপিং
SECTOR_MAP = {
    "METAL": {
        "ticker": "^CNXMETAL",
        "stocks": ["TATASTEEL.NS", "JSL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", "SAIL.NS", "NMDC.NS", "NATIONALUM.NS"]
    },
    "AUTO": {
        "ticker": "^CNXAUTO",
        "stocks": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS"]
    },
    "BANK": {
        "ticker": "^NSEBANK",
        "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS", "BANDHANBNK.NS", "AUBANK.NS"]
    },
    "IT": {
        "ticker": "^CNXIT",
        "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "COFORGE.NS", "PERSISTENT.NS"]
    },
    "PHARMA": {
        "ticker": "^CNXPHARMA",
        "stocks": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS"]
    },
    "ENERGY": {
        "ticker": "^CNXENERGY",
        "stocks": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS", "COALINDIA.NS", "IOC.NS", "GAIL.NS"]
    },
    "FMCG": {
        "ticker": "^CNXFMCG",
        "stocks": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "DABUR.NS", "GODREJCP.NS"]
    }
}

ALL_STOCKS = sorted(list(set([stk for sec in SECTOR_MAP.values() for stk in sec["stocks"]])))
STOCK_TO_SECTOR = {stk: sec for sec, val in SECTOR_MAP.items() for stk in val["stocks"]}

# ২. ডেটা লোড ফাংশন
@st.cache_data(ttl=60)
def fetch_data(tickers):
    df = yf.download(tickers, period="5d", interval="5m", progress=False)
    if df.empty:
        return df
    if df.index.tz is not None:
        df = df.tz_convert("Asia/Kolkata")
    else:
        df = df.tz_localize("UTC").tz_convert("Asia/Kolkata")
    return df

@st.cache_data(ttl=300)
def fetch_daily_data(tickers):
    return yf.download(tickers, period="1mo", interval="1d", progress=False)

# সাইডবার কন্ট্রোল প্যানেল
st.sidebar.header("⚙️ কন্ট্রোল প্যানেল")
mode = st.sidebar.radio("অপারেশন মোড:", [
    "🔴 Live Market (Sector Scope)", 
    "⏪ Historical Replay (Backtest)", 
    "🔍 F&O All Stocks Scanner"
])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Crossover EMA সেটিংস (5m)")
fast_ema_val = st.sidebar.number_input("Fast EMA পিরিয়ড:", min_value=3, max_value=100, value=13, step=1)
slow_ema_val = st.sidebar.number_input("Slow EMA পিরিয়ড:", min_value=5, max_value=200, value=21, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Trend Filter EMA (Intraday)")
trend_ema_val = st.sidebar.number_input("Trend EMA (যেমন: 50, 100, 200):", min_value=10, max_value=500, value=50, step=1)

# ডেটা ফেচ
all_indices = ["^NSEI"] + [v["ticker"] for v in SECTOR_MAP.values()]
with st.spinner("⏳ মার্কেট ডেটা প্রসেস হচ্ছে..."):
    idx_raw = fetch_data(all_indices)
    all_stk_raw = fetch_data(ALL_STOCKS)
    daily_raw = fetch_daily_data(ALL_STOCKS)

available_dates = sorted(list(set(idx_raw.index.date)), reverse=True)

if mode in ["🔴 Live Market (Sector Scope)", "🔍 F&O All Stocks Scanner"]:
    target_date = available_dates[0]
    sub_df = idx_raw[idx_raw.index.date == target_date]
    target_timestamp = sub_df.index[-1]
    st.sidebar.success(f"Snapshot Time: {target_timestamp.strftime('%d-%b-%Y %H:%M')}")
else:
    target_date = st.sidebar.selectbox("তারিখ বাছুন:", available_dates)
    sub_df = idx_raw[idx_raw.index.date == target_date]
    day_times = sorted(list(set([t.time() for t in sub_df.index])))
    selected_time = st.sidebar.select_slider(
        "সময় স্লাইডার:", options=day_times, value=day_times[len(day_times)//2], format_func=lambda x: x.strftime("%H:%M")
    )
    target_timestamp = pd.Timestamp.combine(target_date, selected_time).tz_localize("Asia/Kolkata")

# নিফটি রিটার্ন
cut_idx = sub_df[sub_df.index <= target_timestamp]
nifty_open = cut_idx["Open"]["^NSEI"].dropna().iloc[0]
nifty_ltp = cut_idx["Close"]["^NSEI"].dropna().iloc[-1]
nifty_ret = ((nifty_ltp - nifty_open) / nifty_open) * 100

st.markdown(f"### 📍 Snapshot: `{target_timestamp.strftime('%d-%b-%Y %I:%M %p')}` | Nifty 50: **{nifty_ret:+.2f}%** ({'🟢 BULLISH' if nifty_ret >= 0 else '🔴 BEARISH'})")

stk_sub = all_stk_raw[all_stk_raw.index.date == target_date]
stk_cut = stk_sub[stk_sub.index <= target_timestamp]

# ==============================================================
# মোড ৩: F&O ALL STOCKS SCANNER (আলাদা ইন্টারফেস)
# ==============================================================
if mode == "🔍 F&O All Stocks Scanner":
    st.markdown("---")
    st.subheader("🌐 সম্পূর্ণ F&O ইউনিভার্স স্ক্যানার ও ফিল্টার")

    all_res = []
    for s in ALL_STOCKS:
        try:
            c_series = stk_cut["Close"][s].dropna()
            if len(c_series) < 2:
                continue
            stk_open = stk_cut["Open"][s].dropna().iloc[0]
            stk_ltp = c_series.iloc[-1]
            stk_ret = ((stk_ltp - stk_open) / stk_open) * 100
            rs_score = round(stk_ret - nifty_ret, 2)
            clean_name = s.replace(".NS", "")

            # VWAP
            vol_series = stk_cut["Volume"][s].dropna()
            h_series = stk_cut["High"][s].dropna()
            l_series = stk_cut["Low"][s].dropna()
            typical_price = (h_series + l_series + c_series) / 3
            cum_vp = (typical_price * vol_series).cumsum()
            cum_vol = vol_series.cumsum()
            vwap = (cum_vp / cum_vol).iloc[-1]
            vwap_status = "Above" if stk_ltp >= vwap else "Below"

            # CPR
            d_hist = daily_raw["Close"][s].dropna()
            d_idx = d_hist.index[d_hist.index.date < target_date]
            if len(d_idx) > 0:
                prev_day = d_idx[-1]
                prev_high = daily_raw["High"][s].loc[prev_day]
                prev_low = daily_raw["Low"][s].loc[prev_day]
                prev_close = daily_raw["Close"][s].loc[prev_day]
                pivot = (prev_high + prev_low + prev_close) / 3
                bc = (prev_high + prev_low) / 2
                tc = (pivot - bc) + pivot
                cpr_top = max(tc, bc)
                cpr_bottom = min(tc, bc)
                if stk_ltp > cpr_top:
                    cpr_status = "Above CPR"
                elif stk_ltp < cpr_bottom:
                    cpr_status = "Below CPR"
                else:
                    cpr_status = "Inside CPR"
            else:
                cpr_status = "N/A"

            # Trend EMA
            all_c = all_stk_raw["Close"][s].dropna().loc[:target_timestamp]
            trend_series = all_c.ewm(span=trend_ema_val, adjust=False).mean()
            trend_val = trend_series.iloc[-1]
            trend_status = "Above" if stk_ltp >= trend_val else "Below"

            # Crossover
            fast_ema = all_c.ewm(span=fast_ema_val, adjust=False).mean()
            slow_ema = all_c.ewm(span=slow_ema_val, adjust=False).mean()
            f_curr, f_prev = fast_ema.iloc[-1], fast_ema.iloc[-2]
            s_curr, s_prev = slow_ema.iloc[-1], slow_ema.iloc[-2]

            if f_curr > s_curr and f_prev <= s_prev:
                cross_event = "Golden Cross"
            elif f_curr < s_curr and f_prev >= s_prev:
                cross_event = "Death Cross"
            elif f_curr > s_curr:
                cross_event = "Bullish Trend"
            else:
                cross_event = "Bearish Trend"

            all_res.append({
                "Stock": clean_name,
                "Sector": STOCK_TO_SECTOR.get(s, "F&O"),
                "LTP": round(stk_ltp, 2),
                "Change_%": round(stk_ret, 2),
                "RS_Score": rs_score,
                "VWAP": vwap_status,
                "CPR": cpr_status,
                f"Trend_{trend_ema_val}EMA": trend_status,
                "EMA_Event": cross_event
            })
        except:
            pass

    full_fno_df = pd.DataFrame(all_res)

    # সার্চ এবং ফিল্টার কন্ট্রোল
    fc1, fc2, fc3, fc4, fc5 = st.columns([1.5, 1, 1, 1, 1.2])

    with fc1:
        search_query = st.text_input("🔎 স্টক সার্চ করুন:", placeholder="যেমন: TATASTEEL, RELIANCE...")

    with fc2:
        vwap_filter = st.selectbox("VWAP ফিল্টার:", ["All", "Above", "Below"])

    with fc3:
        cpr_filter = st.selectbox("CPR ফিল্টার:", ["All", "Above CPR", "Inside CPR", "Below CPR"])

    with fc4:
        trend_filter = st.selectbox(f"{trend_ema_val} EMA ফিল্টার:", ["All", "Above", "Below"])

    with fc5:
        cross_filter = st.selectbox("EMA সিগন্যাল / ক্রসওভার:", [
            "All", 
            "Golden Cross", 
            "Death Cross", 
            "Bullish Trend", 
            "Bearish Trend"
        ])

    filtered_df = full_fno_df.copy()

    if search_query:
        filtered_df = filtered_df[filtered_df["Stock"].str.contains(search_query.strip().upper(), na=False)]

    if vwap_filter != "All":
        filtered_df = filtered_df[filtered_df["VWAP"] == vwap_filter]

    if cpr_filter != "All":
        filtered_df = filtered_df[filtered_df["CPR"] == cpr_filter]

    if trend_filter != "All":
        filtered_df = filtered_df[filtered_df[f"Trend_{trend_ema_val}EMA"] == trend_filter]

    if cross_filter != "All":
        filtered_df = filtered_df[filtered_df["EMA_Event"] == cross_filter]

    st.markdown(f"**ফিল্টার করা স্টক সংখ্যা:** `{len(filtered_df)}` টি")

    display_df = filtered_df.copy()
    display_df["VWAP"] = display_df["VWAP"].apply(lambda x: "🟢 Above" if x == "Above" else "🔴 Below")
    display_df["CPR"] = display_df["CPR"].apply(lambda x: "🟢 Above CPR" if x == "Above CPR" else ("🔴 Below CPR" if x == "Below CPR" else "🟡 Inside CPR"))
    display_df[f"Trend_{trend_ema_val}EMA"] = display_df[f"Trend_{trend_ema_val}EMA"].apply(lambda x: f"🟢 Above {trend_ema_val}" if x == "Above" else f"🔴 Below {trend_ema_val}")
    display_df["EMA_Event"] = display_df["EMA_Event"].apply(lambda x: "🚀 Golden Cross" if x == "Golden Cross" else ("⚠️ Death Cross" if x == "Death Cross" else ("🟢 Bullish" if x == "Bullish Trend" else "🔴 Bearish")))

    st.dataframe(
        display_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if v > 0 else 'color: #e74c3c;', subset=['Change_%', 'RS_Score']),
        use_container_width=True,
        hide_index=True
    )

# ==============================================================
# মোড ১ ও ২: SECTOR SCOPE & HISTORICAL REPLAY
# ==============================================================
else:
    sec_list = []
    for s_name, s_info in SECTOR_MAP.items():
        try:
            sym = s_info["ticker"]
            s_open = cut_idx["Open"][sym].dropna().iloc[0]
            s_ltp = cut_idx["Close"][sym].dropna().iloc[-1]
            s_ret = ((s_ltp - s_open) / s_open) * 100
            sec_list.append({"Sector": s_name, "Return_%": round(s_ret, 2), "R_Factor": round(s_ret - nifty_ret, 2)})
        except:
            pass

    sec_df = pd.DataFrame(sec_list).sort_values(by="R_Factor", ascending=False).reset_index(drop=True)

    col_sec, col_trend = st.columns([1.1, 1.9])

    with col_sec:
        st.subheader("🏆 Sector Selection")
        selected_sector = st.radio(
            "Choose Primary Sector:",
            sec_df["Sector"].tolist(),
            index=0,
            horizontal=True
        )
        st.dataframe(
            sec_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if v > 0 else 'color: #e74c3c;', subset=['R_Factor']),
            use_container_width=True,
            hide_index=True
        )

    with col_trend:
        st.subheader("📈 Sector Trend Graph (Locked)")
        if "locked_sectors" not in st.session_state:
            st.session_state.locked_sectors = [selected_sector]

        if selected_sector not in st.session_state.locked_sectors:
            st.session_state.locked_sectors.append(selected_sector)

        chosen_sectors = st.multiselect(
            "Visible Sectors in Chart:",
            options=list(SECTOR_MAP.keys()),
            default=st.session_state.locked_sectors,
            key="sector_ms"
        )
        st.session_state.locked_sectors = chosen_sectors

        fig_sec = go.Figure()
        for sec in chosen_sectors:
            sec_sym = SECTOR_MAP[sec]["ticker"]
            if sec_sym in cut_idx["Close"]:
                sec_series = cut_idx["Close"][sec_sym].dropna()
                sec_open_val = cut_idx["Open"][sec_sym].dropna().iloc[0]
                if len(sec_series) > 0:
                    sec_trend = ((sec_series - sec_open_val) / sec_open_val) * 100
                    fig_sec.add_trace(go.Scatter(x=sec_trend.index, y=sec_trend, mode='lines', name=sec))

        fig_sec.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True, title="% Return"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_sec, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': False})

    sector_ret = sec_df[sec_df["Sector"] == selected_sector]["Return_%"].values[0]
    stock_tickers = SECTOR_MAP[selected_sector]["stocks"]

    stock_res = []
    sector_crossovers = []

    for s in stock_tickers:
        try:
            c_series = stk_cut["Close"][s].dropna()
            stk_open = stk_cut["Open"][s].dropna().iloc[0]
            stk_ltp = c_series.iloc[-1]
            stk_ret = ((stk_ltp - stk_open) / stk_open) * 100
            rs_vs_nifty = stk_ret - nifty_ret
            rs_vs_sector = stk_ret - sector_ret
            dual_score = round(rs_vs_nifty + rs_vs_sector, 2)
            clean_name = s.replace(".NS", "")

            # VWAP
            vol_series = stk_cut["Volume"][s].dropna()
            h_series = stk_cut["High"][s].dropna()
            l_series = stk_cut["Low"][s].dropna()
            typical_price = (h_series + l_series + c_series) / 3
            cum_vp = (typical_price * vol_series).cumsum()
            cum_vol = vol_series.cumsum()
            vwap = (cum_vp / cum_vol).iloc[-1]
            vwap_status = "🟢 Above" if stk_ltp >= vwap else "🔴 Below"

            # CPR
            d_hist = daily_raw["Close"][s].dropna()
            d_idx = d_hist.index[d_hist.index.date < target_date]
            if len(d_idx) > 0:
                prev_day = d_idx[-1]
                prev_high = daily_raw["High"][s].loc[prev_day]
                prev_low = daily_raw["Low"][s].loc[prev_day]
                prev_close = daily_raw["Close"][s].loc[prev_day]
                pivot = (prev_high + prev_low + prev_close) / 3
                bc = (prev_high + prev_low) / 2
                tc = (pivot - bc) + pivot
                cpr_top = max(tc, bc)
                cpr_bottom = min(tc, bc)
                cpr_status = "🟢 Above CPR" if stk_ltp > cpr_top else ("🔴 Below CPR" if stk_ltp < cpr_bottom else "🟡 Inside CPR")
            else:
                cpr_status = "N/A"

            # Trend EMA
            all_close = all_stk_raw["Close"][s].dropna().loc[:target_timestamp]
            trend_val = all_close.ewm(span=trend_ema_val, adjust=False).mean().iloc[-1]
            trend_status = f"🟢 Above {trend_ema_val} EMA" if stk_ltp >= trend_val else f"🔴 Below {trend_ema_val} EMA"

            # Crossover Check
            fast_ema = all_close.ewm(span=fast_ema_val, adjust=False).mean()
            slow_ema = all_close.ewm(span=slow_ema_val, adjust=False).mean()
            f_curr, f_prev = fast_ema.iloc[-1], fast_ema.iloc[-2]
            s_curr, s_prev = slow_ema.iloc[-1], slow_ema.iloc[-2]

            if f_curr > s_curr and f_prev <= s_prev:
                sector_crossovers.append({
                    "Stock": clean_name,
                    "LTP": round(stk_ltp, 2),
                    "Dual_RS": dual_score,
                    "Event": "🚀 Golden Cross",
                    "VWAP": vwap_status,
                    "CPR": cpr_status
                })
            elif f_curr < s_curr and f_prev >= s_prev:
                sector_crossovers.append({
                    "Stock": clean_name,
                    "LTP": round(stk_ltp, 2),
                    "Dual_RS": dual_score,
                    "Event": "⚠️ Death Cross",
                    "VWAP": vwap_status,
                    "CPR": cpr_status
                })

            stock_res.append({
                "Stock": clean_name,
                "LTP": round(stk_ltp, 2),
                "Change_%": round(stk_ret, 2),
                "Dual_Score": dual_score,
                "VWAP": vwap_status,
                "CPR": cpr_status,
                f"Trend ({trend_ema_val} EMA)": trend_status
            })
        except:
            pass

    stk_df = pd.DataFrame(stock_res).sort_values(by="Dual_Score", ascending=False).reset_index(drop=True)

    # সরু বার চার্ট ও মাল্টি-স্টক লাইন চার্ট
    st.markdown("---")
    col_chart_left, col_chart_right = st.columns([1.1, 1.9])

    with col_chart_left:
        st.markdown("#### 🔥 Focus Stocks (Dual RS)")
        if not stk_df.empty:
            top_picks = stk_df.head(2)["Stock"].tolist()
            st.caption(f"Top Focus: `{top_picks[0]}` | `{top_picks[1]}`")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=stk_df["Stock"],
                y=stk_df["Dual_Score"],
                width=0.38,
                marker_color=["#27ae60" if x >= 0 else "#e74c3c" for x in stk_df["Dual_Score"]],
                text=[f"{val:+.2f}" for val in stk_df["Dual_Score"]],
                textposition="outside"
            ))
            fig_bar.update_layout(
                height=280, 
                margin=dict(l=10, r=10, t=15, b=10), 
                xaxis=dict(fixedrange=True, tickangle=-45),
                yaxis=dict(fixedrange=True, title="RS Score")
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    with col_chart_right:
        st.markdown("#### 📊 Multi-Stock RS Trend")
        available_stock_names = stk_df["Stock"].tolist()
        default_selected_stocks = available_stock_names[:2] if len(available_stock_names) >= 2 else available_stock_names

        selected_chart_stocks = st.multiselect(
            "Select stocks to plot:",
            options=available_stock_names,
            default=default_selected_stocks,
            key="multi_stock_ms"
        )

        fig_multi = go.Figure()
        for s_name in selected_chart_stocks:
            ticker_sym = s_name + ".NS"
            try:
                s_series = stk_cut["Close"][ticker_sym].dropna()
                s_open_val = stk_cut["Open"][ticker_sym].dropna().iloc[0]
                if len(s_series) > 0:
                    stk_pct = ((s_series - s_open_val) / s_open_val) * 100
                    fig_multi.add_trace(go.Scatter(x=stk_pct.index, y=stk_pct, mode='lines', name=s_name))
            except:
                pass

        fig_multi.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=15, b=10),
            xaxis=dict(fixedrange=True, title="Time"),
            yaxis=dict(fixedrange=True, title="% Return"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_multi, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': False})

    # টেকনিক্যাল টেবিল (ফুল ভিউ)
    st.markdown("---")
    st.subheader(f"📋 {selected_sector} F&O Intraday Technical Table (Full View)")
    st.dataframe(
        stk_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if v > 0 else 'color: #e74c3c;', subset=['Change_%', 'Dual_Score']),
        use_container_width=True,
        hide_index=True
    )

    # ডুয়াল ক্রসওভার টেবিল
    st.markdown("---")
    st.subheader(f"⚡ Crossover Scanner on Current 5m Candle ({fast_ema_val} & {slow_ema_val} EMA)")

    all_fno_crossovers = []
    for s in ALL_STOCKS:
        try:
            all_c = all_stk_raw["Close"][s].dropna().loc[:target_timestamp]
            if len(all_c) >= 2:
                f_s = all_c.ewm(span=fast_ema_val, adjust=False).mean()
                s_s = all_c.ewm(span=slow_ema_val, adjust=False).mean()
                f_c, f_p = f_s.iloc[-1], f_s.iloc[-2]
                s_c, s_p = s_s.iloc[-1], s_s.iloc[-2]
                clean = s.replace(".NS", "")
                s_open = stk_cut["Open"][s].dropna().iloc[0] if s in stk_cut["Open"] else all_c.iloc[0]
                stk_ltp = all_c.iloc[-1]
                stk_ret = ((stk_ltp - s_open) / s_open) * 100
                rs_score = round(stk_ret - nifty_ret, 2)
                
                if f_c > s_c and f_p <= s_p:
                    all_fno_crossovers.append({
                        "Stock": clean,
                        "Sector": STOCK_TO_SECTOR.get(s, "F&O"),
                        "LTP": round(stk_ltp, 2),
                        "RS_Score": rs_score,
                        "Event": "🚀 Golden Cross"
                    })
                elif f_c < s_c and f_p >= s_p:
                    all_fno_crossovers.append({
                        "Stock": clean,
                        "Sector": STOCK_TO_SECTOR.get(s, "F&O"),
                        "LTP": round(stk_ltp, 2),
                        "RS_Score": rs_score,
                        "Event": "⚠️ Death Cross"
                    })
        except:
            pass

    col_cross_sec, col_cross_all = st.columns(2)

    with col_cross_sec:
        st.markdown(f"#### 🎯 Current Sector Alerts (`{selected_sector}`)")
        if sector_crossovers:
            sec_cross_df = pd.DataFrame(sector_crossovers)
            st.dataframe(
                sec_cross_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if 'Golden' in str(v) else ('color: #e74c3c; font-weight: bold;' if 'Death' in str(v) else ''), subset=['Event']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"এই সেক্টরে বর্তমান ক্যান্ডেলে কোনো Cross নেই।")

    with col_cross_all:
        st.markdown("#### 🌐 All F&O Market Crossover Alerts")
        if all_fno_crossovers:
            all_cross_df = pd.DataFrame(all_fno_crossovers)
            st.dataframe(
                all_cross_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if 'Golden' in str(v) else ('color: #e74c3c; font-weight: bold;' if 'Death' in str(v) else ''), subset=['Event']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"সম্পূর্ণ F&O মার্কেটে বর্তমান ক্যান্ডেলে কোনো Cross নেই।")

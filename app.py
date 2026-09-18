import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Top-Down RS & Nifty 50 All-Stock Engine", page_icon="⚡", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); padding: 16px; border-radius: 12px; color: white; margin-bottom: 20px;">
    <h2 style="margin: 0; font-size: 24px;">📊 TOP-DOWN RS & NIFTY 50 ALL-STOCK ENGINE</h2>
    <p style="margin: 4px 0 0 0; opacity: 0.85; font-size: 13px;">Live Market ⬩ Historical Replay ⬩ Full Nifty 50 Universe Scanner</p>
</div>
""", unsafe_allow_html=True)

# ১. নিফটি ৫০ সম্পূর্ণ স্টক তালিকা
NIFTY_50_TICKERS = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS",
    "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", "INFY.NS",
    "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS",
    "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS",
    "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TATACONSUM.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "WIPRO.NS", "BEL.NS", "TRENT.NS", "SHRIRAMFIN.NS"
]

SECTOR_MAP = {
    "AUTO": {"ticker": "^CNXAUTO", "stocks": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS"]},
    "BANK": {"ticker": "^NSEBANK", "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS"]},
    "IT": {"ticker": "^CNXIT", "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"]},
    "METAL": {"ticker": "^CNXMETAL", "stocks": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS"]},
    "FMCG": {"ticker": "^CNXFMCG", "stocks": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS"]},
    "PHARMA": {"ticker": "^CNXPHARMA", "stocks": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS"]},
    "ENERGY": {"ticker": "^CNXENERGY", "stocks": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS", "COALINDIA.NS"]}
}

@st.cache_data(ttl=600)
def fetch_data(tickers):
    df = yf.download(tickers, period="60d", interval="5m", progress=False)
    if df.index.tz is not None:
        df = df.tz_convert("Asia/Kolkata")
    else:
        df = df.tz_localize("UTC").tz_convert("Asia/Kolkata")
    return df

# সাইডবার মেনু
st.sidebar.header("⚙️ কন্ট্রোল প্যানেল")
mode = st.sidebar.radio(
    "মোড বেছে নিন:",
    ["🔴 Live Market (Sector Scope)", "⏪ Historical Replay (Backtest)", "📋 Nifty 50 All Stocks (সব ৫০টি স্টক)"]
)

# ইনডেক্স ফেচ
all_indices = ["^NSEI"] + [v["ticker"] for v in SECTOR_MAP.values()]
with st.spinner("⏳ ইনডেক্স ডেটা লোড হচ্ছে..."):
    idx_raw = fetch_data(all_indices)

available_dates = sorted(list(set(idx_raw.index.date)), reverse=True)

# সময় ও তারিখ নির্ধারণ
if mode == "🔴 Live Market (Sector Scope)":
    target_date = available_dates[0]
    sub_df = idx_raw[idx_raw.index.date == target_date]
    target_timestamp = sub_df.index[-1]
    st.sidebar.success(f"লাইভ সময়: {target_timestamp.strftime('%d-%b-%Y %H:%M')}")
elif mode == "⏪ Historical Replay (Backtest)":
    target_date = st.sidebar.selectbox("তারিখ বাছুন:", available_dates)
    sub_df = idx_raw[idx_raw.index.date == target_date]
    day_times = sorted(list(set([t.time() for t in sub_df.index])))
    selected_time = st.sidebar.select_slider(
        "সময় স্লাইডার:", options=day_times, value=day_times[len(day_times)//2], format_func=lambda x: x.strftime("%H:%M")
    )
    target_timestamp = pd.Timestamp.combine(target_date, selected_time).tz_localize("Asia/Kolkata")
else:
    # Nifty 50 All Stocks Mode
    time_choice = st.sidebar.radio("ডেটার ধরন:", ["সরাসরি লাইভ (Latest)", "অতীতের কোনো তারিখ (Backtest)"])
    if time_choice == "সরাসরি লাইভ (Latest)":
        target_date = available_dates[0]
        sub_df = idx_raw[idx_raw.index.date == target_date]
        target_timestamp = sub_df.index[-1]
    else:
        target_date = st.sidebar.selectbox("তারিখ বাছুন:", available_dates)
        sub_df = idx_raw[idx_raw.index.date == target_date]
        day_times = sorted(list(set([t.time() for t in sub_df.index])))
        selected_time = st.sidebar.select_slider(
            "সময় বাছুন:", options=day_times, value=day_times[-1], format_func=lambda x: x.strftime("%H:%M")
        )
        target_timestamp = pd.Timestamp.combine(target_date, selected_time).tz_localize("Asia/Kolkata")

# নিফটি রিটার্ন
cut_idx = sub_df[sub_df.index <= target_timestamp]
nifty_open = cut_idx["Open"]["^NSEI"].dropna().iloc[0]
nifty_ltp = cut_idx["Close"]["^NSEI"].dropna().iloc[-1]
nifty_ret = ((nifty_ltp - nifty_open) / nifty_open) * 100

st.markdown(f"### 📍 Snapshot: `{target_timestamp.strftime('%d-%b-%Y %I:%M %p')}` | Nifty 50: **{nifty_ret:+.2f}%** ({'🟢 BULLISH' if nifty_ret >= 0 else '🔴 BEARISH'})")

# মোড ৩: নিফটি ৫০ সম্পূর্ণ স্টক স্ক্যানার
if mode == "📋 Nifty 50 All Stocks (সব ৫০টি স্টক)":
    with st.spinner("⏳ নিফটি ৫০-এর সমস্ত স্টক ফেচ ও ক্যালকুলেট করা হচ্ছে..."):
        all_stk_raw = fetch_data(NIFTY_50_TICKERS)
        stk_sub = all_stk_raw[all_stk_raw.index.date == target_date]
        stk_cut = stk_sub[stk_sub.index <= target_timestamp]

    all_res = []
    for s in NIFTY_50_TICKERS:
        try:
            o = stk_cut["Open"][s].dropna().iloc[0]
            c = stk_cut["Close"][s].dropna().iloc[-1]
            ret = ((c - o) / o) * 100
            rs = ret - nifty_ret
            all_res.append({
                "Stock": s.replace(".NS", ""),
                "LTP": round(c, 2),
                "Change_%": round(ret, 2),
                "RS vs Nifty": round(rs, 2),
                "Signal": "🟢 Leader" if rs > 0 else "🔴 Laggard"
            })
        except:
            pass

    full_df = pd.DataFrame(all_res).sort_values(by="RS vs Nifty", ascending=False).reset_index(drop=True)

    # শীর্ষ ৫ বুলিশ ও শীর্ষ ৫ বেয়ারিশ হাইলাইট
    col_top, col_bottom = st.columns(2)
    with col_top:
        st.success("🔥 **Top 5 Outperformers (সবচেয়ে শক্তিশালী ৫টি স্টক)**")
        st.dataframe(full_df.head(5)[["Stock", "LTP", "Change_%", "RS vs Nifty"]], use_container_width=True, hide_index=True)
    with col_bottom:
        st.error("❄️ **Top 5 Underperformers (সবচেয়ে দুর্বল ৫টি স্টক)**")
        st.dataframe(full_df.tail(5)[["Stock", "LTP", "Change_%", "RS vs Nifty"]], use_container_width=True, hide_index=True)

    st.subheader("🌐 নিফটি ৫০ সম্পূর্ণ স্টক তালিকা (RS র‍্যাঙ্কিং অনুযায়ী সাজানো)")
    st.dataframe(
        full_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if v > 0 else 'color: #e74c3c;', subset=['Change_%', 'RS vs Nifty']),
        use_container_width=True,
        hide_index=True
    )

# মোড ১ ও ২: সেক্টর স্কোপ ও ড্রিলডাউন
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

    col_sec, col_stocks = st.columns([1.1, 1.9])
    with col_sec:
        st.subheader("🏆 সেক্টর স্কোপ র‍্যাঙ্কিং")
        st.dataframe(
            sec_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if v > 0 else 'color: #e74c3c;', subset=['R_Factor']),
            use_container_width=True,
            hide_index=True
        )
        selected_sector = st.selectbox("🔍 স্টক ড্রিলডাউন সেক্টর:", sec_df["Sector"].tolist(), index=0)

    with col_stocks:
        st.subheader(f"🎯 {selected_sector} সেক্টর Dual R-Factor")
        sector_ret = sec_df[sec_df["Sector"] == selected_sector]["Return_%"].values[0]
        stock_tickers = SECTOR_MAP[selected_sector]["stocks"]

        with st.spinner(f"⏳ {selected_sector} স্টক লোড হচ্ছে..."):
            stk_raw = fetch_data(stock_tickers)
            stk_sub = stk_raw[stk_raw.index.date == target_date]
            stk_cut = stk_sub[stk_sub.index <= target_timestamp]

        stock_res = []
        for s in stock_tickers:
            try:
                stk_open = stk_cut["Open"][s].dropna().iloc[0]
                stk_ltp = stk_cut["Close"][s].dropna().iloc[-1]
                stk_ret = ((stk_ltp - stk_open) / stk_open) * 100
                rs_vs_nifty = stk_ret - nifty_ret
                rs_vs_sector = stk_ret - sector_ret
                stock_res.append({
                    "Stock": s.replace(".NS", ""),
                    "LTP": round(stk_ltp, 2),
                    "Change_%": round(stk_ret, 2),
                    "RS vs Nifty": round(rs_vs_nifty, 2),
                    "RS vs Sector": round(rs_vs_sector, 2),
                    "Dual_Score": round((rs_vs_nifty + rs_vs_sector), 2)
                })
            except:
                pass

        if stock_res:
            stk_df = pd.DataFrame(stock_res).sort_values(by="Dual_Score", ascending=False).reset_index(drop=True)
            top_picks = stk_df.head(2)["Stock"].tolist()
            st.success(f"🔥 **Top 2 Focus Stocks:** `{top_picks[0]}` এবং `{top_picks[1]}`")

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=stk_df["Stock"],
                y=stk_df["Dual_Score"],
                marker_color=["#27ae60" if x >= 0 else "#e74c3c" for x in stk_df["Dual_Score"]],
                text=[f"{val:+.2f}" for val in stk_df["Dual_Score"]],
                textposition="outside"
            ))
            fig.update_layout(height=270, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Dual RS Score")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                stk_df.style.map(lambda v: 'color: #27ae60; font-weight: bold;' if v > 0 else 'color: #e74c3c;', subset=['RS vs Nifty', 'RS vs Sector', 'Dual_Score']),
                use_container_width=True,
                hide_index=True
            )


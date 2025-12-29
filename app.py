import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time
import requests

st.title("چارت US30 (Dow Jones)")

# اضافه کردن user-agent برای جلوگیری از بلاک
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# انتخاب نوع
option = st.selectbox(
    "نوع شاخص رو انتخاب کن:",
    ("US30 Futures (YM=F) - معمول در تریدینگ", 
     "Dow Jones Industrial Average (^DJI) - شاخص رسمی")
)

ticker = "YM=F" if "Futures" in option else "^DJI"
name = "US30 (Dow Jones Futures)" if "Futures" in option else "Dow Jones Industrial Average"

# انتخاب بازه زمانی
period = st.selectbox(
    "بازه زمانی:",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y"),
    index=2
)

@st.cache_data(ttl=300)  # کش ۵ دقیقه‌ای برای سرعت بیشتر
def get_data(ticker_symbol, period_time):
    for attempt in range(3):
        try:
            data = yf.download(
                ticker_symbol,
                period=period_time,
                progress=False,
                session=session,  # استفاده از session با user-agent
                auto_adjust=True  # قیمت‌ها رو adjust کنه
            )
            if not data.empty:
                return data
        except Exception as e:
            time.sleep(2 ** attempt)  # exponential backoff
    # اگر YM=F شکست خورد، fallback به ^DJI
    if ticker_symbol == "YM=F":
        st.warning("دریافت داده برای Futures موقتاً مشکل داره، در حال نمایش شاخص رسمی (^DJI)...")
        return yf.download("^DJI", period=period_time, progress=False, session=session)
    return None

with st.spinner("در حال دریافت داده..."):
    data = get_data(ticker, period)

if data is None or data.empty:
    st.error("متأسفانه داده دریافت نشد. بعداً دوباره امتحان کن یا اتصال اینترنت رو چک کن.")
else:
    st.success(f"داده‌های {name} دریافت شد ({len(data)} روز)")

    # چارت کندل‌استیک
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=name
    )])

    fig.update_layout(
        title=f"چارت کندل‌استیک {name} - {period}",
        xaxis_title="تاریخ",
        yaxis_title="قیمت (دلار)",
        xaxis_rangeslider_visible=True,
        height=700,
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    if st.checkbox("نمایش جدول داده‌های خام"):
        st.dataframe(data.tail(50))

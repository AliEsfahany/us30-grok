import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.title("چارت US30 (Dow Jones)")

# انتخاب نوع
option = st.selectbox(
    "نوع شاخص رو انتخاب کن:",
    ("Dow Jones Futures (YM=F) - معمولاً به عنوان US30 شناخته می‌شه", 
     "Dow Jones Industrial Average (^DJI) - شاخص رسمی")
)

if option.startswith("Dow Jones Futures"):
    ticker = "YM=F"
    name = "US30 (Dow Jones Futures)"
else:
    ticker = "^DJI"
    name = "Dow Jones Industrial Average"

# انتخاب بازه زمانی
period = st.selectbox(
    "بازه زمانی:",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"),
    index=3  # پیش‌فرض 1 سال
)

with st.spinner("در حال دریافت داده از yfinance..."):
    data = yf.download(ticker, period=period, progress=False)

if data.empty:
    st.error("داده‌ای دریافت نشد. اتصال اینترنت رو چک کن.")
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
        template="plotly_dark"  # تم تاریک برای زیبایی بیشتر
    )

    st.plotly_chart(fig, use_container_width=True)

    # نمایش جدول (اختیاری)
    if st.checkbox("نمایش جدول داده‌های خام"):
        st.dataframe(data.tail(50))

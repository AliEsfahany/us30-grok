import streamlit as st
import finnhub
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

st.title("چارت US30 (Dow Jones) با Finnhub")

# وارد کردن API Key توسط کاربر
api_key = st.text_input("API Key Finnhub رو وارد کن:", type="password")

if not api_key:
    st.info("لطفاً اول در https://finnhub.io/register ثبت‌نام کن و API Key رایگان بگیر.")
    st.stop()

# تنظیم کلاینت Finnhub
finnhub_client = finnhub.Client(api_key=api_key)

# انتخاب نوع US30
option = st.selectbox(
    "نوع شاخص:",
    ("Dow Jones Industrial Average (INDEXDJX:.DJI)", "US30 CFD (OANDA:US30_USD)")
)

if option == "Dow Jones Industrial Average (INDEXDJX:.DJI)":
    symbol = "INDEXDJX:.DJI"
    name = "Dow Jones Industrial Average"
else:
    symbol = "OANDA:US30_USD"
    name = "US30 CFD (معمول در بروکرها)"

# انتخاب بازه زمانی
period_days = st.selectbox(
    "بازه زمانی:",
    (30, 90, 180, 365, 1825),  # تقریباً 1 ماه تا 5 سال
    format_func=lambda x: f"{x} روز (تقریباً {x//30} ماه)" if x < 1825 else "5 سال"
)

# محاسبه زمان شروع و پایان (unix timestamp)
to_ts = int(datetime.now().timestamp())
from_ts = to_ts - (period_days * 24 * 60 * 60)

with st.spinner("در حال دریافت داده از Finnhub..."):
    res = finnhub_client.stock_candles(symbol, 'D', from_ts, to_ts)

if res['s'] != 'ok':
    st.error("خطا در دریافت داده. ممکنه تیکری اشتباه باشه یا API Key نامعتبر. پیام خطا: " + str(res))
else:
    df = pd.DataFrame({
        'Date': pd.to_datetime(res['t'], unit='s'),
        'Open': res['o'],
        'High': res['h'],
        'Low': res['l'],
        'Close': res['c'],
        'Volume': res['v']
    })
    df.set_index('Date', inplace=True)

    st.success(f"داده‌های {name} دریافت شد ({len(df)} روز)")

    # چارت کندل‌استیک
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=name
    )])

    fig.update_layout(
        title=f"چارت کندل‌استیک {name} - {period_days} روز اخیر",
        xaxis_title="تاریخ",
        yaxis_title="قیمت",
        xaxis_rangeslider_visible=True,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    # جدول داده‌ها
    if st.checkbox("نمایش جدول داده‌های خام"):
        st.dataframe(df.tail(50))

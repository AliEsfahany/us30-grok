import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.title("چارت US30 / Dow Jones با Alpha Vantage")

# وارد کردن API Key توسط کاربر
api_key = st.text_input("API Key Alpha Vantage رو وارد کن:", type="password")

if not api_key:
    st.info("لطفاً در https://www.alphavantage.co/support/#api-key ثبت‌نام کن و API Key رایگان بگیر.")
    st.stop()

# انتخاب بازه زمانی
interval = st.selectbox(
    "بازه زمانی:",
    ("daily", "weekly", "monthly"),
    index=0
)

interval_map = {
    "daily": "روزانه (تا ۲۰ سال)",
    "weekly": "هفتگی",
    "monthly": "ماهانه"
}

function_map = {
    "daily": "TIME_SERIES_DAILY_ADJUSTED",
    "weekly": "TIME_SERIES_WEEKLY_ADJUSTED",
    "monthly": "TIME_SERIES_MONTHLY_ADJUSTED"
}

symbol = "DJI"  # نماد Dow Jones در Alpha Vantage
name = "Dow Jones Industrial Average (US30 Index)"

with st.spinner("در حال دریافت داده از Alpha Vantage..."):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": function_map[interval],
        "symbol": symbol,
        "outputsize": "full",  # داده کامل تاریخی
        "apikey": api_key
    }
    
    response = requests.get(url, params=params)
    data_json = response.json()

# چک خطا
if "Error Message" in data_json:
    st.error("نماد اشتباه یا داده در دسترس نیست.")
    st.stop()
elif "Note" in data_json or "Information" in data_json:
    st.error("محدودیت درخواست رسیدی (۲۵ در روز). بعداً امتحان کن یا API Key جدید بگیر.")
    st.stop()
elif "Time Series" not in data_json:
    st.error("خطا در دریافت داده: " + str(data_json))
    st.stop()

# پردازش داده
time_series_key = list(data_json.keys())[1]  # مثلاً "Time Series (Daily)"
df = pd.DataFrame.from_dict(data_json[time_series_key], orient="index")
df = df.astype(float)
df.index = pd.to_datetime(df.index)
df = df.sort_index()
df.rename(columns={
    "1. open": "Open",
    "2. high": "High",
    "3. low": "Low",
    "4. close": "Close",
    "5. adjusted close": "Close",  # برای adjusted
    "6. volume": "Volume"
}, inplace=True)

st.success(f"داده‌های {name} دریافت شد ({len(df)} نقطه) - {interval_map[interval]}")

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
    title=f"چارت کندل‌استیک {name} - {interval_map[interval]}",
    xaxis_title="تاریخ",
    yaxis_title="قیمت (دلار)",
    xaxis_rangeslider_visible=True,
    height=700,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

if st.checkbox("نمایش جدول داده‌های خام"):
    st.dataframe(df.tail(50))

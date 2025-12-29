import streamlit as st
import yfinance as yf
import mplfinance as mpf
from io import BytesIO

st.set_page_config(page_title="US30 Chart", layout="wide")
st.title("📈 US30 (Dow Jones) – Live Chart")

symbol = "^DJI"
interval = st.selectbox("تایم‌فریم:", ["1h", "4h", "1d"], index=2)
period = st.selectbox("بازه زمانی:", ["7d", "30d", "90d"], index=1)

if st.button("نمایش چارت"):
    data = yf.download(symbol, interval=interval, period=period)

    if data.empty:
        st.error("داده‌ای دریافت نشد")
    else:
        buf = BytesIO()
        mpf.plot(
            data,
            type="candle",
            style="yahoo",
            volume=True,
            savefig=buf
        )
        st.image(buf)

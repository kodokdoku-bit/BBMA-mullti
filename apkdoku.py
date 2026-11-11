import streamlit as st
import pandas as pd
import numpy as np

st.title("📈 BBMA XAU/USD Multi-Timeframe Analyzer")
st.write("Analisis teknikal multi-timeframe (M30, H1, H4) untuk XAU/USD.")

# Simulasi data atau input rentang harga
st.sidebar.header("Pengaturan Parameter")
periode_ma = st.sidebar.slider("Periode Moving Average", 5, 50, 20)

# Tombol untuk memuat analisis
if st.button("Jalankan Analisis BBMA"):
    # Simulasi data harga
    np.random.seed(42)
    waktu = pd.date_range(start='2026-11-01', periods=500, freq='30min')
    harga = 2650 + np.cumsum(np.random.randn(500) * 0.5)
    
    df = pd.DataFrame({'Close': harga}, index=waktu)
    df['MA'] = df['Close'].rolling(window=periode_ma).mean()
    df['BB_Upper'] = df['MA'] + (df['Close'].rolling(window=periode_ma).std() * 2)
    df['BB_Lower'] = df['MA'] - (df['Close'].rolling(window=periode_ma).std() * 2)
    
    st.subheader("Hasil Kalkulasi Terakhir (M30 / H1 / H4)")
    st.line_chart(df[['Close', 'MA', 'BB_Upper', 'BB_Lower']].tail(50))
    st.success("Analisis berhasil diperbarui!")

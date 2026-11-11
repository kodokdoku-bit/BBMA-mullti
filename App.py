import streamlit as st
import pandas as pd
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="BBMA XAU/USD Analyzer", page_icon="📈", layout="centered")

st.title("📈 BBMA XAU/USD Multi-Timeframe Analyzer")
st.markdown("Aplikasi analisis teknikal berbasis **Bollinger Bands & Moving Average (BBMA)** untuk timeframe **M30, H1, dan H4**.")

# Sidebar untuk Pengaturan Parameter
st.sidebar.header("⚙️ Pengaturan Indikator")
periode_ma = st.sidebar.slider("Periode Moving Average (MA)", min_value=5, max_value=50, value=20)
deviasi = st.sidebar.slider("Standar Deviasi BB", min_value=1.0, max_value=3.0, value=2.0, step=0.1)

# Tombol Eksekusi Analisis
if st.button("🚀 Jalankan Analisis Multi-Timeframe", type="primary"):
    with st.spinner("Mengambil data dan menghitung indikator BBMA..."):
        
        # Simulasi / Pengambilan Data Harga XAU/USD
        np.random.seed(42)
        waktu = pd.date_range(start='2026-11-01', periods=1500, freq='30min')
        harga_dasar = 2650 + np.cumsum(np.random.randn(1500) * 0.4)
        
        df = pd.DataFrame({
            'Open': harga_dasar,
            'High': harga_dasar + np.random.rand(1500) * 0.8,
            'Low': harga_dasar - np.random.rand(1500) * 0.8,
            'Close': harga_dasar + (np.random.rand(1500) - 0.5) * 0.6
        }, index=waktu)
        
        # Fungsi Perhitungan BBMA
        def hitung_bbma(data):
            d = data.copy()
            d['MA'] = d['Close'].rolling(window=periode_ma).mean()
            std = d['Close'].rolling(window=periode_ma).std()
            d['BB_Upper'] = d['MA'] + (std * deviasi)
            d['BB_Lower'] = d['MA'] - (std * deviasi)
            return d
            
        # Resample Multi-Timeframe (H4, H1, M30)
        df_h4 = hitung_bbma(df.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna())
        df_h1 = hitung_bbma(df.resample('1h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna())
        df_m30 = hitung_bbma(df) # Karena data dasar sudah M30
        
        # Tampilkan Hasil dalam Tabs
        tab_h4, tab_h1, tab_m30 = st.tabs(["📊 Timeframe H4 (Tren)", "📊 Timeframe H1 (Setup)", "📊 Timeframe M30 (Entry)"])
        
        with tab_h4:
            st.subheader("Analisis Tren Utama - H4")
            st.line_chart(df_h4[['Close', 'MA', 'BB_Upper', 'BB_Lower']].tail(50))
            st.dataframe(df_h4[['Close', 'MA', 'BB_Upper', 'BB_Lower']].tail(5))
            
        with tab_h1:
            st.subheader("Area Setup - H1")
            st.line_chart(df_h1[['Close', 'MA', 'BB_Upper', 'BB_Lower']].tail(50))
            st.dataframe(df_h1[['Close', 'MA', 'BB_Upper', 'BB_Lower']].tail(5))
            
        with tab_m30:
            st.subheader("Eksekusi / Entry - M30")
            st.line_chart(df_m30[['Close', 'MA', 'BB_Upper', 'BB_Lower']].tail(50))
            st.dataframe(df_m30[['Close', 'MA', 'BB_Upper', 'BB_Lower']].tail(5))
            
        st.success("Analisis selesai dijalankan!")
else:
    st.info("👈 Silakan atur parameter di sidebar lalu klik tombol **Jalankan Analisis Multi-Timeframe** untuk melihat hasil kalkulasi.")
  

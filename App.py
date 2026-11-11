import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfigurasi Halaman
st.set_page_config(page_title="BBMA XAU/USD Analyzer", page_icon="📈", layout="wide")

st.title("📈 BBMA XAU/USD Multi-Timeframe Analyzer (H4, H1, M30)")
st.markdown("Analisis Tren (H4), Setup (H1), dan Titik Eksekusi Entry (M30) dengan Grafik Interaktif.")

# Sidebar Pengaturan
st.sidebar.header("⚙️ Parameter BBMA")
periode_ma = st.sidebar.slider("Periode MA (Middle BB)", 5, 50, 20)
deviasi = st.sidebar.slider("Standar Deviasi", 1.0, 3.0, 2.0, 0.1)

if st.button("🚀 Jalankan Analisis Lengkap", type="primary"):
    with st.spinner("Menghitung indikator BBMA & mendeteksi sinyal entry..."):
        
        # Simulasi Data Harga XAU/USD (M30)
        np.random.seed(42)
        waktu = pd.date_range(start='2026-11-01', periods=1000, freq='30min')
        harga_dasar = 2650 + np.cumsum(np.random.randn(1000) * 0.5)
        
        df_m30 = pd.DataFrame({
            'Open': harga_dasar,
            'High': harga_dasar + np.random.rand(1000) * 0.8,
            'Low': harga_dasar - np.random.rand(1000) * 0.8,
            'Close': harga_dasar + (np.random.rand(1000) - 0.5) * 0.6
        }, index=waktu)
        
        # Fungsi Kalkulasi BBMA
        def hitung_bbma(data):
            d = data.copy()
            d['MA'] = d['Close'].rolling(window=periode_ma).mean()
            std = d['Close'].rolling(window=periode_ma).std()
            d['BB_Upper'] = d['MA'] + (std * deviasi)
            d['BB_Lower'] = d['MA'] - (std * deviasi)
            return d
            
        # Resample ke H1 dan H4
        df_h4 = hitung_bbma(df_m30.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna())
        df_h1 = hitung_bbma(df_m30.resample('1h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna())
        df_m30 = hitung_bbma(df_m30)
        
        # Logika Sederhana Sinyal Entry M30 (Harga menyentuh BB Lower/Upper)
        df_m30['Signal'] = 0
        df_m30.loc[df_m30['Close'] <= df_m30['BB_Lower'], 'Signal'] = 1  # Buy
        df_m30.loc[df_m30['Close'] >= df_m30['BB_Upper'], 'Signal'] = -1 # Sell

        # Tabs untuk Multi-Timeframe
        tab_h4, tab_h1, tab_m30 = st.tabs(["📊 H4 (Tren Utama)", "📊 H1 (Setup Area)", "🎯 M30 (Entry Signal BUY/SELL)"])
        
        with tab_h4:
            st.subheader("Timeframe H4 - Menilai Arah Tren")
            fig_h4 = go.Figure()
            fig_h4.add_trace(go.Candlestick(x=df_h4.index, open=df_h4['Open'], high=df_h4['High'], low=df_h4['Low'], close=df_h4['Close'], name='H4'))
            fig_h4.add_trace(go.Scatter(x=df_h4.index, y=df_h4['BB_Upper'], line=dict(color='gray', width=1), name='BB Upper'))
            fig_h4.add_trace(go.Scatter(x=df_h4.index, y=df_h4['MA'], line=dict(color='blue', width=1.5), name='Middle MA'))
            fig_h4.add_trace(go.Scatter(x=df_h4.index, y=df_h4['BB_Lower'], line=dict(color='gray', width=1), name='BB Lower', fill='tonexty'))
            fig_h4.update_layout(xaxis_rangeslider_visible=False, height=450)
            st.plotly_chart(fig_h4, use_container_width=True)

        with tab_h1:
            st.subheader("Timeframe H1 - Mencari Setup (Extreme / Momentum)")
            fig_h1 = go.Figure()
            fig_h1.add_trace(go.Candlestick(x=df_h1.index, open=df_h1['Open'], high=df_h1['High'], low=df_h1['Low'], close=df_h1['Close'], name='H1'))
            fig_h1.add_trace(go.Scatter(x=df_h1.index, y=df_h1['BB_Upper'], line=dict(color='gray', width=1), name='BB Upper'))
            fig_h1.add_trace(go.Scatter(x=df_h1.index, y=df_h1['MA'], line=dict(color='blue', width=1.5), name='Middle MA'))
            fig_h1.add_trace(go.Scatter(x=df_h1.index, y=df_h1['BB_Lower'], line=dict(color='gray', width=1), name='BB Lower'))
            fig_h1.update_layout(xaxis_rangeslider_visible=False, height=450)
            st.plotly_chart(fig_h1, use_container_width=True)

        with tab_m30:
            st.subheader("Timeframe M30 - Sinyal Eksekusi Entry")
            df_m30_plot = df_m30.tail(150)
            
            fig_m30 = go.Figure()
            fig_m30.add_trace(go.Candlestick(x=df_m30_plot.index, open=df_m30_plot['Open'], high=df_m30_plot['High'], low=df_m30_plot['Low'], close=df_m30_plot['Close'], name='M30'))
            fig_m30.add_trace(go.Scatter(x=df_m30_plot.index, y=df_m30_plot['BB_Upper'], line=dict(color='red', width=1), name='BB Upper'))
            fig_m30.add_trace(go.Scatter(x=df_m30_plot.index, y=df_m30_plot['MA'], line=dict(color='orange', width=1.5), name='Middle MA'))
            fig_m30.add_trace(go.Scatter(x=df_m30_plot.index, y=df_m30_plot['BB_Lower'], line=dict(color='green', width=1), name='BB Lower'))
            
            buy_signals = df_m30_plot[df_m30_plot['Signal'] == 1]
            sell_signals = df_m30_plot[df_m30_plot['Signal'] == -1]
            
            fig_m30.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Low'] - 1.5, mode='markers', marker=dict(symbol='triangle-up', size=12, color='green'), name='Signal BUY'))
            fig_m30.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['High'] + 1.5, mode='markers', marker=dict(symbol='triangle-down', size=12, color='red'), name='Signal SELL'))
            
            fig_m30.update_layout(xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig_m30, use_container_width=True)
            
        st.success("Analisis Multi-Timeframe & Sinyal Entry berhasil dimuat!")
else:
    st.info("👈 Klik tombol **Jalankan Analisis Lengkap** di atas untuk menampilkan grafik interaktif gaya TradingView.")
        

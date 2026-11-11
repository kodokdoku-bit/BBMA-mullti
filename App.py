import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfigurasi Halaman (Centered agar rapi di atas background foto)
st.set_page_config(page_title="BBMA Pro Terminal", page_icon="📈", layout="centered")

# --- KODE CSS UNTUK BACKGROUND FOTO LOKAL (bg_kota.jpg) ---
css_background = """
<style>
.stApp {
    background-image: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.75)), url("bg_kota..jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

/* Sidebar transparan agar menyatu dengan background */
[data-testid="stSidebar"] {
    background-color: rgba(20, 20, 20, 0.85) !important;
}

/* Warna teks utama putih kontras */
h1, h2, h3, p, .stMarkdown, label, span {
    color: white !important;
}
</style>
"""
st.markdown(css_background, unsafe_allow_html=True)

# --- JUDUL & SIDEBAR ---
st.title("📈 BBMA Multi-Asset Pro Terminal")
st.markdown("Analisis Tren (H4), Setup (H1), dan Titik Eksekusi Entry (M30) Berbagai Pasar.")

st.sidebar.header("⚙️ Pengaturan Pasar")
pilihan_aset = st.sidebar.selectbox(
    "Pilih Aset / Pair:",
    (
        "XAU/USD (Gold)", 
        "BTC/USD (Bitcoin)", 
        "ETH/USD (Ethereum)", 
        "EUR/USD (Forex)", 
        "GBP/USD (Forex)", 
        "USD/JPY (Forex)"
    )
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Parameter BBMA")
periode_ma = st.sidebar.slider("Periode MA (Middle BB)", 5, 50, 20)
deviasi = st.sidebar.slider("Standar Deviasi", 1.0, 3.0, 2.0, 0.1)

if st.button("🚀 Jalankan Analisis Aset", type="primary"):
    with st.spinner(f"Memproses data pasar untuk {pilihan_aset}..."):
        
        # Pengaturan skala volatilitas berdasarkan aset yang dipilih
        np.random.seed(42)
        waktu = pd.date_range(start='2026-11-01', periods=1000, freq='30min')
        
        if "XAU/USD" in pilihan_aset:
            harga_awal, vol = 2650.0, 0.5
        elif "BTC/USD" in pilihan_aset:
            harga_awal, vol = 92000.0, 15.0
        elif "ETH/USD" in pilihan_aset:
            harga_awal, vol = 3400.0, 5.0
        elif "EUR/USD" in pilihan_aset:
            harga_awal, vol = 1.0850, 0.0005
        elif "GBP/USD" in pilihan_aset:
            harga_awal, vol = 1.2800, 0.0006
        else:
            harga_awal, vol = 152.00, 0.08
            
        harga_dasar = harga_awal + np.cumsum(np.random.randn(1000) * vol)
        
        df_m30 = pd.DataFrame({
            'Open': harga_dasar,
            'High': harga_dasar + (np.random.rand(1000) * vol * 1.5),
            'Low': harga_dasar - (np.random.rand(1000) * vol * 1.5),
            'Close': harga_dasar + ((np.random.rand(1000) - 0.5) * vol * 1.2)
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
        
        # Logika Sinyal M30
        df_m30['Signal'] = 0
        df_m30.loc[df_m30['Close'] <= df_m30['BB_Lower'], 'Signal'] = 1  # Buy
        df_m30.loc[df_m30['Close'] >= df_m30['BB_Upper'], 'Signal'] = -1 # Sell

        st.subheader(f"📊 Analisis Aktif: {pilihan_aset}")
        
        # Tabs Multi-Timeframe
        tab_h4, tab_h1, tab_m30 = st.tabs(["📊 H4 (Tren Utama)", "📊 H1 (Setup Area)", "🎯 M30 (Entry Signal BUY/SELL)"])
        
        with tab_h4:
            st.markdown(f"**Timeframe H4 - Arah Tren {pilihan_aset}**")
            fig_h4 = go.Figure()
            fig_h4.add_trace(go.Candlestick(x=df_h4.index, open=df_h4['Open'], high=df_h4['High'], low=df_h4['Low'], close=df_h4['Close'], name='H4'))
            fig_h4.add_trace(go.Scatter(x=df_h4.index, y=df_h4['BB_Upper'], line=dict(color='gray', width=1), name='BB Upper'))
            fig_h4.add_trace(go.Scatter(x=df_h4.index, y=df_h4['MA'], line=dict(color='white', width=1.5), name='Middle MA'))
            fig_h4.add_trace(go.Scatter(x=df_h4.index, y=df_h4['BB_Lower'], line=dict(color='gray', width=1), name='BB Lower', fill='tonexty'))
            fig_h4.update_layout(xaxis_rangeslider_visible=False, height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_h4, use_container_width=True)

        with tab_h1:
            st.markdown(f"**Timeframe H1 - Area Setup (Extreme/Momentum)**")
            fig_h1 = go.Figure()
            fig_h1.add_trace(go.Candlestick(x=df_h1.index, open=df_h1['Open'], high=df_h1['High'], low=df_h1['Low'], close=df_h1['Close'], name='H1'))
            fig_h1.add_trace(go.Scatter(x=df_h1.index, y=df_h1['BB_Upper'], line=dict(color='gray', width=1), name='BB Upper'))
            fig_h1.add_trace(go.Scatter(x=df_h1.index, y=df_h1['MA'], line=dict(color='white', width=1.5), name='Middle MA'))
            fig_h1.add_trace(go.Scatter(x=df_h1.index, y=df_h1['BB_Lower'], line=dict(color='gray', width=1), name='BB Lower'))
            fig_h1.update_layout(xaxis_rangeslider_visible=False, height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_h1, use_container_width=True)

        with tab_m30:
            st.markdown(f"**Timeframe M30 - Sinyal Eksekusi BUY / SELL**")
            df_m30_plot = df_m30.tail(150)
            
            fig_m30 = go.Figure()
            fig_m30.add_trace(go.Candlestick(x=df_m30_plot.index, open=df_m30_plot['Open'], high=df_m30_plot['High'], low=df_m30_plot['Low'], close=df_m30_plot['Close'], name='M30'))
            fig_m30.add_trace(go.Scatter(x=df_m30_plot.index, y=df_m30_plot['BB_Upper'], line=dict(color='indianred', width=1), name='BB Upper'))
            fig_m30.add_trace(go.Scatter(x=df_m30_plot.index, y=df_m30_plot['MA'], line=dict(color='white', width=1.5), name='Middle MA'))
            fig_m30.add_trace(go.Scatter(x=df_m30_plot.index, y=df_m30_plot['BB_Lower'], line=dict(color='mediumseagreen', width=1), name='BB Lower'))
            
            buy_signals = df_m30_plot[df_m30_plot['Signal'] == 1]
            sell_signals = df_m30_plot[df_m30_plot['Signal'] == -1]
            
            offset = vol * 1.5
            fig_m30.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Low'] - offset, mode='markers', marker=dict(symbol='triangle-up', size=12, color='lime'), name='Signal BUY'))
            fig_m30.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['High'] + offset, mode='markers', marker=dict(symbol='triangle-down', size=12, color='red'), name='Signal SELL'))
            
            fig_m30.update_layout(xaxis_rangeslider_visible=False, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_m30, use_container_width=True)
            
        st.success(f"Analisis pasar untuk {pilihan_aset} selesai dimuat!")
else:
    st.info("👈 Silakan pilih instrumen aset di panel kiri, lalu klik tombol **Jalankan Analisis Aset**.")
        

"""
Tableau de Bord Web Interactif pour l'Analyse Technique Forex
Construit avec Streamlit et Plotly
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Ajouter le répertoire scripts au chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from data_fetcher import ForexDataFetcher, get_available_pairs

# Configuration de la page
st.set_page_config(
    page_title="Forex Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre et description
st.title("📈 Tableau de Bord d'Analyse Technique Forex")
st.markdown("Analyse technique en temps réel pour les paires de devises Forex")

# Initialiser le fetcher
fetcher = ForexDataFetcher()
available_pairs = get_available_pairs()

# Sidebar pour les paramètres
st.sidebar.header("⚙️ Paramètres")

# Sélection de la paire de devises
selected_pair_name = st.sidebar.selectbox(
    "Sélectionnez une paire de devises",
    list(available_pairs.keys()),
    index=0
)
selected_pair = available_pairs[selected_pair_name]

# Sélection de la période
period = st.sidebar.selectbox(
    "Période",
    ["1mo", "3mo", "6mo", "1y", "2y"],
    index=2
)

# Sélection de l'intervalle
interval = st.sidebar.selectbox(
    "Intervalle",
    ["1d", "1wk", "1mo"],
    index=0
)

# Sélection des indicateurs à afficher
st.sidebar.header("📊 Indicateurs")
show_sma = st.sidebar.checkbox("Moyennes Mobiles (SMA 20/50)", value=True)
show_ema = st.sidebar.checkbox("Moyennes Exponentielles (EMA 12/26)", value=False)
show_bb = st.sidebar.checkbox("Bandes de Bollinger", value=True)
show_rsi = st.sidebar.checkbox("RSI (14)", value=True)
show_macd = st.sidebar.checkbox("MACD", value=True)
show_stoch = st.sidebar.checkbox("Stochastique", value=False)

# Bouton pour rafraîchir les données
if st.sidebar.button("🔄 Rafraîchir les données", use_container_width=True):
    st.session_state.refresh = True

# Récupérer et traiter les données
@st.cache_data(ttl=3600)
def load_data(pair, period, interval):
    """Charge et traite les données Forex."""
    df = fetcher.fetch_forex_data(pair, period=period, interval=interval)
    if df is not None:
        df = fetcher.calculate_indicators(df)
    return df

# Charger les données
df = load_data(selected_pair, period, interval)

if df is None or df.empty:
    st.error("❌ Impossible de récupérer les données. Veuillez réessayer.")
else:
    # Afficher les statistiques clés
    col1, col2, col3, col4, col5 = st.columns(5)
    
    last_close = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    change = last_close - prev_close
    change_pct = (change / prev_close) * 100
    
    with col1:
        st.metric("Prix Actuel", f"{last_close:.5f}")
    
    with col2:
        st.metric("Variation", f"{change:.5f}", f"{change_pct:.2f}%")
    
    with col3:
        st.metric("Haut (52 sem.)", f"{df['High'].max():.5f}")
    
    with col4:
        st.metric("Bas (52 sem.)", f"{df['Low'].min():.5f}")
    
    with col5:
        st.metric("Signal Actuel", df['Signal'].iloc[-1], 
                 delta="BUY" if df['Signal'].iloc[-1] == "BUY" else ("SELL" if df['Signal'].iloc[-1] == "SELL" else "HOLD"))
    
    st.divider()
    
    # Créer le graphique principal avec sous-graphiques
    num_subplots = 1
    if show_rsi:
        num_subplots += 1
    if show_macd:
        num_subplots += 1
    if show_stoch:
        num_subplots += 1
    
    # Créer les subplots
    specs = [[{"secondary_y": False}] for _ in range(num_subplots)]
    fig = make_subplots(
        rows=num_subplots, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        specs=specs,
        row_heights=[0.5] + [0.15] * (num_subplots - 1)
    )
    
    # Graphique principal avec chandeliers
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="OHLC",
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )
    
    # Ajouter les Moyennes Mobiles
    if show_sma:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='blue', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='orange', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )
    
    # Ajouter les Moyennes Exponentielles
    if show_ema:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['EMA_12'],
                mode='lines',
                name='EMA 12',
                line=dict(color='purple', width=1, dash='dash'),
                opacity=0.7
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['EMA_26'],
                mode='lines',
                name='EMA 26',
                line=dict(color='brown', width=1, dash='dash'),
                opacity=0.7
            ),
            row=1, col=1
        )
    
    # Ajouter les Bandes de Bollinger
    if show_bb:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_High'],
                mode='lines',
                name='BB High',
                line=dict(color='gray', width=0.5),
                opacity=0.3,
                showlegend=False
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_Low'],
                mode='lines',
                name='BB Low',
                line=dict(color='gray', width=0.5),
                opacity=0.3,
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
    
    # Ajouter le RSI
    current_row = 2
    if show_rsi:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['RSI'],
                mode='lines',
                name='RSI (14)',
                line=dict(color='purple', width=2)
            ),
            row=current_row, col=1
        )
        
        # Ajouter les niveaux de suracheté/survente
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
        
        current_row += 1
    
    # Ajouter le MACD
    if show_macd:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=current_row, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['MACD_Signal'],
                mode='lines',
                name='Signal',
                line=dict(color='red', width=2)
            ),
            row=current_row, col=1
        )
        
        current_row += 1
    
    # Ajouter le Stochastique
    if show_stoch:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Stoch_K'],
                mode='lines',
                name='Stoch K',
                line=dict(color='blue', width=1)
            ),
            row=current_row, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Stoch_D'],
                mode='lines',
                name='Stoch D',
                line=dict(color='red', width=1)
            ),
            row=current_row, col=1
        )
        
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=current_row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=current_row, col=1)
    
    # Mise à jour du layout
    fig.update_layout(
        title=f"Analyse Technique - {selected_pair_name}",
        xaxis_title="Date",
        yaxis_title="Prix",
        template="plotly_dark",
        height=800,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)
    
    # Afficher les données brutes
    st.divider()
    st.subheader("📋 Données Brutes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Affichage des dernières 10 barres :")
        display_cols = ['Open', 'High', 'Low', 'Close', 'RSI', 'MACD', 'Signal']
        st.dataframe(df[display_cols].tail(10), use_container_width=True)
    
    with col2:
        st.write("Statistiques descriptives :")
        st.dataframe(df[['Open', 'High', 'Low', 'Close']].describe(), use_container_width=True)

# Footer
st.divider()
st.markdown("""
---
**Tableau de Bord d'Analyse Technique Forex** | Données fournies par Yahoo Finance | Mise à jour : 2025
""")

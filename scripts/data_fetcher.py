"""
Module d'acquisition de données Forex et calcul des indicateurs techniques.
Utilise yfinance pour récupérer les données historiques des paires de devises.
"""

import pandas as pd
import yfinance as yf
import ta
from datetime import datetime, timedelta
import os

class ForexDataFetcher:
    """Classe pour récupérer et traiter les données Forex."""
    
    def __init__(self, data_dir="data"):
        """
        Initialise le fetcher de données.
        
        Args:
            data_dir (str): Répertoire pour stocker les données.
        """
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def fetch_forex_data(self, pair="EURUSD=X", period="1y", interval="1d"):
        """
        Récupère les données historiques d'une paire Forex.
        
        Args:
            pair (str): Paire de devises (ex: EURUSD=X, GBPUSD=X).
            period (str): Période (ex: 1y, 6mo, 3mo, 1mo).
            interval (str): Intervalle (ex: 1d, 1h, 15m).
        
        Returns:
            pd.DataFrame: DataFrame contenant les données OHLCV.
        """
        try:
            print(f"Récupération des données pour {pair}...")
            data = yf.download(pair, period=period, interval=interval, progress=False)
            
            if data.empty:
                print(f"Aucune donnée trouvée pour {pair}")
                return None
            
            # Renommer les colonnes pour cohérence
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Supprimer les lignes avec des NaN
            data = data.dropna()
            
            print(f"✓ {len(data)} barres récupérées pour {pair}")
            return data
        
        except Exception as e:
            print(f"✗ Erreur lors de la récupération des données: {e}")
            return None
    
    def calculate_indicators(self, df):
        """
        Calcule les indicateurs techniques pour un DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame contenant les données OHLCV.
        
        Returns:
            pd.DataFrame: DataFrame augmenté avec les indicateurs.
        """
        if df is None or df.empty:
            return df
        
        try:
            # Moyennes Mobiles
            df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
            df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
            df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
            df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
            
            # Bandes de Bollinger
            bollinger = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
            df['BB_High'] = bollinger.bollinger_hband()
            df['BB_Mid'] = bollinger.bollinger_mavg()
            df['BB_Low'] = bollinger.bollinger_lband()
            
            # RSI (Relative Strength Index)
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
            
            # MACD (Moving Average Convergence Divergence)
            macd = ta.trend.MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_Signal'] = macd.macd_signal()
            df['MACD_Diff'] = macd.macd_diff()
            
            # Stochastique
            stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], window=14)
            df['Stoch_K'] = stoch.stoch()
            df['Stoch_D'] = stoch.stoch_signal()
            
            # ATR (Average True Range)
            df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
            
            # Signaux simples
            df['Signal'] = 'HOLD'
            df.loc[df['RSI'] < 30, 'Signal'] = 'BUY'
            df.loc[df['RSI'] > 70, 'Signal'] = 'SELL'
            
            print("✓ Indicateurs calculés avec succès")
            return df
        
        except Exception as e:
            print(f"✗ Erreur lors du calcul des indicateurs: {e}")
            return df
    
    def save_data(self, df, filename):
        """
        Sauvegarde les données dans un fichier CSV.
        
        Args:
            df (pd.DataFrame): DataFrame à sauvegarder.
            filename (str): Nom du fichier.
        """
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath)
        print(f"✓ Données sauvegardées dans {filepath}")
    
    def load_data(self, filename):
        """
        Charge les données depuis un fichier CSV.
        
        Args:
            filename (str): Nom du fichier.
        
        Returns:
            pd.DataFrame: DataFrame chargé.
        """
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        return None


def get_available_pairs():
    """Retourne les paires Forex disponibles."""
    return {
        'EUR/USD': 'EURUSD=X',
        'GBP/USD': 'GBPUSD=X',
        'USD/JPY': 'USDJPY=X',
        'USD/CHF': 'USDCHF=X',
        'AUD/USD': 'AUDUSD=X',
        'USD/CAD': 'USDCAD=X',
        'NZD/USD': 'NZDUSD=X',
        'EUR/GBP': 'EURGBP=X',
        'EUR/JPY': 'EURJPY=X',
        'GBP/JPY': 'GBPJPY=X',
    }


if __name__ == "__main__":
    # Test du module
    fetcher = ForexDataFetcher()
    
    # Récupérer les données pour EUR/USD
    df = fetcher.fetch_forex_data("EURUSD=X", period="1y", interval="1d")
    
    if df is not None:
        # Calculer les indicateurs
        df = fetcher.calculate_indicators(df)
        
        # Sauvegarder les données
        fetcher.save_data(df, "EURUSD_data.csv")
        
        # Afficher les dernières lignes
        print("\nDernières données:")
        print(df.tail())
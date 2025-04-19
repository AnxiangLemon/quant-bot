# 📁 modules/data/indicator_fetcher.py

import pandas as pd
from ta.trend import MACD
from ta.momentum import StochasticOscillator
from ta.volatility import AverageTrueRange

from binance.exchange import exchange

def fetch_ohlcv(symbol: str = "BTC/USDT", timeframe: str = "1m", limit: int = 200) -> pd.DataFrame:
    """
    从 Binance 获取历史 K 线数据。
    """
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

def get_strategy_indicators(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
    limit: int = 200,
    macd_params: tuple = (12, 26, 9),
    kdj_params: tuple = (9, 3),
    atr_window: int = 14
) -> dict:
    """
    获取策略所需技术指标：MACD + KDJ + ATR，支持参数配置。
    """
    df = fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)

    # MACD
    macd = MACD(
        close=df["close"],
        window_slow=macd_params[1],
        window_fast=macd_params[0],
        window_sign=macd_params[2]
    )
    df["DIF"] = macd.macd()
    df["DEA"] = macd.macd_signal()

    # KDJ
    kdj = StochasticOscillator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=kdj_params[0],
        smooth_window=kdj_params[1]
    )
    df["K"] = kdj.stoch()
    df["D"] = kdj.stoch_signal()
    df["J"] = 3 * df["K"] - 2 * df["D"]

    # ATR
    atr = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=atr_window
    )
    df["ATR"] = atr.average_true_range()

    indicators = {
        "DIF": df["DIF"].dropna().tolist(),
        "DEA": df["DEA"].dropna().tolist(),
        "K": df["K"].dropna().tolist(),
        "D": df["D"].dropna().tolist(),
        "J": df["J"].dropna().tolist(),
        "ATR": df["ATR"].dropna().tolist(),
    }

    # 可选调试打印
    if True:
        print(f"\n[DEBUG] {symbol} - {timeframe}")
        print(f"🔍 DIF[-1]: {indicators['DIF'][-1]:.6f}, DEA[-1]: {indicators['DEA'][-1]:.6f}")
        print(f"🔍 KDJ[-1]: K={indicators['K'][-1]:.2f}, D={indicators['D'][-1]:.2f}, J={indicators['J'][-1]:.2f}")
        print(f"📏 ATR[-1]: {indicators['ATR'][-1]:.6f}")
        print(f"🕒 最新时间戳: {df['timestamp'].iloc[-1]}")

    return indicators

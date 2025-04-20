# 📁 modules/data/indicator_fetcher.py

import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.momentum import StochasticOscillator
from ta.volatility import AverageTrueRange
from binance.exchange import exchange
from config.logger import log

def fetch_ohlcv(symbol: str = "BTC/USDT", timeframe: str = "1m", limit: int = 200) -> pd.DataFrame:
    """
    从 Binance 获取历史 K 线数据。
    """
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

def _calculate_kdj(df: pd.DataFrame, n: int = 9, k_smooth: int = 3, d_smooth: int = 3) -> pd.DataFrame:
    """
    KDJ计算核心逻辑（私有函数）
    参数:
        n: RSV周期
        k_smooth: K值平滑周期
        d_smooth: D值平滑周期
    """
    # 计算n日内的最低价和最高价
    low_min = df['low'].rolling(window=n).min()
    high_max = df['high'].rolling(window=n).max()
    
    # 计算RSV（未成熟随机值）
    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
    rsv = rsv.replace([np.inf, -np.inf], np.nan).ffill()  # 处理异常值
    
    # 初始化K和D数组
    K, D = np.zeros(len(df)), np.zeros(len(df))
    K[:n-1] = np.nan  # 前n-1个数据点无效
    
    # 递归计算K值和D值
    for i in range(n-1, len(df)):
        if i == n-1:
            K[i] = rsv.iloc[i]
            D[i] = K[i]
        else:
            # 根据平滑周期动态计算权重
            k_alpha = 1 / k_smooth
            d_alpha = 1 / d_smooth
            K[i] = (1 - k_alpha) * K[i-1] + k_alpha * rsv.iloc[i]
            D[i] = (1 - d_alpha) * D[i-1] + d_alpha * K[i]
    
    df['K'] = K
    df['D'] = D
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df

def get_strategy_indicators(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
    limit: int = 200,
    macd_params: tuple = (12, 26, 9),
    kdj_params: tuple = (9, 3, 3),
    atr_window: int = 14
) -> dict:
    """
    获取多指标组合（MACD + KDJ + ATR）
    参数示例:
        macd_params: (fast, slow, signal)
        kdj_params: (n_period, k_smooth, d_smooth)
    """
    df = fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
    
    # ===== MACD =====
    macd = MACD(
        close=df["close"],
        window_fast=macd_params[0],
        window_slow=macd_params[1],
        window_sign=macd_params[2]
    )
    df["DIF"] = macd.macd()
    df["DEA"] = macd.macd_signal()
    
    # ===== KDJ =====
    df = _calculate_kdj(
        df,
        n=kdj_params[0],
        k_smooth=kdj_params[1],
        d_smooth=kdj_params[2]
    )
    
    # ===== ATR =====
    atr = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=atr_window
    )
    df["ATR"] = atr.average_true_range()
    
    # 结果处理
    indicators = {
        "DIF": df["DIF"].dropna().tolist(),
        "DEA": df["DEA"].dropna().tolist(),
        "K": df["K"].dropna().tolist(),
        "D": df["D"].dropna().tolist(),
        "J": df["J"].dropna().tolist(),
        "ATR": df["ATR"].dropna().tolist(),
    }
    
    # 调试日志
    log(f"\n[指标状态] {symbol}@{timeframe}")
    log(f"MACD | DIF: {indicators['DIF'][-1]:.4f}, DEA: {indicators['DEA'][-1]:.4f}")
    log(f"KDJ  | K: {indicators['K'][-1]:.2f}, D: {indicators['D'][-1]:.2f}, J: {indicators['J'][-1]:.2f}")
    log(f"ATR  | {indicators['ATR'][-1]:.4f}")
    
    return indicators
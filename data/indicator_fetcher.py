# 📁 modules/data/indicator_fetcher.py

import pandas as pd
from ta.trend import MACD
from ta.momentum import StochasticOscillator
from binance.exchange import exchange


def fetch_ohlcv(symbol: str = "BTC/USDT", timeframe: str = "1m", limit: int = 200) -> pd.DataFrame:
    """
    从 Binance 获取历史 K 线数据。

    :param symbol: 交易对（如 BTC/USDT）
    :param timeframe: 时间周期，如 1m、5m、1h、1d
    :param limit: 获取的数据点数量（最大 1000）
    :return: 包含 open, high, low, close, volume 的 DataFrame
    """
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

def get_macd_kdj_indicators(df: pd.DataFrame) -> dict:
    """
    基于收盘、最高、最低价计算 MACD + KDJ 指标。

    :param df: 包含 close、high、low 的 DataFrame
    :return: dict，包含策略需要的指标列表
    """
    macd = MACD(close=df["close"])
    kdj = StochasticOscillator(close=df["close"], high=df["high"], low=df["low"])

    DIF = macd.macd().tolist()
    DEA = macd.macd_signal().tolist()
    K = kdj.stoch().tolist()
    D = kdj.stoch_signal().tolist()
    J = [(3 * k) - (2 * d) for k, d in zip(K, D)]

    return {
        "DIF": DIF,
        "DEA": DEA,
        "K": K,
        "D": D,
        "J": J
    }

def get_strategy_indicators(symbol: str = "BTC/USDT", timeframe: str = "1m", limit: int = 200) -> dict:
    """
    一步到位：从币安拉取K线并返回策略所需的指标数据。

    :param symbol: 币种对（如 BTC/USDT）
    :param timeframe: 周期（如 1h）
    :param limit: 数据条数
    :return: dict，包含 DIF, DEA, K, D, J 等
    """
    df = fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
    indicators =  get_macd_kdj_indicators(df)

    if True:
        print(f"\n[DEBUG] {symbol} - {timeframe}")
        print(f"🔍 DIF[-1]: {indicators['DIF'][-1]:.6f}, DEA[-1]: {indicators['DEA'][-1]:.6f}")
        print(f"🔍 K[-1]: {indicators['K'][-1]:.2f}, D[-1]: {indicators['D'][-1]:.2f}, J[-1]: {indicators['J'][-1]:.2f}")
        print(f"🕒 最新时间戳: {df['timestamp'].iloc[-1]}")
    return indicators
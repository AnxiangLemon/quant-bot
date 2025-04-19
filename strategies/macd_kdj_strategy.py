# 📁 strategies/macd_kdj_strategy.py

from strategies.base_strategy import BaseStrategy
from config.config import SYMBOL_CONFIGS

class MACDKDJStrategy(BaseStrategy):
    """
    MACD + KDJ 技术面策略，支持配置化：
    - 买入：MACD 金叉或 KDJ 金叉 且 J < max_j_buy
    - 卖出：MACD 死叉 或 J > min_j_sell
    - 止损：价格 < entry_price - ATR * atr_stop_multiplier
    """

    def should_buy(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        if position.get("holding", False):
            return False

        indicators = kwargs.get("indicators", {})
        config = SYMBOL_CONFIGS[symbol]
        max_j = config.get("max_j_buy", 70)

        if not self._check_indicators(indicators):
            return False

        # 获取前一周期和当前周期的 MACD DIF/DEA 值
        dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]  # 上一个周期
        dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]      # 当前周期

        # 获取前一周期和当前周期的 KDJ K/D 值
        k_y, d_y = indicators["K"][-2], indicators["D"][-2]
        k, d = indicators["K"][-1], indicators["D"][-1]

        # 当前周期的 J 值
        j = indicators["J"][-1]

        # 判断条件：MACD 金叉 或 KDJ 金叉 且 J 值未过热
        return (
            ((dif_y < dea_y and dif > dea) or (k_y < d_y and k > d)) and j < max_j
        )

    def should_sell(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        if not position.get("holding", False):
            return False

        indicators = kwargs.get("indicators", {})
        config = SYMBOL_CONFIGS[symbol]
        min_j = config.get("min_j_sell", 90)

        if not self._check_indicators(indicators):
            return False

        # 获取 MACD 当前与前一周期 DIF 和 DEA 值
        dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]
        dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]

        # 当前周期 J 值
        j = indicators["J"][-1]

        # 判断条件：MACD 死叉 或 J 值过热
        return (
            (dif_y > dea_y and dif < dea) or j > min_j
        )

    def should_stop_loss(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        # 获取持仓时的买入价
        entry_price = position.get("entry_price")
        if not position.get("holding", False) or not entry_price:
            return False

        indicators = kwargs.get("indicators", {})
        atr_values = indicators.get("ATR", [])

        # 如果没有 ATR 数据，不进行止损判断
        if not atr_values or len(atr_values) < 1:
            return False

        # 获取配置中的 ATR 止损倍数（默认 2.0）
        config = SYMBOL_CONFIGS[symbol]
        multiplier = config.get("atr_stop_multiplier", 2.0)

        # 获取最新 ATR 值
        latest_atr = atr_values[-1]

        # 动态止损价格 = 买入价 - ATR × 倍数
        stop_price = entry_price - multiplier * latest_atr

        # 如果当前价格跌破止损价格，触发止损
        return price < stop_price

    @staticmethod
    def _check_indicators(indicators: dict) -> bool:
        """
        检查指标是否完整，且每个关键指标序列长度不少于 2（用于计算金叉/死叉）
        """
        required_keys = ["DIF", "DEA", "K", "D", "J", "ATR"]
        return all(key in indicators and len(indicators[key]) >= 2 for key in required_keys)

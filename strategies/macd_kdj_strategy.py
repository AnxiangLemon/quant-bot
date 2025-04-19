# 📁 strategies/macd_kdj_strategy.py

from strategies.base_strategy import BaseStrategy
from config.config import SYMBOL_CONFIGS
from config.logger import log


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
        """
        综合止损判断函数，支持多种止损逻辑，并可配置优先级顺序。
        """

        entry_price = position.get("entry_price")
        if not position.get("holding", False) or not entry_price:
            return False

        config = SYMBOL_CONFIGS[symbol]
        indicators = kwargs.get("indicators", {})
        atr_values = indicators.get("ATR", [])

        # 止损优先级顺序（可配置）
        priorities = config.get("stop_loss_priority", ["trailing", "fixed", "atr", "macd", "drawdown"])

        for method in priorities:
            if method == "fixed":
                fix_stop_pct = config.get("fixed_stop_loss_pct", 0.02)
                if price < entry_price * (1 - fix_stop_pct):
                    log("🔻 触发固定百分比止损")
                    kwargs["stop_reason"] = "fixed"
                    return True

            elif method == "atr":
                atr_multiplier = config.get("atr_stop_multiplier", 2.0)
                if atr_values and len(atr_values) >= 1:
                    latest_atr = atr_values[-1]
                    stop_price = entry_price - atr_multiplier * latest_atr
                    if price < stop_price:
                        log("🔻 触发 ATR 动态止损")
                        kwargs["stop_reason"] = "atr"
                        return True

            elif method == "macd":
                if self._check_indicators(indicators):
                    dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]
                    dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]
                    if dif_y > dea_y and dif < dea and price < entry_price:
                        log("🔻 触发 MACD 死叉趋势止损")
                        kwargs["stop_reason"] = "macd"
                        return True

            elif method == "drawdown":
                max_price = position.get("max_price", entry_price)
                drawdown_pct = (max_price - price) / max_price
                max_drawdown_pct = config.get("max_drawdown_pct", 0.05)
                if drawdown_pct >= max_drawdown_pct:
                    log(f"🔻 触发最大回撤止损：回撤 {drawdown_pct:.2%}")
                    kwargs["stop_reason"] = "drawdown"
                    return True

            elif method == "trailing":
                trailing_stop_price = position.get("trailing_stop_price")
                if trailing_stop_price and price < trailing_stop_price:
                    log(f"🔻 触发移动止损：当前价格 {price:.2f} < 止损线 {trailing_stop_price:.2f}")
                    kwargs["stop_reason"] = "trailing"
                    return True

        return False


    @staticmethod
    def _check_indicators(indicators: dict) -> bool:
        """
        检查指标是否完整，且每个关键指标序列长度不少于 2（用于计算金叉/死叉）
        """
        required_keys = ["DIF", "DEA", "K", "D", "J", "ATR"]
        return all(key in indicators and len(indicators[key]) >= 2 for key in required_keys)

# 引入基础策略类
from strategies.base_strategy import BaseStrategy
from config.config import SYMBOL_CONFIGS


class MACDKDJStrategy(BaseStrategy):
    """
    MACD + KDJ 技术面策略：
    
    - 买入：
        1. MACD 金叉（DIF 上穿 DEA）
        2. KDJ 金叉（K 上穿 D）
        3. J 值未过热（J < 50）

    - 卖出：
        1. MACD 死叉（DIF 下穿 DEA）
        或
        2. J 值过热（J > 90）

    - 止损（可选）：
        当前价格低于买入价 * stop_loss_ratio（默认 0.99）
    """

    def should_buy(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        if position.get("holding", False):
            return False

        indicators = kwargs.get("indicators", {})
        if not self._check_indicators(indicators):
            return False

        dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]
        dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]
        k_y, d_y = indicators["K"][-2], indicators["D"][-2]
        k, d = indicators["K"][-1], indicators["D"][-1]
        j = indicators["J"][-1]

        return (
            dif_y < dea_y and dif > dea and
            k_y < d_y and k > d and
            j < 50
        )

    def should_sell(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        if not position.get("holding", False):
            return False

        indicators = kwargs.get("indicators", {})
        if not self._check_indicators(indicators):
            return False

        dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]
        dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]
        j = indicators["J"][-1]

        return (
            (dif_y > dea_y and dif < dea) or
            j > 90
        )

    def should_stop_loss(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        config = SYMBOL_CONFIGS[symbol]
        entry_price = position.get("entry_price")
        if not position.get("holding", False) or not entry_price:
            return False
        return price < entry_price * config.get("stop_loss_ratio", 0.99)

    @staticmethod
    def _check_indicators(indicators: dict) -> bool:
        """
        简单的指标合法性校验，避免因数据缺失导致异常。
        """
        required_keys = ["DIF", "DEA", "K", "D", "J"]
        return all(key in indicators and len(indicators[key]) >= 2 for key in required_keys)

# 引入基础策略类 BaseStrategy，用于继承实现具体策略逻辑
from strategies.base_strategy import BaseStrategy

# 引入符号（币种/股票等）对应的策略配置参数，如买入价、止盈比例、止损比例
from config.config import SYMBOL_CONFIGS


class SimpleThresholdStrategy(BaseStrategy):
    """
    简单阈值交易策略类，继承自 BaseStrategy。

    策略逻辑：
    - 买入条件：当前价格低于配置中的买入价格（buy_price）。
    - 卖出条件：当前盈利比例高于设定的止盈比例（take_profit_pct，默认 3%）。
    - 止损条件：当前价格低于买入价乘以止损比率（stop_loss_ratio，默认 0.99，即亏损超过 1%）。
    """

    def should_buy(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        判断是否应该买入。

        参数：
        - symbol: 当前的交易标的（如 BTC/USDT）。
        - price: 当前的市场价格。
        - position: 当前持仓状态，包含 holding（是否持仓）、entry_price（买入价）等字段。

        返回：
        - True 表示满足买入条件；False 表示不满足。
        """
        config = SYMBOL_CONFIGS[symbol]  # 获取该标的的策略参数配置
        # 如果当前没有持仓，且价格低于预设买入价，则返回 True
        return not position.get("holding", False) and price < config["buy_price"]

    def should_sell(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        判断是否应该卖出（止盈）。

        参数：
        - symbol: 当前的交易标的。
        - price: 当前的市场价格。
        - position: 当前持仓状态。

        返回：
        - True 表示满足卖出条件；False 表示不满足。
        """
        config = SYMBOL_CONFIGS[symbol]  # 获取配置
        entry_price = position.get("entry_price")  # 获取买入价

        # 如果未持仓或没有记录买入价，无法判断，直接返回 False
        if not position.get("holding", False) or not entry_price:
            return False

        # 计算当前盈利比例
        profit_pct = (price - entry_price) / entry_price
        # 若盈利比例超过设定阈值（默认 3%），则返回 True
        return profit_pct > config.get("take_profit_pct", 0.03)

    def should_stop_loss(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        判断是否应该止损。

        参数：
        - symbol: 当前的交易标的。
        - price: 当前的市场价格。
        - position: 当前持仓状态。

        返回：
        - True 表示满足止损条件；False 表示不满足。
        """
        config = SYMBOL_CONFIGS[symbol]  # 获取配置
        entry_price = position.get("entry_price")  # 获取买入价

        # 如果未持仓或没有买入价，无法止损判断，直接返回 False
        if not position.get("holding", False) or not entry_price:
            return False

        # 若当前价格低于买入价乘以止损比率（默认 0.99），表示触发止损
        return price < entry_price * config.get("stop_loss_ratio", 0.99)

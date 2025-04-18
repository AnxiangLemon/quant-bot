from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    策略基类，所有策略需继承此类，并实现 should_buy、should_sell 和 should_stop_loss 方法。

    所有方法都支持 **kwargs，用于接收扩展参数，例如技术指标、市场情绪等。
    """

    @abstractmethod
    def should_buy(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        判断是否应该买入。
        :param symbol: 交易标的（如 BTC/USDT）
        :param price: 当前价格
        :param position: 当前持仓状态
        :param kwargs: 可选的扩展参数（如技术指标）
        :return: 是否买入
        """
        pass

    @abstractmethod
    def should_sell(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        判断是否应该卖出。
        :param symbol: 交易标的
        :param price: 当前价格
        :param position: 当前持仓状态
        :param kwargs: 可选扩展参数
        :return: 是否卖出
        """
        pass

    @abstractmethod
    def should_stop_loss(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        判断是否应该止损。
        :param symbol: 交易标的
        :param price: 当前价格
        :param position: 当前持仓状态
        :param kwargs: 可选扩展参数
        :return: 是否止损
        """
        pass

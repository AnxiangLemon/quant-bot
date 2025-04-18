from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    策略基类，所有策略都需要继承此类并实现 should_buy、should_sell 和 should_stop_loss 方法
    """

    @abstractmethod
    def should_buy(self, symbol: str, price: float, position: dict) -> bool:
        pass

    @abstractmethod
    def should_sell(self, symbol: str, price: float, position: dict) -> bool:
        pass

    @abstractmethod
    def should_stop_loss(self, symbol: str, price: float, position: dict) -> bool:
        pass

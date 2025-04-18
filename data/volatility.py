from config.config import SYMBOL_CONFIGS
from config.logger import log

def adjust_strategy_based_on_volatility(symbol, price):
    from config.config import SYMBOL_CONFIGS
    from config.logger import log

    volatility = get_market_volatility(symbol)

    volatility_threshold = 0.02
    price_adjustment_factor = 0.01

    if volatility > volatility_threshold:
        # 动态调整（保留小数）
        buy_price = price * (1 - price_adjustment_factor)
        sell_price = price * (1 + price_adjustment_factor)

        # 根据币种设定精度
        if symbol.startswith("BTC"):
            decimals = 2
        elif symbol.startswith("ETH"):
            decimals = 2
        elif symbol.startswith("DOGE"):
            decimals = 6
        else:
            decimals = 4  # 默认值

        # 四舍五入处理
        buy_price = round(buy_price, decimals)
        sell_price = round(sell_price, decimals)

        SYMBOL_CONFIGS[symbol]["buy_price"] = buy_price
        SYMBOL_CONFIGS[symbol]["sell_price"] = sell_price

        log(f"调整 {symbol} 策略：买入价={buy_price}, 卖出价={sell_price}, 波动率={volatility:.2f}")
    else:
        log(f"{symbol} 当前波动较小，维持原策略：买入价={SYMBOL_CONFIGS[symbol]['buy_price']}, 卖出价={SYMBOL_CONFIGS[symbol]['sell_price']}")



def get_market_volatility(symbol):
    """
    假设获取市场波动率的函数，可以根据历史价格计算波动率
    目前返回一个虚拟的波动率值
    """
    return 0.03  # 假设市场波动率为 3%（你可以用更复杂的计算方法）


# def get_market_volatility(symbol):
#     """
#     获取市场的波动率，计算过去一段时间内的标准差作为波动性指标
#     这里可以使用历史价格数据来计算
#     """
#     historical_prices = get_historical_prices(symbol, timeframe='1h', limit=50)  # 假设能获取过去50个小时的价格

#     # 计算价格的标准差，作为波动率指标
#     volatility = np.std(historical_prices)  # 使用 numpy 的 std 函数来计算标准差

#     return volatility

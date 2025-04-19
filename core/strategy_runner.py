# 📁 core/strategy_runner.py

import time
from config.config import SYMBOL_CONFIGS, INTERVAL
from config.logger import log
from config.position import load_position
from binance.services import get_ticker_price
from data.volatility import adjust_strategy_based_on_volatility
from core.signal_handler import handle_buy, handle_sell, handle_stop_loss

from strategies.simple_threshold_strategy import SimpleThresholdStrategy
from strategies.macd_kdj_strategy import MACDKDJStrategy
from data.indicator_fetcher import get_strategy_indicators



def run_loop():
    #strategy = SimpleThresholdStrategy()
    strategy = MACDKDJStrategy()
    position = load_position()

    log("🚀 模拟量化交易机器人启动！")

    while True:
        try:
            print("\n")
            for symbol, config in SYMBOL_CONFIGS.items():
                price = get_ticker_price(symbol)
                log(f"📈 当前 {symbol} 价格：{price:.6f} USDT")

                holding_info = position.get(symbol, {"holding": False, "entry_price": None})
                # 市场波动来推断
               # adjust_strategy_based_on_volatility(symbol, price)

                # 根据MACD KDJ 来推断
               #  indicators = get_strategy_indicators(symbol)
                indicators = get_strategy_indicators(
                symbol=symbol,
                timeframe="1m",
                limit=200,
                macd_params=config.get("macd_params", (12, 26, 9)),
                kdj_params=config.get("kdj_params", (9, 3)),
                atr_window=config.get("atr_window", 14)
)
                if strategy.should_buy(symbol, price, holding_info, indicators=indicators):
                    handle_buy(symbol, price, position)

                elif strategy.should_sell(symbol, price, holding_info, indicators=indicators):
                    handle_sell(symbol, price, holding_info, position)

                elif strategy.should_stop_loss(symbol, price, holding_info, indicators=indicators):
                    handle_stop_loss(symbol, price, holding_info, position)

                else:
                    log(f"⌛ {symbol} 无操作（未触发策略买卖条件）")

            time.sleep(INTERVAL)

        except Exception as e:
            log(f"❌ 出现错误：{e}")
            time.sleep(5)


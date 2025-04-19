# 📁 core/strategy_runner.py

import time
from config.config import SYMBOL_CONFIGS, INTERVAL
from config.logger import log
from config.position import load_position, save_position, update_trailing_stop
from binance.services import get_ticker_price
from data.volatility import adjust_strategy_based_on_volatility
from core.signal_handler import handle_buy, handle_sell, handle_stop_loss

from strategies.simple_threshold_strategy import SimpleThresholdStrategy
from strategies.macd_kdj_strategy import MACDKDJStrategy
from data.indicator_fetcher import get_strategy_indicators


def ensure_position(symbol, position):
    """
    确保每个币种的持仓结构存在，避免后续操作报错。
    """
    if symbol not in position:
        position[symbol] = {
            "holding": False,
            "entry_price": None,
            "trailing_stop_price": None,
            "max_price": None
        }

def run_loop():
    """
    主运行循环函数，负责：
    - 获取价格和技术指标
    - 执行买入 / 卖出 / 止损操作
    - 更新仓位信息并保存
    - 每 INTERVAL 秒执行一次
    """
    strategy = MACDKDJStrategy()
    position = load_position()

    log("🚀 模拟量化交易机器人启动！")

    while True:
        try:
            for symbol, config in SYMBOL_CONFIGS.items():
                # ✅ 初始化该币种仓位结构
                ensure_position(symbol, position)

                # 获取实时价格
                price = get_ticker_price(symbol)
                log(f"📈 当前 {symbol} 价格：{price:.6f} USDT")

                holding_info = position[symbol]

                # ✅ 更新移动止损线和最大价格
                if update_trailing_stop(position[symbol], price, config["trailing_stop_pct"]):
                    # 保存最新仓位状态
                     save_position(position)
                
                # 获取技术指标（MACD / KDJ / ATR）
                indicators = get_strategy_indicators(
                    symbol=symbol,
                    timeframe="1m",
                    limit=200,
                    macd_params=config.get("macd_params", (12, 26, 9)),
                    kdj_params=config.get("kdj_params", (9, 3)),
                    atr_window=config.get("atr_window", 14)
                )

                # 策略判断
                if strategy.should_buy(symbol, price, holding_info, indicators=indicators):
                    handle_buy(symbol, price, position)

                elif strategy.should_sell(symbol, price, holding_info, indicators=indicators):
                    handle_sell(symbol, price, holding_info, position)

                elif strategy.should_stop_loss(symbol, price, holding_info, indicators=indicators):
                    # ✅ 添加止损原因到持仓（便于日志/记录）
                    stop_reason = indicators.get("stop_reason", "unknown")
                    position[symbol]["stop_reason"] = stop_reason
                    handle_stop_loss(symbol, price, holding_info, position)

                else:
                    log(f"⌛ {symbol} 无操作（未触发策略买卖条件）")

            time.sleep(INTERVAL)

        except Exception as e:
            log(f"❌ 出现错误：{e}")
            time.sleep(5)
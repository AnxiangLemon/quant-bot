# 📁 grid_bot.py

import time
from modules.config import SYMBOL_CONFIGS, INTERVAL
from modules.logger import log
from modules.position import load_position, save_position
from modules.telegram_notify import send_telegram_message
from modules.binance_client import get_ticker_price
from modules.utils import adjust_strategy_based_on_volatility  # 引入动态策略调整功能
from modules.strategies.simple_threshold import SimpleThresholdStrategy

# 初始化状态和策略
strategy = SimpleThresholdStrategy()
position = load_position()

log("🚀 模拟量化交易机器人启动！")

while True:
    try:
        round_logs = []  # 用于收集本轮全部日志
        print('\n')

        for symbol, config in SYMBOL_CONFIGS.items():
            price = get_ticker_price(symbol)
            log(f"📈 当前 {symbol} 价格：{price:.6f} USDT")

            holding_info = position.get(symbol, {"holding": False, "entry_price": None})

            # 策略动态调整（根据市场波动）
            adjust_strategy_based_on_volatility(symbol, price)

            if strategy.should_buy(symbol, price, holding_info):
                position[symbol] = {"holding": True, "entry_price": price}
                save_position(position)

                log(f"✅ 模拟买入 {symbol} @ {price:.6f}")
                send_telegram_message(f"🟢 模拟买入 {symbol} @ {price:.6f} USDT")

            elif strategy.should_sell(symbol, price, holding_info):
                entry_price = holding_info["entry_price"]
                profit = price - entry_price
                pct = (profit / entry_price) * 100 if entry_price else 0

                log(f"✅ 模拟卖出 {symbol} @ {price:.6f}，盈亏：{profit:.6f}（{pct:.2f}%）")
                send_telegram_message(
                    f"🔴 模拟卖出 {symbol} @ {price:.6f} USDT\n盈亏：{profit:.6f} USDT（{pct:.2f}%）"
                )
                position[symbol] = {"holding": False, "entry_price": None}
                save_position(position)

            elif strategy.should_stop_loss(symbol, price, holding_info):
                entry_price = holding_info["entry_price"]
                profit = price - entry_price
                pct = (profit / entry_price) * 100 if entry_price else 0

                log(f"💥 触发止损：{symbol} @ {price:.6f}，亏损：{profit:.6f}（{pct:.2f}%）")
                send_telegram_message(
                    f"🔻 模拟止损卖出 {symbol} @ {price:.6f} USDT\n亏损：{profit:.6f} USDT（{pct:.2f}%）"
                )
                position[symbol] = {"holding": False, "entry_price": None}
                save_position(position)

            else:
                log(f"⌛ {symbol} 无操作（未触发买卖条件）")

        time.sleep(INTERVAL)

    except Exception as e:
        log(f"❌ 出现错误：{e}")
        time.sleep(5)

# 📁 core/signal_handler.py

from config.logger import log
from config.position import save_position
from notify.telegram import send_telegram_message

def handle_buy(symbol, price, position):
    position[symbol] = {"holding": True, "entry_price": price}
    save_position(position)

    log(f"✅ 模拟买入 {symbol} @ {price:.6f}")
    send_telegram_message(f"🟢 模拟买入 {symbol} @ {price:.6f} USDT")


def handle_sell(symbol, price, holding_info, position):
    entry_price = holding_info["entry_price"]
    profit = price - entry_price
    pct = (profit / entry_price) * 100 if entry_price else 0

    log(f"✅ 模拟卖出 {symbol} @ {price:.6f}，盈亏：{profit:.6f}（{pct:.2f}%）")
    send_telegram_message(
        f"🔴 模拟卖出 {symbol} @ {price:.6f} USDT\n盈亏：{profit:.6f} USDT（{pct:.2f}%）"
    )
    position[symbol] = {"holding": False, "entry_price": None}
    save_position(position)


def handle_stop_loss(symbol, price, holding_info, position):
    entry_price = holding_info["entry_price"]
    loss = price - entry_price
    pct = (loss / entry_price) * 100 if entry_price else 0

    log(f"💥 触发止损：{symbol} @ {price:.6f}，亏损：{loss:.6f}（{pct:.2f}%）")
    send_telegram_message(
        f"🔻 模拟止损卖出 {symbol} @ {price:.6f} USDT\n亏损：{loss:.6f} USDT（{pct:.2f}%）"
    )
    position[symbol] = {"holding": False, "entry_price": None}
    save_position(position)

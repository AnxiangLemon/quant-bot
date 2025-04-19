import csv
import os
from datetime import datetime, timezone

from config.logger import log
from config.position import save_position
from notify.telegram import send_telegram_message

TRADE_LOG_PATH = "logs/trade_history.csv"

def record_trade_to_csv(symbol, action, price, profit=None, pct=None):
    """
    将交易记录追加写入 CSV 文件
    """
    os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)

    file_exists = os.path.isfile(TRADE_LOG_PATH)
    with open(TRADE_LOG_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            #writer.writerow(["timestamp", "symbol", "action", "price", "profit", "pct"])
            writer.writerow(["时间", "交易对", "操作", "价格", "盈亏金额", "盈亏比例"])

        writer.writerow([
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            action,
            f"{price:.6f}",
            f"{profit:.6f}" if profit is not None else "",
            f"{pct:.2f}" if pct is not None else ""
        ])

def handle_buy(symbol, price, position):
    position[symbol] = {"holding": True, "entry_price": price}
    save_position(position)

    log(f"✅ 模拟买入 {symbol} @ {price:.6f}")
    send_telegram_message(f"🟢 模拟买入 {symbol} @ {price:.6f} USDT")

    record_trade_to_csv(symbol, "BUY", price)

def handle_sell(symbol, price, holding_info, position):
    entry_price = holding_info["entry_price"]
    profit = price - entry_price
    pct = (profit / entry_price) * 100 if entry_price else 0

    log(f"✅ 模拟卖出 {symbol} @ {price:.6f}，盈亏：{profit:.6f}（{pct:.2f}%）")
    send_telegram_message(
        f"🔴 模拟卖出 {symbol} @ {price:.6f} USDT\n盈亏：{profit:.6f} USDT（{pct:.2f}%）"
    )

    record_trade_to_csv(symbol, "SELL", price, profit, pct)
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

    record_trade_to_csv(symbol, "STOP_LOSS", price, loss, pct)
    position[symbol] = {"holding": False, "entry_price": None}
    save_position(position)

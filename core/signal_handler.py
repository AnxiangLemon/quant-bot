import csv
import os
from datetime import datetime, timezone

from config.logger import log
from config.position import save_position
from notify.telegram import send_telegram_message
from config.config import SYMBOL_CONFIGS  # 确保引入配置

# CSV 日志文件路径
TRADE_LOG_PATH = "logs/trade_history.csv"

def record_trade_to_csv(symbol, action, price, profit=None, pct=None, reason=None):
    """
    将交易记录追加写入 CSV 文件中。
    
    参数:
        symbol (str): 交易对名称，例如 BTC/USDT
        action (str): 动作，如 BUY, SELL, STOP_LOSS
        price (float): 成交价格
        profit (float): 盈亏金额（卖出或止损时）
        pct (float): 盈亏比例（百分比形式）
        reason (str): 止损原因或说明（如：atr、trailing、macd）
    """
    os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(TRADE_LOG_PATH)

    with open(TRADE_LOG_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            # 写入表头（中文）
            writer.writerow(["时间", "交易对", "操作", "价格", "盈亏金额", "盈亏比例", "原因"])

        writer.writerow([
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            action,
            f"{price:.6f}",
            f"{profit:.6f}" if profit is not None else "",
            f"{pct:.2f}" if pct is not None else "",
            reason or ""
        ])


def reset_position(symbol, position):
    """
    清空某个币种的持仓状态，适用于止损或卖出后的重置。

    参数:
        symbol (str): 币种，如 BTC/USDT
        position (dict): 全部仓位数据的字典
    """
    position[symbol] = {
        "holding": False,
        "entry_price": None,
        "trailing_stop_price": None,
        "max_price": None
    }


def handle_buy(symbol, price, position):
    """
    处理买入逻辑，初始化持仓数据并记录交易。

    参数:
        symbol (str): 币种
        price (float): 当前价格
        position (dict): 所有币种的仓位字典
    """
    config = SYMBOL_CONFIGS[symbol]
    trailing_pct = config.get("trailing_stop_pct", 0.02)

    position[symbol] = {
        "holding": True,
        "entry_price": price,
        "trailing_stop_price": price * (1 - trailing_pct),
        "max_price": price
    }

    save_position(position)

    log(f"✅ 模拟买入 {symbol} @ {price:.6f}")
    send_telegram_message(f"🟢 模拟买入 {symbol} @ {price:.6f} USDT")

    record_trade_to_csv(symbol, "BUY", price)


def handle_sell(symbol, price, holding_info, position):
    """
    处理卖出逻辑，计算盈亏并记录。

    参数:
        symbol (str): 币种
        price (float): 当前价格
        holding_info (dict): 当前币种的持仓信息
        position (dict): 所有仓位字典
    """
    entry_price = holding_info["entry_price"]
    profit = price - entry_price
    pct = (profit / entry_price) * 100 if entry_price else 0

    log(f"✅ 模拟卖出 {symbol} @ {price:.6f}，盈亏：{profit:.6f}（{pct:.2f}%）")
    send_telegram_message(
        f"🔴 模拟卖出 {symbol} @ {price:.6f} USDT\n盈亏：{profit:.6f} USDT（{pct:.2f}%）"
    )

    record_trade_to_csv(symbol, "SELL", price, profit, pct)
    reset_position(symbol, position)
    save_position(position)


def handle_stop_loss(symbol, price, holding_info, position):
    """
    处理止损逻辑，记录止损原因并重置持仓。

    参数:
        symbol (str): 币种
        price (float): 当前价格
        holding_info (dict): 当前币种的持仓信息
        position (dict): 所有仓位字典
    """
    entry_price = holding_info["entry_price"]
    loss = price - entry_price
    pct = (loss / entry_price) * 100 if entry_price else 0

    # 提取止损原因（由策略函数注入）
    reason = holding_info.get("stop_reason", "unknown")

    log(f"💥 触发止损：{symbol} @ {price:.6f}，亏损：{loss:.6f}（{pct:.2f}%）")
    send_telegram_message(
        f"🔻 模拟止损卖出 {symbol} @ {price:.6f} USDT\n"
        f"亏损：{loss:.6f} USDT（{pct:.2f}%）\n"
        f"原因：{reason}"
    )

    record_trade_to_csv(symbol, "STOP_LOSS", price, loss, pct, reason)
    reset_position(symbol, position)
    save_position(position)

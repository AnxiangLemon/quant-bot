import csv
import os
from datetime import datetime
from config.logger import log
from config.position import save_position
from notify.telegram import send_telegram_message
from config.config import SYMBOL_CONFIGS, DRY_RUN, TRADE_FEE_RATE
from binance.services import place_order


def get_local_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_trade_log_path():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return f"logs/trade_history_{date_str}.csv"

def record_trade_to_csv(symbol, action, price, amount=None, profit=None, pct=None, reason=None, buy_fee=None, sell_fee=None):
    path = get_trade_log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_exists = os.path.isfile(path)

    try:
        with open(path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["时间", "交易对", "操作", "价格", "数量", "盈亏金额", "盈亏比例", "买入手续费", "卖出手续费", "原因"])

            writer.writerow([
                get_local_time(),
                symbol,
                action,
                f"{price:.6f}",
                f"{amount:.6f}" if amount is not None else "",
                f"{profit:.6f}" if profit is not None else "",
                f"{pct:.2f}" if pct is not None else "",
                f"{buy_fee:.6f}" if buy_fee else "",
                f"{sell_fee:.6f}" if sell_fee else "",
                reason or ""
            ])
    except Exception as e:
        log(f"⚠️ 写入交易日志失败: {e}")

def reset_position(symbol, position):
    position[symbol] = {
        "holding": False,
        "entry_price": None,
        "amount": None,
        "trailing_stop_price": None,
        "max_price": None,
        "buy_fee": None
    }

def handle_buy(symbol, price, position):
    config = SYMBOL_CONFIGS[symbol]
    trailing_pct = config.get("trailing_stop_pct", 0.02)
    amount = config.get("amount", 0.01)
    fee_rate = config.get("fee_rate", TRADE_FEE_RATE)

    total_cost = price * amount
    fee = total_cost * fee_rate
    cost_with_fee = total_cost + fee

    position[symbol] = {
        "holding": True,
        "amount": amount,
        "entry_price": price,
        "trailing_stop_price": price * (1 - trailing_pct),
        "max_price": price,
        "buy_fee": fee
    }

    save_position(position)

    log(f"✅ 买入 {symbol} @ {price:.6f}，数量: {amount}, 手续费: {fee:.6f}, 总成本: {cost_with_fee:.2f} USDT")
    send_telegram_message(
        f"🟢 模拟买入 {symbol}\n"
        f"价格: {price:.6f} USDT\n"
        f"数量: {amount}\n"
        f"买入手续费: {fee:.6f}\n"
        f"总成本: {cost_with_fee:.2f} USDT"
    )

    if not DRY_RUN:
        place_order(symbol, "BUY", amount, order_type="MARKET")

    record_trade_to_csv(symbol, "BUY", price, amount=amount, buy_fee=fee)

def finalize_trade(symbol, price, holding_info, position, action="SELL", reason=None, ignore_min_profit=False):
    # 从持仓信息中获取买入价格、买入数量、买入手续费
    entry_price = holding_info["entry_price"]
    amount = holding_info.get("amount", 0.01)
    buy_fee = holding_info.get("buy_fee", 0.0)

    # 获取当前交易对的手续费率（默认使用全局设置）
    fee_rate = SYMBOL_CONFIGS[symbol].get("fee_rate", TRADE_FEE_RATE)

    # 最小可接受的净利润门槛（比如 0.5 USDT），只有非止损才判断
   # MIN_PROFIT_USDT = SYMBOL_CONFIGS[symbol].get("min_profit", 0.5)

    # 计算本次卖出收入（未扣手续费）
    sell_total = price * amount

    # 卖出手续费
    sell_fee = sell_total * fee_rate

    # 计算净利润：卖出收益 - 买入成本 - 买入手续费 - 卖出手续费
    net_profit = sell_total - (entry_price * amount) - buy_fee - sell_fee

    # 计算盈亏百分比（以买入成本为基准）
    pct = (net_profit / (entry_price * amount)) * 100 if entry_price else 0

    # # 如果不是止损操作（ignore_min_profit=False），且利润低于设定阈值，则跳过卖出
    # if not ignore_min_profit and net_profit < MIN_PROFIT_USDT:
    #     log(f"⚠️ 净利润 {net_profit:.6f} 小于最小门槛 {MIN_PROFIT_USDT}，不执行卖出")
    #     send_telegram_message(
    #         f"⚠️ {symbol} 净利润过低：{net_profit:.6f} USDT（{pct:.2f}%）\n"
    #         f"买入价: {entry_price:.6f}，卖出价: {price:.6f}\n"
    #         f"手续费共: {buy_fee + sell_fee:.6f} → 利润被吃掉了"
    #     )
    #     return  # 中止交易

    # 表情和文案根据类型（正常卖出 or 止损）切换
    emoji = "🔴" if action == "SELL" else "🔻"
    result_text = "卖出" if action == "SELL" else "止损卖出"

    # 日志记录卖出成功详情
    log(
        f"✅ 模拟{result_text} {symbol} @ {price:.6f}，数量: {amount}，净盈亏: {net_profit:.6f}（{pct:.2f}%），卖出手续费: {sell_fee:.6f}"
    )

    # 发送 Telegram 通知，显示盈亏详情
    send_telegram_message(
        f"{emoji} 模拟{result_text} {symbol}\n"
        f"买入价: {entry_price:.6f}，卖出价: {price:.6f}\n"
        f"数量: {amount}\n"
        f"总手续费: {buy_fee + sell_fee:.6f} USDT\n"
        f"净盈亏: {net_profit:.6f} USDT（{pct:.2f}%）"
        + (f"\n原因: {reason}" if reason else "")
    )

    # 实盘环境下才发送实际订单（此处为市价单）
    if not DRY_RUN:
        place_order(symbol, "SELL", amount, order_type="MARKET")

    # 写入交易记录 CSV 文件
    record_trade_to_csv(
        symbol, action, price, amount=amount,
        profit=net_profit, pct=pct, reason=reason,
        buy_fee=buy_fee, sell_fee=sell_fee
    )

    # 清空仓位状态
    reset_position(symbol, position)
    save_position(position)


def handle_sell(symbol, price, holding_info, position):
    finalize_trade(symbol, price, holding_info, position, action="SELL")

def handle_stop_loss(symbol, price, holding_info, position):
    reason = holding_info.get("stop_reason", "unknown")
    finalize_trade(symbol, price, holding_info, position, action="STOP_LOSS", reason=reason, ignore_min_profit=True)

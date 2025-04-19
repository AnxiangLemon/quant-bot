from binance.exchange import exchange
from config.logger import log
from datetime import datetime, timedelta


def get_ticker_price(symbol):
    """
    获取当前交易对最新成交价。
    例如 symbol="BTC/USDT"，返回当前市场成交价。
    """
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']


def get_balance(asset):
    """
    获取账户中指定资产的可用余额。
    例如 asset="USDT" 或 "BTC"
    """
    try:
        balance = exchange.fetch_balance()
        return balance['free'].get(asset.upper(), 0.0)
    except Exception as e:
        log(f"⚠️ 获取余额失败: {e}")
        return 0.0


def get_precision_info(symbol):
    """
    获取交易对的最小下单单位 stepSize 和最小金额 minNotional。
    用于自动精度适配和合法性校验。
    返回: (step_size, min_notional)
    """
    try:
        info = exchange.client().fetch_market(symbol)
        step_size = info['precision']['amount']  # 数量精度（如 0.0001）
        min_notional = info['limits']['cost']['min']  # 最小交易金额（如 10 USDT）
        return step_size, min_notional
    except Exception as e:
        log(f"⚠️ 获取精度失败: {e}")
        return 0.0001, 10  # 默认安全值


def round_to_precision(value, precision):
    """
    将数量 value 按照最小精度 precision 进行截断处理。
    如 value=0.00357, precision=0.001 -> 返回 0.003
    """
    factor = 1 / precision
    return int(value * factor) / factor


def cancel_order_if_timeout(symbol, order_id, timeout_seconds=20):
    """
    如果限价单在指定时间内未成交，则自动撤销。
    适用于挂单策略，防止长时间不成交导致持仓紊乱。

    参数:
        symbol (str): 交易对
        order_id (str): Binance 返回的订单ID
        timeout_seconds (int): 超时时间（秒）
    """
    try:
        order_info = exchange.fetch_order(order_id, symbol.replace("/", ""))
        create_time = datetime.fromtimestamp(order_info['timestamp'] / 1000)
        now = datetime.now()

        if order_info['status'] in ('closed', 'canceled'):
            log(f"✅ 订单已处理完毕（状态：{order_info['status']}），无需取消。")
            return

        if (now - create_time) > timedelta(seconds=timeout_seconds):
            exchange.cancel_order(order_id, symbol.replace("/", ""))
            log(f"⏳ 超时未成交，已撤销订单 ID: {order_id}")

    except Exception as e:
        log(f"⚠️ 检查或撤销订单失败: {e}")


def place_order(symbol: str, side: str, quantity: float, order_type: str = "MARKET", price_offset_pct: float = 0.005):
    """
    自动处理下单逻辑，包括：
    - 获取最新市场价
    - 判断余额是否足够
    - 自动调整下单精度（防止失败）
    - 支持市价单或限价单（默认市价）
    - 限价挂单支持自动撤单（由外部调用 cancel_order_if_timeout）

    参数：
        symbol (str): 交易对，如 "BTC/USDT"
        side (str): "BUY" 或 "SELL"
        quantity (float): 下单数量（基础币）
        order_type (str): "MARKET" 或 "LIMIT"
        price_offset_pct (float): 限价挂单时的偏移百分比，例如 0.005 表示 ±0.5%

    返回：
        dict or None: Binance 订单回执，失败返回 None
    """
    base, quote = symbol.upper().split("/")
    market_price = get_ticker_price(symbol)
    step_size, min_notional = get_precision_info(symbol)

    quantity = round_to_precision(quantity, step_size)

    if side.upper() == "BUY":
        cost_estimate = market_price * quantity * 1.01
        quote_balance = get_balance(quote)
        if quote_balance < cost_estimate:
            log(f"❌ BUY 失败，{quote} 余额不足：需 {cost_estimate:.2f}，现有 {quote_balance:.2f}")
            return None

    elif side.upper() == "SELL":
        base_balance = get_balance(base)
        if base_balance < quantity:
            log(f"❌ SELL 失败，{base} 余额不足：需 {quantity}，现有 {base_balance}")
            return None

    try:
        if order_type.upper() == "MARKET":
            order = exchange.create_order(
                symbol=symbol.replace("/", ""),
                type="market",
                side=side.lower(),
                amount=quantity
            )
        elif order_type.upper() == "LIMIT":
            if side.upper() == "BUY":
                limit_price = market_price * (1 - price_offset_pct)
            else:
                limit_price = market_price * (1 + price_offset_pct)
            limit_price = round(limit_price, 2)
            order = exchange.create_order(
                symbol=symbol.replace("/", ""),
                type="limit",
                side=side.lower(),
                amount=quantity,
                price=limit_price,
                params={"timeInForce": "GTC"}
            )
            log(f"⏳ 已挂限价单，价格: {limit_price}，等待成交... 可调用 cancel_order_if_timeout 设定超时撤单。")
        else:
            log(f"❌ 不支持的订单类型: {order_type}")
            return None

        log(f"✅ 成功下单 {symbol} [{side}] 数量: {quantity}")
        return order

    except Exception as e:
        log(f"❌ 下单失败: {e}")
        return None

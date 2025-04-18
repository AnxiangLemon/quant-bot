from binance.exchange import exchange

def get_ticker_price(symbol):
    """
    获取指定交易对的最新价格（ticker）。
    
    参数:
        symbol (str): 交易对符号，例如 "BTC/USDT"
    
    返回:
        float: 最新成交价格（last price）
    """
    ticker = exchange.fetch_ticker(symbol)  # 从交易所获取当前行情数据
    return ticker['last']  # 返回最新成交价



# 导入 ccxt 库，用于连接加密货币交易所 API
import ccxt

# 从自定义模块中导入 Binance API 的密钥配置
from modules.config import API_KEY, API_SECRET

# 初始化 Binance 交易所对象，配置 API 密钥和参数
exchange = ccxt.binance({
    'apiKey': API_KEY,               # 设置 API Key
    'secret': API_SECRET,           # 设置 API Secret
    'enableRateLimit': True,        # 启用速率限制，以防止触发 API 限频
    'options': {'defaultType': 'spot'}  # 使用现货市场（spot），而非合约或杠杆市场
})

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

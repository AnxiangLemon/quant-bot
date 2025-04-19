# 导入 ccxt 库，用于连接加密货币交易所 API
import ccxt

# 从自定义模块中导入 Binance API 的密钥配置
from config.config import BINANCE_API_KEY, BINANCE_API_SECRET

# 初始化 Binance 交易所对象，配置 API 密钥和参数
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,               # 设置 API Key
    'secret': BINANCE_API_SECRET,           # 设置 API Secret
    'enableRateLimit': True,        # 启用速率限制，以防止触发 API 限频
    'options': {'defaultType': 'spot'}  # 使用现货市场（spot），而非合约或杠杆市场
})


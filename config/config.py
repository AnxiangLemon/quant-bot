import os
from dotenv import load_dotenv

# 加载 .env 文件中的变量
load_dotenv()

# 从环境变量中获取
#币安api
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# ===================== Telegram 设置 ========================
# 你的 Telegram Bot Token，从 @BotFather 创建 Bot 后获得
# 用于让你的交易机器人能通过 Telegram 给你发消息
# 你的 Telegram 用户 ID 或频道 ID
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ======================== 策略参数 ==========================

# 每个币种的完整策略配置（包含买入价、买入数量、止盈比例、止损比例）
# 每个币种的完整策略配置字典（用于量化策略中参数控制）
SYMBOL_CONFIGS = {
    "BTC/USDT": {
        #  交易参数
        "buy_price": 84580,            # 买入触发价格（当现价低于此值才考虑买入）
        "amount": 0.001,               # 买入数量（单位为 BTC）
        "fee_rate":0.001,              # 手续费  千分之一
        "take_profit_pct": 0.03,       # 止盈比例（如 0.03 表示盈利3%即卖出）
        "stop_loss_ratio": 0.98,       # 基础止损比例（作为兜底策略：入场价 * 0.99）

        #  技术指标参数
        "macd_params": (12, 26, 9),    # MACD 参数（快速EMA周期, 慢速EMA周期, 信号线周期）
        "kdj_params": (9, 3),          # KDJ 参数（周期, 平滑因子）
        "atr_window": 14,              # ATR（平均真实波动范围）计算窗口

        #  技术策略判断条件
        "max_j_buy": 70,               # 当 J < 70 才允许买入（防止高位追涨）
        "min_j_sell": 90,              # 当 J > 90 时考虑超买卖出

        #  多重止损机制
        "fixed_stop_loss_pct": 0.02,         # 固定止损（入场价下跌 2% 即止损）
        "atr_stop_multiplier": 2.0,          # ATR 动态止损系数（止损线 = entry - ATR*系数）
        "max_drawdown_pct": 0.05,            # 最大浮盈回撤（从最大涨幅回撤 5% 即止损）
        "trailing_stop_pct": 0.02,           # 移动止损比例（随价格上升而抬升止损线）

        "stop_loss_priority": [              # 各止损方式判断的优先顺序（先匹配先执行）
            "trailing",      # 移动止损
            "fixed",         # 固定百分比止损
            "atr",           # ATR 波动止损
            "macd",          # MACD 趋势止损
            "drawdown"       # 最大回撤止损
        ]
    },

    "ETH/USDT": {
        "buy_price": 1600,              # 以太坊的买入价格
        "amount": 0.02,                 # 买入 0.02 ETH
        "take_profit_pct": 0.04,        # 盈利 4% 即止盈
        "stop_loss_ratio": 0.985,       # 兜底止损线：入场价 * 0.985

        "macd_params": (12, 26, 9),
        "kdj_params": (9, 3),
        "atr_window": 14,

        "max_j_buy": 65,                # 略微保守，只在 J < 65 时买入
        "min_j_sell": 85,               # 超买判断更灵敏

        "fixed_stop_loss_pct": 0.025,
        "atr_stop_multiplier": 2.2,
        "max_drawdown_pct": 0.06,
        "trailing_stop_pct": 0.025,

        "stop_loss_priority": [
            "trailing",
            "atr",
            "fixed",
            "macd",
            "drawdown"
        ]
    },

    "DOGE/USDT": {
        "buy_price": 0.16,              # 狗狗币的建仓价
        "amount": 20,                   # 买入 20 个 DOGE
        "take_profit_pct": 0.05,        # 盈利 5% 即止盈
        "stop_loss_ratio": 0.98,        # 亏损 2% 止损

        "macd_params": (12, 26, 9),
        "kdj_params": (9, 3),
        "atr_window": 14,

        "max_j_buy": 60,                # J < 60 才可买入（防止过热买入）
        "min_j_sell": 80,               # 超买 J > 80 卖出

        "fixed_stop_loss_pct": 0.03,
        "atr_stop_multiplier": 2.5,
        "max_drawdown_pct": 0.08,
        "trailing_stop_pct": 0.03,

        "stop_loss_priority": [
            "atr",
            "trailing",
            "fixed",
            "drawdown",
            "macd"
        ]
    }
}


# 每轮循环检查行情的时间间隔（单位：秒）
INTERVAL = 5

# 是否启用“模拟交易模式”
DRY_RUN = True

# 交易手续费率（默认 0.1%）
TRADE_FEE_RATE = 0.001
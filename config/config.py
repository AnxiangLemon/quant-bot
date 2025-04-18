# config.py（公开模板 + 自动加载本地配置）

try:
    from config_local import *  # 引入所有本地私密变量
except ImportError:
    # 若无 config_local，则定义默认值，或报错提示
    print("⚠️ 警告：未找到 config_local.py，将使用默认配置")
    # 交易所，配置 API 密钥和参数
    API_KEY = ""
    API_SECRET = ""

    # ===================== Telegram 设置 ========================

    # 你的 Telegram Bot Token，从 @BotFather 创建 Bot 后获得
    # 用于让你的交易机器人能通过 Telegram 给你发消息
    TELEGRAM_TOKEN = ''

    # 你的 Telegram 用户 ID 或频道 ID
    # 建议使用 @userinfobot 获取你的 chat_id
    # 所有交易日志会发送到这个 chat_id 对应的对话窗口
    TELEGRAM_CHAT_ID = ''


    # ======================== 策略参数 ==========================

    # 每个币种的完整策略配置（包含买入价、买入数量、止盈比例、止损比例）
    SYMBOL_CONFIGS = {
        "BTC/USDT": {
            "buy_price": 84580,
            "amount": 0.001,
            "take_profit_pct": 0.03,
            "stop_loss_ratio": 0.99
        },
        "ETH/USDT": {
            "buy_price": 1600,
            "amount": 0.02,
            "take_profit_pct": 0.04,
            "stop_loss_ratio": 0.985
        },
        "DOGE/USDT": {
            "buy_price": 0.16,
            "amount": 20,
            "take_profit_pct": 0.05,
            "stop_loss_ratio": 0.98
        }
    }

    # 每轮循环检查行情的时间间隔（单位：秒）
    INTERVAL = 10

    # 是否启用“模拟交易模式”
    DRY_RUN = True




# 🧠 gridbot - 模拟网格量化交易机器人

gridbot 是一个基于 Python 和 Binance API 的开源模拟网格量化交易机器人。
支持多币种监控、动态策略调整、止盈止损机制、Telegram 通知、持久化持仓状态，是入门量化交易和策略验证的极佳项目。

---

## 🚀 功能亮点

- ✅ **支持多币种网格交易策略**（BTC/ETH/DOGE/...）
- ✅ **插件式策略架构**，可自由添加/切换策略模块
- ✅ **买入/卖出/止损 策略可配置**（例如盈利超过 3% 卖出）
- ✅ **模拟盘模式（Dry Run）**，安全验证策略
- ✅ **自动持仓保存**，断电后可续跑
- ✅ **支持 Telegram 通知**，交易结果实时推送
- ✅ **交易行为日志记录**，方便复盘与调试

---

## 🛠 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/AnxiangLemon/gridbot.git
cd gridbot
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 和参数

在 `modules/config.py` 中设置：

- Binance API Key / Secret（模拟盘不需要）
- 各币种的买入价、止盈比例、止损比例等参数
- Telegram 通知（可选）

### 4. 启动机器人

```bash
python grid_bot.py
```

---

## 🧩 策略插件

策略实现统一继承 `BaseStrategy` 接口：
```python

class BaseStrategy:
    def should_buy(...):
    def should_sell(...):
    def should_stop_loss(...):
```

默认内置策略：`SimpleThresholdStrategy`，基于配置判断买卖/止损。

你可以自由添加如 `MACDStrategy`, `RSIStrategy` 等自定义模块。

---

## 📁 项目结构

```
quant-grid/
├── grid_bot.py                    # 主程序
├── modules/
│   ├── config.py                  # 全部币种+策略参数配置
│   ├── logger.py                  # 日志打印与持久化
│   ├── position.py                # 本地持仓状态存取
│   ├── telegram_notify.py         # Telegram 通知模块
│   ├── binance_client.py          # Binance API 封装
│   ├── utils.py                   # 波动率等辅助函数
│   └── strategies/
│       ├── base_strategy.py       # 策略接口定义
│       └── simple_threshold.py    # 默认阈值策略
```

---

## 📜 授权协议

MIT License - 欢迎 fork/使用/二次开发，转载请注明来源。

---

## 💬 联系与反馈

欢迎通过 [issues](https://github.com/AnxiangLemon/gridbot/issues) 提问或提交建议。
如果你觉得项目有帮助，可以点个 ⭐ 支持一下！

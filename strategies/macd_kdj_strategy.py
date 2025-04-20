# 📁 strategies/macd_kdj_strategy.py

from strategies.base_strategy import BaseStrategy
from config.config import SYMBOL_CONFIGS, TRADE_FEE_RATE
from config.logger import log


class MACDKDJStrategy(BaseStrategy):
    """
    MACD + KDJ 技术面策略，支持配置化：
    - 买入：MACD 金叉或 KDJ 金叉 且 J < max_j_buy
    - 卖出：MACD 死叉 或 J > min_j_sell
    - 止损：价格 < entry_price - ATR * atr_stop_multiplier
    """

    def should_buy(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        if position.get("holding", False):
            return False

        indicators = kwargs.get("indicators", {})
        config = SYMBOL_CONFIGS[symbol]
        max_j = config.get("max_j_buy", 70)

        if not self._check_indicators(indicators):
            return False

        # 获取前一周期和当前周期的 MACD DIF/DEA 值
        dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]  # 上一个周期
        dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]      # 当前周期

        # 获取前一周期和当前周期的 KDJ K/D 值
        k_y, d_y = indicators["K"][-2], indicators["D"][-2]
        k, d = indicators["K"][-1], indicators["D"][-1]

        # 当前周期的 J 值
        j = indicators["J"][-1]

        # 判断条件：MACD 金叉 或 KDJ 金叉 且 J 值未过热
        return (
            ((dif_y < dea_y and dif > dea) or (k_y < d_y and k > d)) #and j < max_j
        )

    def should_sell(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        判断是否应该主动卖出（非止损行为）。
        该方法综合技术面卖出信号 + 最小利润过滤，确保：
        - 满足 MACD 死叉 或 J 值过热 等技术指标条件；
        - 同时当前净利润达到配置的最小利润阈值（如 min_profit = 0.5 USDT）；
        - 否则不会卖出（等待更好机会）。
        
        参数：
            symbol (str): 交易对，如 "BTC/USDT"
            price (float): 当前市场价格
            position (dict): 当前币种持仓信息
            kwargs:
                indicators (dict): 指标数据，如 MACD、KDJ、ATR 等

        返回：
            bool: 是否满足主动卖出条件（True 表示应当卖出）
        """

        # 1️⃣ 如果当前没有持仓状态（未买入），则不考虑卖出
        if not position.get("holding", False):
            return False

        # 2️⃣ 获取传入的指标数据（由外部传入，如 MACD、KDJ 等）
        indicators = kwargs.get("indicators", {})
        config = SYMBOL_CONFIGS[symbol]  # 获取当前币种的策略配置
        min_j = config.get("min_j_sell", 90)  # 卖出时 J 值过热的阈值（技术面）

        # 3️⃣ 检查指标数据是否齐全，避免出现 index 或 key 错误
        if not self._check_indicators(indicators):
            return False

        # 4️⃣ 取出 MACD 的前一周期 和 当前周期数据，用于判断死叉
        dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]  # 上一根K线的 DIF/DEA
        dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]      # 当前K线的 DIF/DEA

        # 5️⃣ 取出当前周期的 KDJ 的 J 值
        j = indicators["J"][-1]

        # 6️⃣ 技术面判断：如果出现 MACD 死叉 或 J > min_j（过热），触发卖出信号
        technical_signal = (dif_y > dea_y and dif < dea) or (j > min_j)

        # 7️⃣ 如果技术面不满足，则不考虑利润，直接返回 False
        if not technical_signal:
            return False

        # 8️⃣ 技术面满足后，判断当前是否达到设定的最小盈利门槛（避免小赚就卖）
        entry_price = position.get("entry_price")               # 原始买入价格
        amount = position.get("amount", 0.01)                   # 持仓数量（默认 0.01）
        buy_fee = position.get("buy_fee", 0.0)                  # 原始买入手续费
        fee_rate = config.get("fee_rate", TRADE_FEE_RATE)       # 当前手续费率
       # min_profit = config.get("min_profit", 0.5)              # 最小净利润限制（如 0.5 USDT）

        # 获取配置中的最小利润百分比（例如：1%）
        min_profit_pct = config.get("min_profit_pct", 1.0)  # 默认 1%
         # 计算最小利润金额
        min_profit_value = entry_price * amount * (min_profit_pct / 100)
        
         # 9️⃣ 计算当前卖出价格下的毛收入（price * 数量）
        sell_total = price * amount

        # 🔟 卖出手续费 = 总卖出金额 * 费率
        sell_fee = sell_total * fee_rate

        # 🔁 计算净利润 = 卖出收入 - 买入成本 - 手续费
        net_profit = sell_total - (entry_price * amount) - buy_fee - sell_fee

        #  如果净利润未达到设定的最小利润，则拒绝卖出
        if net_profit < min_profit_value:
            log(f"⏸️ 盈利未达最小门槛 {net_profit:.6f} < {min_profit_value:.6f}，暂不卖出")
            return False

        # ✅ 技术面满足、利润也达标，允许卖出
        return True

    def should_stop_loss(self, symbol: str, price: float, position: dict, **kwargs) -> bool:
        """
        综合止损判断函数，支持多种止损逻辑，并可配置优先级顺序。
        """

        entry_price = position.get("entry_price")
        if not position.get("holding", False) or not entry_price:
            return False

        config = SYMBOL_CONFIGS[symbol]
        indicators = kwargs.get("indicators", {})
        atr_values = indicators.get("ATR", [])

        # 止损优先级顺序（可配置）
        priorities = config.get("stop_loss_priority", ["trailing", "fixed", "atr", "macd", "drawdown"])

        for method in priorities:
            if method == "fixed":
                fix_stop_pct = config.get("fixed_stop_loss_pct", 0.02)
                if price < entry_price * (1 - fix_stop_pct):
                    log("🔻 触发固定百分比止损")
                    indicators["stop_reason"] = "fixed"
                    return True

            elif method == "atr":
                atr_multiplier = config.get("atr_stop_multiplier", 2.0)
                if atr_values and len(atr_values) >= 1:
                    latest_atr = atr_values[-1]
                    stop_price = entry_price - atr_multiplier * latest_atr
                    if price < stop_price:
                        log("🔻 触发 ATR 动态止损")
                        indicators["stop_reason"] = "atr"
                        return True

            elif method == "macd":
                if self._check_indicators(indicators):
                    dif_y, dea_y = indicators["DIF"][-2], indicators["DEA"][-2]
                    dif, dea = indicators["DIF"][-1], indicators["DEA"][-1]
                    if dif_y > dea_y and dif < dea and price < entry_price:
                        log("🔻 触发 MACD 死叉趋势止损")
                        indicators["stop_reason"] = "macd"
                        return True

            elif method == "drawdown":
                max_price = position.get("max_price", entry_price)
                drawdown_pct = (max_price - price) / max_price
                max_drawdown_pct = config.get("max_drawdown_pct", 0.05)
                if drawdown_pct >= max_drawdown_pct:
                    log(f"🔻 触发最大回撤止损：回撤 {drawdown_pct:.2%}")
                    indicators["stop_reason"] = "drawdown"
                    return True

            elif method == "trailing":
                trailing_stop_price = position.get("trailing_stop_price")
                if trailing_stop_price and price < trailing_stop_price:
                    log(f"🔻 触发移动止损：当前价格 {price:.2f} < 止损线 {trailing_stop_price:.2f}")
                    indicators["stop_reason"] = "trailing"
                    return True

        return False


    @staticmethod
    def _check_indicators(indicators: dict) -> bool:
        """
        检查指标是否完整，且每个关键指标序列长度不少于 2（用于计算金叉/死叉）
        """
        required_keys = ["DIF", "DEA", "K", "D", "J", "ATR"]
        return all(key in indicators and len(indicators[key]) >= 2 for key in required_keys)

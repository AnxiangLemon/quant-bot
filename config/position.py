import json
import os

# 定义保存仓位信息的文件名
POSITION_FILE = "position.json"

def load_position():
    """
    从本地文件加载仓位信息。
    如果文件存在，则读取其内容并返回一个字典格式的数据；
    如果文件不存在，则返回一个默认的空仓结构。
    
    返回:
        dict: 包含持仓状态、入场价、移动止损线和最大价格的字典。
    """
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # 避免读取异常导致程序中断
                return {
                    "holding": False,
                    "entry_price": None,
                    "trailing_stop_price": None,
                    "max_price": None
                }

    # 默认仓位结构（无持仓）
    return {}

def save_position(position):
    """
    将当前仓位信息保存到本地文件。
    
    参数:
        position (dict): 包含以下键的字典：
            - holding: 是否持仓
            - entry_price: 入场价
            - trailing_stop_price: 当前移动止损位
            - max_price: 持仓期间最高价（用于回撤止损）
    """
    with open(POSITION_FILE, 'w') as f:
        json.dump(position, f, indent=4)

def update_trailing_stop(position: dict, price: float, trailing_pct: float) -> bool:
    """
    更新移动止损价格和最大价格。

    该函数仅在价格上涨时更新止损线或最大值，并返回是否发生实际变化。
    
    参数:
        position (dict): 当前币种的持仓字典，需包含 holding、trailing_stop_price、max_price
        price (float): 当前最新市场价格
        trailing_pct (float): 移动止损百分比（如 0.02 表示 2%）
    
    返回:
        bool: 如果 trailing_stop_price 或 max_price 被更新，返回 True；否则返回 False
    """
    if not position.get("holding"):
        return False

    updated = False  # 标志是否发生了更新

    # 计算新的止损位（随着上涨而上移）
    trailing_stop = price * (1 - trailing_pct)
    old_stop = position.get("trailing_stop_price")

    if old_stop is None or trailing_stop > old_stop:
        position["trailing_stop_price"] = trailing_stop
        updated = True

    # 更新最大价格（只允许向上更新）
    max_price = position.get("max_price")
    if max_price is None or price > max_price:
        position["max_price"] = price
        updated = True

    return updated

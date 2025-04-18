import json
import os

# 定义保存仓位信息的文件名
POSITION_FILE = "position.json"

def load_position():
    """
    从本地文件加载仓位信息。
    如果文件存在，则读取其内容并返回一个字典格式的数据；
    如果文件不存在，则返回一个默认的空仓信息。
    
    返回:
        dict: 包含持仓状态（holding）和入场价格（entry_price）的字典。
    """
    if os.path.exists(POSITION_FILE):
        # 打开文件并读取 JSON 数据
        with open(POSITION_FILE, 'r') as f:
            return json.load(f)
    # 如果文件不存在，返回默认的空仓结构
    return {"holding": False, "entry_price": None}

def save_position(position):
    """
    将当前的仓位信息保存到本地文件。
    
    参数:
        position (dict): 包含持仓状态（holding）和入场价格（entry_price）的字典。
    """
    # 将字典写入文件，保存为 JSON 格式
    with open(POSITION_FILE, 'w') as f:
        json.dump(position, f)

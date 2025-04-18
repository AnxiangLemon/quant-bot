from datetime import datetime

LOG_FILE = "trade_log.txt"  # 设置日志文件路径

def log_to_file(msg):
    """将日志写入文件"""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:  # 使用 utf-8 编码
        log_file.write(msg + "\n")

def log(msg):
    """
    打印并记录日志到文件
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    
    # 打印到控制台
    print(log_msg)
    
    # 写入日志文件
    log_to_file(log_msg)

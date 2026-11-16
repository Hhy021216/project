"""日志模块：控制台 INFO + 文件 DEBUG。"""
import logging
import os
from config import config

def setup_logger(name=None):
    log_file = str(config.LOG_FILE)
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

    lg = logging.getLogger(name)
    lg.setLevel(logging.DEBUG)

    if lg.handlers:
        return lg

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    lg.addHandler(console_handler)
    lg.addHandler(file_handler)
    return lg


logger = setup_logger()

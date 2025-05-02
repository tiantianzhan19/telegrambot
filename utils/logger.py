# utils/logger.py - 日志配置

import logging

def setup_logger():
    """配置并返回日志记录器"""
    # 设置日志格式
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # 获取logger
    logger = logging.getLogger(__name__)
    return logger

# 创建logger实例
logger = setup_logger()

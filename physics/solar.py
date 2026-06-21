"""
太阳直射点模型 — Solar Declination
================================
计算太阳直射点纬度、季节名称、月份名称.
"""

import numpy as np


def get_solar_declination(month: float) -> float:
    """计算太阳直射点纬度.
    公式: delta = 23.5 deg * sin(2 * pi * (month - 3) / 12)
    关键节点: 春分(3月) 0 deg, 夏至(6月) +23.5 deg, 秋分(9月) 0 deg, 冬至(12月) -23.5 deg
    """
    return 23.5 * np.sin(2 * np.pi * (month - 3) / 12)


def get_season_name(month: float) -> str:
    """根据月份返回北半球季节名称 (气象季节)"""
    m = month % 12
    if 3 <= m < 6:
        return "春季"
    elif 6 <= m < 9:
        return "夏季"
    elif 9 <= m < 12:
        return "秋季"
    else:
        return "冬季"


def get_month_name(month: float) -> str:
    """将月份数字转为中文名称, 支持小数 (如 6.5 -> '6月中旬')"""
    m_int = int(np.floor(month))
    frac = month - m_int
    m_int = ((m_int - 1) % 12) + 1
    name = f"{m_int}月"
    if frac < 0.33:
        name += "上旬"
    elif frac < 0.67:
        name += "中旬"
    else:
        name += "下旬"
    return name

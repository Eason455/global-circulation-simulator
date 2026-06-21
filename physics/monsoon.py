"""
东亚季风模型 — East Asian Monsoon
================================
海陆热力性质差异驱动的季风判定, 区间判断 + 连续强度.
"""

import numpy as np
from typing import Dict


def get_monsoon_state(month: float) -> Dict:
    """判断东亚季风状态.

    季节划分 (教材标准):
      夏季风:  5月 ~ 9月   (大陆低压+海洋高压 -> 东南季风)
      冬季风: 11月 ~ 次年2月 (大陆高压+海洋低压 -> 西北季风)
      过渡期:  3~4月, 10月 (季风较弱, 风向多变)

    strength 采用连续函数平滑过渡, 保持动画流畅.
    """
    m = month % 12
    if m == 0:
        m = 12
    if 5 <= m < 10:
        season = "summer"
    elif m >= 11 or m < 3:
        season = "winter"
    else:
        season = "transition"

    # 强度: 连续函数, 夏季7月峰值, 冬季1月峰值
    if season == "summer":
        strength = 1.0 - abs(m - 7.0) / 3.0
        strength = np.clip(strength, 0.3, 1.0)
    elif season == "winter":
        dist = min(abs(m - 1.0), abs(m - 13.0)) if m < 3 else abs(m - 13.0)
        strength = 1.0 - dist / 3.0
        strength = np.clip(strength, 0.3, 1.0)
    else:
        strength = 0.3

    if season == "summer":
        return {
            "season": "summer",
            "land_pressure": "low",
            "ocean_pressure": "high",
            "wind_direction": -45,
            "wind_name": "东南季风",
            "wind_name_en": "SE Monsoon",
            "strength": strength,
        }
    elif season == "winter":
        return {
            "season": "winter",
            "land_pressure": "high",
            "ocean_pressure": "low",
            "wind_direction": 135,
            "wind_name": "西北季风",
            "wind_name_en": "NW Monsoon",
            "strength": strength,
        }
    else:
        return {
            "season": "transition",
            "land_pressure": "neutral",
            "ocean_pressure": "neutral",
            "wind_direction": 0,
            "wind_name": "过渡期弱风",
            "wind_name_en": "Weak Variable",
            "strength": 0.3,
        }


def get_monsoon_season(month: float) -> str:
    """返回季风季节标签 ('summer' / 'winter' / 'transition'), 供其他模块统一调用."""
    m = month % 12
    if m == 0:
        m = 12
    if 5 <= m < 10:
        return "summer"
    elif m >= 11 or m < 3:
        return "winter"
    else:
        return "transition"

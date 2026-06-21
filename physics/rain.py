"""
雨带模型 — ITCZ Rain Belt
=========================
降水带位置随太阳直射点移动, 约 1 个月滞后.
"""

import numpy as np
from typing import Dict
from physics.solar import get_solar_declination


def get_rain_belt_position(month: float) -> Dict:
    """计算雨带位置. 跟随直射点, 约1个月滞后, 北半球夏季最北~20-25 deg N."""
    declination_lag = get_solar_declination(month - 1)
    lat_center = declination_lag * 0.9
    half_width = 8.0 if abs(lat_center) > 10 else 5.0
    intensity = np.clip(1.0 - abs(declination_lag) / 30.0, 0.3, 1.0)
    return {
        "lat_center": lat_center,
        "lat_min": lat_center - half_width,
        "lat_max": lat_center + half_width,
        "intensity": intensity,
        "declination": declination_lag,
    }

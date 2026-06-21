"""
气压带模型 — Pressure Belts
===========================
定义气压带数据结构, 计算季节偏移后的气压带位置.
"""

import numpy as np
from dataclasses import dataclass
from typing import List

# ---- 气压带类别常量 ----
KIND_POLAR_HIGH       = "polar_high"
KIND_SUBPOLAR_LOW     = "subpolar_low"
KIND_SUBTROPICAL_HIGH = "subtropical_high"
KIND_EQUATORIAL_LOW   = "equatorial_low"


@dataclass
class PressureBelt:
    """单个气压带

    Attributes:
        kind: 气压带类别标识, 用于风带分类等语义判定:
              polar_high / subpolar_low / subtropical_high / equatorial_low
    """
    name: str
    name_en: str
    base_lat: float
    is_low: bool
    color: str
    kind: str = ""


PRESSURE_BELTS_BASE = [
    PressureBelt("北极高压带",   "PHP",  90.0,  False, "#d4a574", KIND_POLAR_HIGH),
    PressureBelt("副极地低压带", "SPL",  60.0,  True,  "#74b9ff", KIND_SUBPOLAR_LOW),
    PressureBelt("副热带高压带", "STH",  30.0,  False, "#e17055", KIND_SUBTROPICAL_HIGH),
    PressureBelt("赤道低压带",   "ITCZ",  0.0,  True,  "#00b894", KIND_EQUATORIAL_LOW),
    PressureBelt("副热带高压带", "STH", -30.0,  False, "#e17055", KIND_SUBTROPICAL_HIGH),
    PressureBelt("副极地低压带", "SPL", -60.0,  True,  "#74b9ff", KIND_SUBPOLAR_LOW),
    PressureBelt("南极高压带",   "PHP", -90.0,  False, "#d4a574", KIND_POLAR_HIGH),
]


def get_pressure_belt_positions(
    declination: float, shift_amplitude: float = 10.0
) -> List[PressureBelt]:
    """根据太阳直射点纬度计算气压带实际位置.
    ITCZ 完全跟随直射点(100%), 副热带 80%, 副极地 50%, 极地 10%.
    偏移逻辑基于 kind 字段而非数值纬度.
    """
    shift_fraction = declination / 23.5
    max_shift = shift_amplitude * shift_fraction
    shifted_belts = []
    for belt in PRESSURE_BELTS_BASE:
        if belt.kind == KIND_EQUATORIAL_LOW:
            lat_shift = max_shift * 1.0
        elif belt.kind == KIND_SUBTROPICAL_HIGH:
            lat_shift = max_shift * 0.8
        elif belt.kind == KIND_SUBPOLAR_LOW:
            lat_shift = max_shift * 0.5
        elif belt.kind == KIND_POLAR_HIGH:
            lat_shift = max_shift * 0.1
        else:
            lat_shift = max_shift * 0.7
        new_lat = np.clip(belt.base_lat + lat_shift, -90, 90)
        # 防止副热带高压跨过赤道
        if belt.kind == KIND_SUBTROPICAL_HIGH and belt.base_lat > 0:
            new_lat = max(new_lat, 5)
        elif belt.kind == KIND_SUBTROPICAL_HIGH and belt.base_lat < 0:
            new_lat = min(new_lat, -5)
        shifted_belts.append(PressureBelt(
            name=belt.name, name_en=belt.name_en,
            base_lat=new_lat, is_low=belt.is_low, color=belt.color,
            kind=belt.kind))
    return shifted_belts

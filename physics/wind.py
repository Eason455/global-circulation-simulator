"""
风带模型 — Wind Belts
=====================
基于气压带类别组合推导风带分布, 输出中文风向标签.
"""

from dataclasses import dataclass
from typing import List
from physics.pressure import (
    PressureBelt,
    KIND_EQUATORIAL_LOW,
    KIND_SUBTROPICAL_HIGH,
    KIND_SUBPOLAR_LOW,
    KIND_POLAR_HIGH,
)


@dataclass
class WindBelt:
    """单个风带

    name / name_en:   风带显示名 (如 '东北信风带' / 'NE Trades')
    direction_cn:     中文风向 (如 '东北'), 用于 UI 标签
    arrow_angle:      matplotlib 箭头角度 (度)
    """
    name: str
    name_en: str
    lat_min: float
    lat_max: float
    direction_cn: str
    arrow_angle: float


def get_wind_belts(pressure_belts: List[PressureBelt]) -> List[WindBelt]:
    """根据气压带类别推导风带分布.

    风从高压吹向低压, 受科里奥利力偏转: 北半球右偏, 南半球左偏.

    分类规则 (基于气压带 kind):
      equatorial_low + subtropical_high -> 信风带
      subtropical_high + subpolar_low -> 盛行西风带
      subpolar_low + polar_high       -> 极地东风带

    风向命名: 描述的是"风从哪里来".
    """
    sorted_belts = sorted(pressure_belts, key=lambda b: b.base_lat, reverse=True)
    wind_belts = []
    for i in range(len(sorted_belts) - 1):
        upper, lower = sorted_belts[i], sorted_belts[i + 1]
        lat_mid = (upper.base_lat + lower.base_lat) / 2
        is_nh = lat_mid > 0
        kinds = {upper.kind, lower.kind}

        if kinds == {KIND_EQUATORIAL_LOW, KIND_SUBTROPICAL_HIGH}:
            name = "东北信风带" if is_nh else "东南信风带"
            name_en = "NE Trades" if is_nh else "SE Trades"
            direction_cn = "东北" if is_nh else "东南"
            arrow_angle = -135 if is_nh else -45
        elif kinds == {KIND_SUBTROPICAL_HIGH, KIND_SUBPOLAR_LOW}:
            name = "盛行西风带"
            name_en = "Westerlies"
            direction_cn = "西南" if is_nh else "西北"
            arrow_angle = 135 if is_nh else 45
        elif kinds == {KIND_SUBPOLAR_LOW, KIND_POLAR_HIGH}:
            name = "极地东风带"
            name_en = "Polar Easterlies"
            direction_cn = "东北" if is_nh else "东南"
            arrow_angle = -135 if is_nh else -45
        else:
            continue

        wind_belts.append(WindBelt(
            name=name, name_en=name_en,
            lat_min=lower.base_lat, lat_max=upper.base_lat,
            direction_cn=direction_cn, arrow_angle=arrow_angle,
        ))
    return wind_belts

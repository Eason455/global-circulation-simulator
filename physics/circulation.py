"""
三圈环流模型 — Three-Cell Circulation
===================================
Hadley / Ferrel / Polar 环流圈边界的动态计算.
"""

import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class CirculationCell:
    """单个环流圈"""
    name: str
    lat_min: float
    lat_max: float
    is_thermal_direct: bool


def get_circulation_cells(
    declination: float, shift_amplitude: float = 10.0
) -> List[CirculationCell]:
    """计算三圈环流的边界位置.
    Hadley(0~30 deg), Ferrel(30~60 deg), Polar(60~90 deg).
    边界随太阳直射点偏移.
    """
    shift = (declination / 23.5) * shift_amplitude
    cells = []
    hadley_n = np.clip(30 + shift * 0.8, 25, 35)
    ferrel_n = np.clip(60 + shift * 0.5, 55, 65)
    cells.append(CirculationCell("哈德莱环流 (NH)", 0, hadley_n, True))
    cells.append(CirculationCell("费雷尔环流 (NH)", hadley_n, ferrel_n, False))
    cells.append(CirculationCell("极地环流 (NH)", ferrel_n, 90, True))
    hadley_s = np.clip(-30 + shift * 0.8, -35, -25)
    ferrel_s = np.clip(-60 + shift * 0.5, -65, -55)
    cells.append(CirculationCell("哈德莱环流 (SH)", hadley_s, 0, True))
    cells.append(CirculationCell("费雷尔环流 (SH)", ferrel_s, hadley_s, False))
    cells.append(CirculationCell("极地环流 (SH)", -90, ferrel_s, True))
    return cells

"""
绘图辅助函数 — Plotting Helpers
==============================
纬度刻度和地球背景色等共享绘图工具.
"""

import numpy as np
from typing import Tuple, List


def get_lat_ticks() -> Tuple[np.ndarray, List[str]]:
    """获取纬度刻度标签"""
    ticks = np.arange(-90, 91, 15)
    labels = []
    for t in ticks:
        if t > 0:
            labels.append(f"{int(t)} deg N")
        elif t < 0:
            labels.append(f"{int(abs(t))} deg S")
        else:
            labels.append("0 deg")
    return ticks, labels


def add_globe_bg(ax, lat_range=(-90, 90)):
    """为纬度剖面图添加地球背景色"""
    import matplotlib.pyplot as plt
    y_min, y_max = lat_range
    for lat in np.linspace(y_min, y_max, 200):
        frac = abs(lat) / 90
        r = 1.0 - frac * 0.4
        g = 1.0 - frac * 0.6
        b = 1.0 - frac * 0.3
        ax.axhspan(lat - 0.5, lat + 0.5, color=(r, g, b), alpha=0.15, zorder=0)

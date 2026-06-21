"""
模块5: 雨带移动模拟
================
显示赤道雨带 (ITCZ 降水区) 位置随季节的移动.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from utils.physics import get_rain_belt_position, get_solar_declination, get_lat_ticks


def plot_rain_belt(
    ax: plt.Axes,
    month: float,
) -> None:
    """
    绘制全球雨带 (ITCZ 降水集中区) 纬向分布图.

    雨带跟随太阳直射点移动, 但有一定滞后 (~1 个月).
    北半球夏季雨带北移最远可达 20-25°N.
    """
    rain = get_rain_belt_position(month)
    decl = get_solar_declination(month)

    ax.clear()
    ax.set_xlim(-90, 90)
    ax.set_ylim(0, 10)
    ax.set_xlabel("纬度", fontsize=12, fontweight='bold')

    ticks, labels = get_lat_ticks()
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticks([])

    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.axvline(0, color='#636e72', linewidth=1.5, alpha=0.5)

    ax.axvspan(-30, 30, color='#ffeaa7', alpha=0.1, zorder=0)
    ax.text(0, 9.5, "热带范围", fontsize=9, ha='center', color='#636e72', alpha=0.5)

    lat_center = rain["lat_center"]
    lat_min = rain["lat_min"]
    lat_max = rain["lat_max"]
    intensity = rain["intensity"]

    for i, (alpha, y_bottom, y_top) in enumerate([
        (0.15, 0.5, 9.5),
        (0.25, 1.0, 9.0),
        (0.4, 1.5, 8.5),
        (0.6, 2.0, 8.0),
    ]):
        ax.axvspan(lat_min, lat_max,
                   ymin=y_bottom / 10, ymax=y_top / 10,
                   facecolor='#0984e3', alpha=alpha * intensity,
                   zorder=3)

    core_half = (lat_max - lat_min) * 0.3
    if core_half > 1.5:
        ax.axvspan(lat_center - core_half, lat_center + core_half,
                   ymin=0.25, ymax=0.75,
                   facecolor='#074b8a', alpha=0.5 * intensity,
                   zorder=4)

    for lat, style in [(lat_min, '--'), (lat_max, '--')]:
        ax.axvline(lat, color='#0984e3', linewidth=1.5,
                   linestyle=style, alpha=0.7, zorder=5)

    ax.axvline(decl, color='#d63031', linewidth=1.5,
               linestyle=':', alpha=0.8, zorder=5)

    lat_center_str = f"{abs(lat_center):.1f}°{'N' if lat_center >= 0 else 'S'}"
    ax.text(
        lat_center, 8.7,
        f"雨带中心\n{lat_center_str}",
        fontsize=10, ha='center', va='bottom',
        fontweight='bold', color='#074b8a',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor='#0984e3', alpha=0.9),
        zorder=6,
    )

    decl_str = f"{abs(decl):.1f}°{'N' if decl >= 0 else 'S'}"
    ax.text(
        decl, 3.0,
        f"直射点\n{decl_str}",
        fontsize=8, ha='center', va='bottom',
        color='#d63031', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffeaa7',
                  edgecolor='#d63031', alpha=0.85),
        zorder=6,
    )

    if month in [6, 7, 8]:
        note = "北半球夏季: 雨带北移"
        note_color = '#d63031'
    elif month in [12, 1, 2]:
        note = "北半球冬季: 雨带南移"
        note_color = '#0984e3'
    elif month in [3, 4, 5]:
        note = "春季: 雨带逐渐北移"
        note_color = '#00b894'
    else:
        note = "秋季: 雨带逐渐南移"
        note_color = '#e17055'

    ax.text(0.5, 0.95, note, transform=ax.transAxes,
            fontsize=11, ha='center', fontweight='bold', color=note_color,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title("全球降水带 (ITCZ) 季节移动", fontsize=14,
                 fontweight='bold', color='#2d3436')

"""
模块4: 东亚季风形成模拟
====================
绘制亚洲大陆-太平洋简化地图,
展示夏季 (东南季风) 和冬季 (西北季风) 模式.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
from matplotlib.patches import Polygon, Ellipse

from utils.physics import get_monsoon_state


def plot_east_asian_monsoon(
    ax: plt.Axes,
    month: float,
) -> None:
    """
    绘制东亚季风形成示意图.

    简化地图:
      - 左侧: 亚洲大陆 (矩形)
      - 右侧: 太平洋 (矩形)
      - 中国东南沿海位于交界处

    夏季: 大陆低压 (L) + 海洋高压 (H) → 东南风 (海洋→大陆)
    冬季: 大陆高压 (H) + 海洋低压 (L) → 西北风 (大陆→海洋)
    """
    monsoon = get_monsoon_state(month)

    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    # === 地理背景 ===
    continent = Polygon(
        [(0, 0), (4.5, 0), (4.5, 10), (0, 10)],
        facecolor='#dfe6e9', edgecolor='#636e72',
        linewidth=2, zorder=2
    )
    ax.add_patch(continent)

    plateau = Polygon(
        [(1.5, 4), (3.5, 4), (3.5, 7), (1.5, 6)],
        facecolor='#b2bec3', edgecolor='#636e72',
        linewidth=1, alpha=0.7, zorder=3
    )
    ax.add_patch(plateau)
    ax.text(2.5, 5.5, "青藏\n高原", fontsize=8, ha='center', va='center',
            fontweight='bold', color='#2d3436', zorder=4)

    ocean = Polygon(
        [(5.5, 0), (10, 0), (10, 10), (5.5, 10)],
        facecolor='#74b9ff', edgecolor='#0984e3',
        linewidth=2, alpha=0.6, zorder=2
    )
    ax.add_patch(ocean)

    coast = Polygon(
        [(4.2, 2), (5.8, 2), (5.8, 5.5), (4.2, 5)],
        facecolor='#81ecec', edgecolor='#00b894',
        linewidth=1.5, alpha=0.5, zorder=3
    )
    ax.add_patch(coast)
    ax.text(5, 3.5, "东南\n沿海", fontsize=7, ha='center', va='center',
            fontweight='bold', color='#2d3436')

    ax.text(2.25, 9.2, "亚洲大陆", fontsize=13, ha='center',
            fontweight='bold', color='#2d3436')
    ax.text(7.75, 9.2, "太平洋", fontsize=13, ha='center',
            fontweight='bold', color='#0984e3')

    # === 气压系统 ===
    if monsoon["land_pressure"] == "low":
        land_color = '#d63031'
        land_label = "亚洲低压\n(热低压)"
        ocean_color = '#0984e3'
        ocean_label = "太平洋高压\n(副热带高压)"
    elif monsoon["land_pressure"] == "high":
        land_color = '#0984e3'
        land_label = "亚洲高压\n(冷高压)"
        ocean_color = '#d63031'
        ocean_label = "太平洋低压\n(阿留申低压)"
    else:
        land_color = '#636e72'
        land_label = "过渡期"
        ocean_color = '#636e72'
        ocean_label = "过渡期"

    land_center = (2.5, 7.0)
    _draw_pressure_center(ax, land_center[0], land_center[1],
                          land_color, "L" if monsoon["land_pressure"] == "low"
                          else "H" if monsoon["land_pressure"] == "high" else "~")
    ax.text(land_center[0], land_center[1] - 1.0, land_label,
            fontsize=9, ha='center', fontweight='bold', color=land_color)

    ocean_center = (8.0, 7.0)
    _draw_pressure_center(ax, ocean_center[0], ocean_center[1],
                          ocean_color, "H" if monsoon["ocean_pressure"] == "high"
                          else "L" if monsoon["ocean_pressure"] == "low" else "~")
    ax.text(ocean_center[0], ocean_center[1] - 1.0, ocean_label,
            fontsize=9, ha='center', fontweight='bold', color=ocean_color)

    # === 季风箭头 ===
    if monsoon["season"] != "transition":
        _draw_monsoon_arrows(ax, monsoon, land_center, ocean_center)

    # === 温度对比提示 ===
    if monsoon["season"] == "summer":
        ax.text(2.25, 0.8, "大陆升温快\n(热低压形成)", fontsize=9,
                ha='center', color='#d63031', fontweight='bold')
        ax.text(7.75, 0.8, "海洋升温慢\n(相对高压)", fontsize=9,
                ha='center', color='#0984e3', fontweight='bold')
    elif monsoon["season"] == "winter":
        ax.text(2.25, 0.8, "大陆降温快\n(冷高压形成)", fontsize=9,
                ha='center', color='#0984e3', fontweight='bold')
        ax.text(7.75, 0.8, "海洋降温慢\n(相对低压)", fontsize=9,
                ha='center', color='#d63031', fontweight='bold')

    if monsoon["season"] == "summer":
        title = f"东亚夏季风 — {monsoon['wind_name']} (海洋 → 大陆)"
    elif monsoon["season"] == "winter":
        title = f"东亚冬季风 — {monsoon['wind_name']} (大陆 → 海洋)"
    else:
        title = "东亚季风过渡期"

    ax.set_title(title, fontsize=14, fontweight='bold', color='#2d3436',
                 pad=10)


def _draw_pressure_center(ax, x, y, color, label, size=1.2):
    """绘制气压中心标记"""
    circle = Circle((x, y), size, facecolor=color, edgecolor='white',
                    linewidth=2, alpha=0.7, zorder=5)
    ax.add_patch(circle)
    ax.text(x, y, label, fontsize=14, ha='center', va='center',
            fontweight='bold', color='white', zorder=6)


def _draw_monsoon_arrows(ax, monsoon, land_center, ocean_center):
    """绘制季风方向箭头"""
    wind_dir = monsoon["wind_direction"]
    strength = monsoon["strength"]

    if wind_dir == -45:
        arrow_starts = [
            (7.0, 4.0), (7.5, 5.0), (8.0, 6.0),
            (6.5, 3.0), (7.0, 2.5),
        ]
        dx, dy = -2.2, -2.2
    elif wind_dir == 135:
        arrow_starts = [
            (3.0, 4.0), (2.5, 5.0), (2.0, 6.0),
            (3.5, 3.0), (3.0, 2.5),
        ]
        dx, dy = 2.2, 2.2
    else:
        return

    for i, (sx, sy) in enumerate(arrow_starts):
        alpha = 0.3 + strength * 0.6
        width = 0.06 + strength * 0.08
        ax.arrow(sx, sy, dx, dy,
                head_width=0.4 + strength * 0.2,
                head_length=0.3 + strength * 0.15,
                fc='#2d3436', ec='#636e72',
                alpha=alpha, width=width,
                length_includes_head=True,
                zorder=5)

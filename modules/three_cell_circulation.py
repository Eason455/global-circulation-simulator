"""
模块3: 三圈环流可视化
==================
显示哈德莱环流、费雷尔环流、极地环流,
采用流线动画, 红色表示上升, 蓝色表示下沉.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Arc, FancyBboxPatch
from typing import List

from utils.physics import (
    get_solar_declination,
    get_circulation_cells,
    CirculationCell,
    get_lat_ticks,
)


def plot_three_cell_circulation(
    ax: plt.Axes,
    month: float,
    shift_amplitude: float = 10.0,
) -> None:
    """
    绘制三圈环流示意图.

    采用纬度-高度剖面图:
      - 垂直轴: 高度 (对流层)
      - 水平轴: 纬度 (-90° ~ 90°)
      - 流线表示空气运动路径
      - 红色区 = 上升气流, 蓝色区 = 下沉气流
    """
    decl = get_solar_declination(month)
    cells = get_circulation_cells(decl, shift_amplitude)

    ax.clear()
    ax.set_xlim(-90, 90)
    ax.set_ylim(0, 12)
    ax.set_xlabel("纬度", fontsize=12, fontweight='bold')
    ax.set_ylabel("高度 (对流层)", fontsize=11, fontweight='bold')

    ticks, labels = get_lat_ticks()
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticks([0, 3, 6, 9, 12])
    ax.set_yticklabels(["地面", "3km", "6km", "9km", "12km"], fontsize=8)

    ax.grid(alpha=0.2, linestyle='--')
    ax.axvline(0, color='#636e72', linewidth=1.5, alpha=0.5)
    ax.axhline(0, color='#2d3436', linewidth=2, alpha=0.8)

    ax.fill_between([-90, 90], 0, 0.3, color='#b2bec3', alpha=0.5, zorder=1)
    ax.axhline(12, color='#636e72', linewidth=1, linestyle=':', alpha=0.6)
    ax.text(-88, 12.3, "对流层顶 (~12km)", fontsize=7, color='#636e72', alpha=0.7)

    for cell in cells:
        lat_min = cell.lat_min
        lat_max = cell.lat_max
        lat_mid = (lat_min + lat_max) / 2

        is_nh = lat_mid > 0
        bg_color = '#ff7675' if cell.is_thermal_direct else '#74b9ff'
        ax.fill_between(
            [lat_min, lat_max],
            0, 12,
            color=bg_color, alpha=0.06, zorder=1
        )

        if cell.is_thermal_direct:
            if is_nh:
                rise_lat = lat_min + 2
                sink_lat = lat_max - 2
            else:
                rise_lat = lat_max - 2
                sink_lat = lat_min + 2
        else:
            if is_nh:
                rise_lat = lat_max - 2
                sink_lat = lat_min + 2
            else:
                rise_lat = lat_min + 2
                sink_lat = lat_max - 2

        _draw_vertical_flow(ax, rise_lat, 0.3, 10, 'up', '#d63031', 2.5)
        _draw_vertical_flow(ax, sink_lat, 0.3, 10, 'down', '#0984e3', 2.5)

        upper_dir = 'right' if ((is_nh and cell.is_thermal_direct) or
                                 (not is_nh and not cell.is_thermal_direct)) else 'left'
        _draw_horizontal_flow(ax, rise_lat, sink_lat, 9.5, upper_dir,
                             '#636e72', 1.5)

        surface_dir = 'left' if upper_dir == 'right' else 'right'
        _draw_horizontal_flow(ax, rise_lat, sink_lat, 2.0, surface_dir,
                             '#2d3436', 1.5)

        ax.text(
            lat_mid, 6,
            cell.name.replace(" (NH)", "").replace(" (SH)", ""),
            fontsize=10, ha='center', va='center',
            fontweight='bold', color='#2d3436',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='#636e72', alpha=0.85),
            zorder=6,
        )

    ax.text(0.02, 0.98, "↑ 红色箭头 = 上升气流 (低压区)\n↓ 蓝色箭头 = 下沉气流 (高压区)",
            transform=ax.transAxes, fontsize=8,
            va='top', ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title("三圈环流示意图", fontsize=14, fontweight='bold',
                 color='#2d3436')


def _draw_vertical_flow(ax, lat, y_bottom, y_top, direction, color, width):
    """绘制垂直气流箭头"""
    n_arrows = 4
    y_positions = np.linspace(y_bottom + 0.5, y_top - 0.5, n_arrows)
    for yp in y_positions:
        if direction == 'up':
            dy = 1.2
        else:
            dy = -1.2
        ax.arrow(lat, yp - dy / 2, 0, dy,
                head_width=1.5, head_length=0.8,
                fc=color, ec=color, alpha=0.8,
                width=0.3, length_includes_head=True,
                zorder=5)


def _draw_horizontal_flow(ax, lat_start, lat_end, height, direction, color, width):
    """绘制水平气流箭头"""
    if direction == 'right':
        lat_from = min(lat_start, lat_end)
        lat_to = max(lat_start, lat_end)
    else:
        lat_from = max(lat_start, lat_end)
        lat_to = min(lat_start, lat_end)

    span = lat_to - lat_from
    n_arrows = max(2, int(abs(span) / 8))
    lat_positions = np.linspace(lat_from + 2, lat_to - 2, n_arrows)

    for lp in lat_positions:
        if direction == 'right':
            dx = 2.0
        else:
            dx = -2.0
        ax.arrow(lp - dx / 2, height, dx, 0,
                head_width=0.6, head_length=1.5,
                fc=color, ec=color, alpha=0.7,
                width=0.15, length_includes_head=True,
                zorder=4)

"""
模块2: 全球气压带与风带动态模拟
===========================
绘制全球纬度剖面图, 显示气压带和风带,
随太阳直射点移动同步偏移.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from typing import List

from utils.physics import (
    get_solar_declination,
    get_pressure_belt_positions,
    get_wind_belts,
    PressureBelt,
    WindBelt,
    get_lat_ticks,
)


def plot_pressure_wind_belts(
    ax: plt.Axes,
    month: float,
    shift_amplitude: float = 10.0,
    show_pressure: bool = True,
    show_wind: bool = True,
) -> None:
    """
    绘制全球气压带和风带纬度剖面图.

    Args:
        ax: matplotlib Axes
        month: 当前月份
        shift_amplitude: 偏移幅度 (5/10/15)
        show_pressure: 是否显示气压带
        show_wind: 是否显示风带
    """
    decl = get_solar_declination(month)
    pressure_belts = get_pressure_belt_positions(decl, shift_amplitude)
    wind_belts = get_wind_belts(pressure_belts)

    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(-90, 90)
    ax.set_ylabel("纬度", fontsize=12, fontweight='bold')
    ax.set_xlabel("")

    ticks, labels = get_lat_ticks()
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xticks([])

    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.axhline(0, color='#636e72', linewidth=1.5, alpha=0.5)

    if show_pressure:
        _draw_pressure_belts(ax, pressure_belts)

    if show_wind:
        _draw_wind_belts(ax, wind_belts)

    legend_elements = []
    if show_pressure:
        from matplotlib.patches import Patch
        legend_elements.extend([
            Patch(facecolor='#00b894', alpha=0.4, label='低压带 (上升气流)'),
            Patch(facecolor='#e17055', alpha=0.4, label='高压带 (下沉气流)'),
        ])
    if show_wind:
        from matplotlib.lines import Line2D
        legend_elements.append(
            Line2D([0], [0], color='#0984e3', linewidth=2,
                   label='风带方向')
        )

    if legend_elements:
        ax.legend(handles=legend_elements, loc='lower right',
                  fontsize=8, framealpha=0.9)

    shift_str = f"移动幅度: ±{shift_amplitude}°"
    ax.set_title(
        f"全球气压带与风带分布  ({shift_str})",
        fontsize=14, fontweight='bold', color='#2d3436'
    )


def _draw_pressure_belts(ax: plt.Axes, belts: List[PressureBelt]) -> None:
    """绘制气压带色块"""
    sorted_belts = sorted(belts, key=lambda b: b.base_lat, reverse=True)

    for belt in sorted_belts:
        half_width = 3 if belt.is_low else 5

        lat_bottom = max(-90, belt.base_lat - half_width)
        lat_top = min(90, belt.base_lat + half_width)

        alpha = 0.35
        ax.fill_betweenx(
            [lat_bottom, lat_top],
            0, 10,
            color=belt.color,
            alpha=alpha,
            zorder=2,
        )

        for lat in [lat_bottom, lat_top]:
            ax.axhline(lat, color=belt.color, linewidth=1,
                       alpha=0.6, linestyle='-', zorder=3)

        mid = (lat_bottom + lat_top) / 2
        pressure_type = "低压 (L)" if belt.is_low else "高压 (H)"
        ax.text(
            5, mid,
            f"{belt.name}\n{pressure_type}\n{belt.base_lat:.0f}°",
            fontsize=8,
            ha='center', va='center',
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor=belt.color, alpha=0.85),
            zorder=5,
        )


def _draw_wind_belts(ax: plt.Axes, wind_belts: List[WindBelt]) -> None:
    """绘制风带箭头"""
    for wb in wind_belts:
        lat_mid = (wb.lat_min + wb.lat_max) / 2
        lat_span = wb.lat_max - wb.lat_min

        ax.axhspan(
            wb.lat_min, wb.lat_max,
            color='#74b9ff', alpha=0.08, zorder=1
        )

        n_arrows = max(3, int(lat_span / 3))
        arrow_lats = np.linspace(wb.lat_min + 2, wb.lat_max - 2, n_arrows)

        angle_rad = np.radians(wb.arrow_angle)
        dx = np.cos(angle_rad) * 1.8
        dy = np.sin(angle_rad) * 1.2

        for lat_a in arrow_lats:
            x_start = 2.0 + (lat_a - wb.lat_min) / lat_span * 2.0
            ax.arrow(
                x_start - dx / 2, lat_a,
                dx, dy,
                head_width=0.8, head_length=0.6,
                fc='#0984e3', ec='#074b8a',
                alpha=0.7, width=0.15,
                zorder=4,
                length_includes_head=True,
            )

        ax.text(
            8, lat_mid,
            f"{wb.name}\n({wb.direction}风)",
            fontsize=9, ha='center', va='center',
            fontweight='bold', color='#074b8a',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#dfe6e9',
                      edgecolor='#74b9ff', alpha=0.85),
            zorder=5,
        )

    for wb in wind_belts:
        for lat in [wb.lat_min, wb.lat_max]:
            if abs(lat) < 85:
                ax.plot([0, 0.5], [lat, lat], color='#636e72',
                        linewidth=0.8, alpha=0.5, zorder=3)

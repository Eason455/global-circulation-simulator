"""
模块6: 全球气候带联动显示
======================
显示主要气候类型分布, 当风带与雨带移动时同步高亮受影响区域.
点击气候带显示详细信息.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from typing import List, Optional

from utils.physics import (
    get_solar_declination,
    get_climate_zones,
    ClimateZone,
    get_lat_ticks,
)


def plot_climate_zones(
    ax: plt.Axes,
    month: float,
    shift_amplitude: float = 10.0,
    highlight_zone: Optional[str] = None,
) -> None:
    """
    绘制全球气候带联动分布图.
    """
    decl = get_solar_declination(month)
    zones = get_climate_zones(decl, shift_amplitude)

    ax.clear()
    ax.set_xlim(0, 12)
    ax.set_ylim(-90, 90)
    ax.set_ylabel("纬度", fontsize=12, fontweight='bold')

    ticks, labels = get_lat_ticks()
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xticks([])

    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.axhline(0, color='#636e72', linewidth=1.5, alpha=0.5)

    for zone in zones:
        lat_min = max(-90, zone.lat_range[0])
        lat_max = min(90, zone.lat_range[1])

        is_highlighted = (highlight_zone is not None and
                         highlight_zone == zone.name)

        alpha = 0.5 if is_highlighted else 0.25
        edge_width = 2 if is_highlighted else 0.5

        ax.fill_betweenx(
            [lat_min, lat_max],
            0, 12,
            color=zone.color,
            alpha=alpha,
            edgecolor='#2d3436' if is_highlighted else zone.color,
            linewidth=edge_width,
            zorder=3 if is_highlighted else 1,
        )

        mid = (lat_min + lat_max) / 2
        font_weight = 'bold' if is_highlighted else 'normal'
        font_size = 9 if is_highlighted else 7.5

        ax.text(
            6, mid,
            f"{zone.name}\n{zone.name_en}",
            fontsize=font_size,
            ha='center', va='center',
            fontweight=font_weight,
            color='#2d3436',
            bbox=dict(boxstyle='round,pad=0.2',
                      facecolor='white',
                      edgecolor=zone.color,
                      alpha=0.9 if is_highlighted else 0.7),
            zorder=5,
        )

    from utils.physics import get_pressure_belt_positions
    pressure_belts = get_pressure_belt_positions(decl, shift_amplitude)
    for belt in pressure_belts:
        marker = "L" if belt.is_low else "H"
        color = '#00b894' if belt.is_low else '#e17055'
        ax.plot(11.5, belt.base_lat, marker='o', color=color,
                markersize=5, alpha=0.6, zorder=4)
        ax.text(11.8, belt.base_lat, f"{marker}",
                fontsize=6, ha='left', va='center',
                color=color, alpha=0.6)

    ax.text(0.02, 0.98, "右侧小圆: L=低压 H=高压",
            transform=ax.transAxes, fontsize=7,
            va='top', color='#636e72')

    ax.set_title("全球气候带分布与气压带联动", fontsize=14,
                 fontweight='bold', color='#2d3436')


def get_climate_zone_detail(zone_name: str) -> Optional[ClimateZone]:
    """根据气候带名称获取详细信息."""
    from utils.physics import CLIMATE_ZONES_BASE
    for zone in CLIMATE_ZONES_BASE:
        if zone.name == zone_name:
            return zone
    return None


def render_climate_detail(zone: ClimateZone) -> str:
    """将气候带详细信息渲染为 HTML 字符串."""
    return f"""
    <div style="
        background: linear-gradient(135deg, {zone.color}22, {zone.color}44);
        border-left: 4px solid {zone.color};
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    ">
        <h4 style="color: {zone.color}; margin-top: 0;">
            {zone.name} ({zone.name_en})
        </h4>
        <p><b>形成原因:</b> {zone.formation}</p>
        <p><b>典型分布地区:</b> {zone.typical_areas}</p>
        <p><b>降水特点:</b> {zone.precipitation}</p>
        <p><b>气温特点:</b> {zone.temperature}</p>
    </div>
    """

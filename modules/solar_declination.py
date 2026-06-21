"""
模块1: 太阳直射点周年运动
======================
在地球示意图上动态显示太阳直射点位置,
支持拖动时间轴实时控制月份.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.patches import FancyArrow
from utils.physics import get_solar_declination, get_month_name


def plot_solar_declination(ax: plt.Axes, month: float) -> None:
    """
    在地球剖面图上绘制太阳直射点位置.

    采用地球剖面图 (圆形), 标注:
      - 赤道 (0°)
      - 回归线 (23.5°N, 23.5°S)
      - 太阳直射点 (黄色圆点)
      - 太阳光线箭头

    Args:
        ax: matplotlib Axes
        month: 当前月份 (1.0~12.0)
    """
    decl = get_solar_declination(month)

    ax.clear()
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect('equal')
    ax.axis('off')

    # 绘制地球圆
    earth = Circle((0, 0), 1.0, facecolor='#dfe6e9', edgecolor='#636e72',
                   linewidth=2, zorder=2)
    ax.add_patch(earth)

    # 赤道线
    ax.axhline(0, color='#e17055', linewidth=1.5, linestyle='--',
               alpha=0.7, zorder=3)
    ax.text(1.08, 0.05, "赤道 (0°)", fontsize=9, color='#e17055',
            va='bottom', fontweight='bold')

    # 回归线
    tropic_n = np.sin(np.radians(23.5))
    tropic_s = -tropic_n

    for lat, label, y in [(23.5, "北回归线\n23.5°N", tropic_n),
                            (-23.5, "南回归线\n23.5°S", tropic_s)]:
        radius_at_lat = np.cos(np.radians(lat))
        theta = np.linspace(0, 2 * np.pi, 100)
        x_line = radius_at_lat * np.cos(theta)
        y_line = np.full_like(theta, y)
        ax.plot(x_line, y_line, color='#0984e3', linewidth=1,
                linestyle=':', alpha=0.6, zorder=3)
        ax.text(1.08, y, label, fontsize=8, color='#0984e3',
                va='center', linespacing=1.2)

    # 太阳直射点
    sun_lat_rad = np.radians(decl)
    sun_y = np.sin(sun_lat_rad)
    sun_x = 0

    for radius, alpha in [(0.12, 0.3), (0.08, 0.6), (0.04, 1.0)]:
        sun_dot = Circle((sun_x, sun_y), radius,
                         facecolor='#fdcb6e', edgecolor='#e17055',
                         linewidth=1.5, alpha=alpha, zorder=5)
        ax.add_patch(sun_dot)

    # 太阳光线
    sun_ray_x = 1.5
    arrow = FancyArrow(sun_ray_x, sun_y + 0.3, -0.4, -0.3,
                       width=0.03, head_width=0.12, head_length=0.1,
                       facecolor='#fdcb6e', edgecolor='#e17055',
                       alpha=0.8, zorder=4)
    ax.add_patch(arrow)
    arrow2 = FancyArrow(sun_ray_x + 0.1, sun_y, -0.5, 0,
                        width=0.03, head_width=0.12, head_length=0.1,
                        facecolor='#fdcb6e', edgecolor='#e17055',
                        alpha=0.8, zorder=4)
    ax.add_patch(arrow2)
    arrow3 = FancyArrow(sun_ray_x, sun_y - 0.3, -0.4, 0.3,
                        width=0.03, head_width=0.12, head_length=0.1,
                        facecolor='#fdcb6e', edgecolor='#e17055',
                        alpha=0.8, zorder=4)
    ax.add_patch(arrow3)

    # 标注
    decl_str = f"{abs(decl):.1f}°{'N' if decl >= 0 else 'S'}"
    ax.annotate(
        f"太阳直射点\n{decl_str}",
        xy=(sun_x, sun_y),
        xytext=(0.7, sun_y + 0.6),
        fontsize=10,
        fontweight='bold',
        color='#d63031',
        arrowprops=dict(arrowstyle='->', color='#636e72', lw=1.2),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffeaa7',
                  edgecolor='#e17055', alpha=0.9),
        zorder=6,
    )

    month_name = get_month_name(month)
    ax.text(0, -1.2, f"{month_name} | 直射纬度: {decl_str}",
            fontsize=13, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#2d3436',
                      edgecolor='#636e72', alpha=0.9),
            color='white')

    ax.set_title("太阳直射点周年运动", fontsize=14, fontweight='bold',
                 color='#2d3436', pad=5)

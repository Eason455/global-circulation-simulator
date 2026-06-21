"""
全球大气环流物理模型 — 共享计算函数
===============================
本模块提供所有可视化模块共用的物理计算:
- 太阳直射点纬度 (太阳赤纬)
- 气压带位置 (随太阳直射点移动偏移)
- 风带方向
- 三圈环流边界
- 季风判定
- 雨带/ITCZ 位置
- 气候带分布
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


# ============================================================
# 1. 太阳直射点 (Solar Declination)
# ============================================================

def get_solar_declination(month: float) -> float:
    """
    计算太阳直射点纬度 (太阳赤纬角).
    使用正弦函数模拟全年连续移动.

    关键节点:
      - 春分 (3月):  0°
      - 夏至 (6月): +23.5°N
      - 秋分 (9月):  0°
      - 冬至 (12月): -23.5°S

    公式: δ = 23.5° × sin(2π × (month - 3) / 12)

    Args:
        month: 月份 (1.0 ~ 12.0, 支持小数表示月中某日)

    Returns:
        太阳直射纬度 (度), 正值表示北半球
    """
    return 23.5 * np.sin(2 * np.pi * (month - 3) / 12)


def get_season_name(month: float) -> str:
    """根据月份返回北半球季节名称"""
    m = month % 12
    if 3 <= m < 6:
        return "春季"
    elif 6 <= m < 9:
        return "夏季"
    elif 9 <= m < 12:
        return "秋季"
    else:
        return "冬季"


def get_month_name(month: float) -> str:
    """将月份数字转为中文名称, 支持小数 (如 6.5 → '6月中旬')"""
    m_int = int(np.floor(month))
    frac = month - m_int
    m_int = ((m_int - 1) % 12) + 1  # 归一化到 1~12
    name = f"{m_int}月"
    if frac < 0.33:
        name += "上旬"
    elif frac < 0.67:
        name += "中旬"
    else:
        name += "下旬"
    return name


# ============================================================
# 2. 气压带模型
# ============================================================

@dataclass
class PressureBelt:
    """单个气压带"""
    name: str           # 中文名称
    name_en: str        # 英文缩写
    base_lat: float     # 基准纬度
    is_low: bool        # True=低压, False=高压
    color: str          # 显示颜色


# 基准气压带定义 (不考虑季节移动时的位置)
PRESSURE_BELTS_BASE = [
    PressureBelt("北极高压带",   "PHP",  90.0,  False, "#d4a574"),  # 暖棕色
    PressureBelt("副极地低压带", "SPL",  60.0,  True,  "#74b9ff"),  # 蓝色
    PressureBelt("副热带高压带", "STH",  30.0,  False, "#e17055"),  # 橙红
    PressureBelt("赤道低压带",   "ITCZ",  0.0,  True,  "#00b894"),  # 绿色
    PressureBelt("副热带高压带", "STH", -30.0,  False, "#e17055"),
    PressureBelt("副极地低压带", "SPL", -60.0,  True,  "#74b9ff"),
    PressureBelt("南极高压带",   "PHP", -90.0,  False, "#d4a574"),
]


def get_pressure_belt_positions(
    declination: float,
    shift_amplitude: float = 10.0
) -> List[PressureBelt]:
    """
    根据太阳直射点纬度计算气压带实际位置.

    气压带随太阳直射点发生南北偏移, 但偏移幅度小于太阳直射点移动幅度.
    ITCZ 偏移最明显, 极地偏移较小.

    Args:
        declination: 太阳直射纬度 (度)
        shift_amplitude: 最大偏移幅度 (度), 可选 5, 10, 15

    Returns:
        偏移后的气压带列表
    """
    shift_fraction = declination / 23.5  # 归一化到 [-1, 1]
    max_shift = shift_amplitude * shift_fraction

    shifted_belts = []
    for belt in PRESSURE_BELTS_BASE:
        # 不同气压带对太阳直射点移动的响应不同
        if belt.base_lat == 0:
            # ITCZ 完全跟随直射点
            lat_shift = max_shift * 1.0
        elif abs(belt.base_lat) == 30:
            # 副热带高压带偏移约 80%
            lat_shift = max_shift * 0.8
        elif abs(belt.base_lat) == 60:
            # 副极地低压带偏移约 50%
            lat_shift = max_shift * 0.5
        elif abs(belt.base_lat) == 90:
            # 极地高压基本不偏移
            lat_shift = max_shift * 0.1
        else:
            lat_shift = max_shift * 0.7

        # 确保气压带不越界
        new_lat = np.clip(belt.base_lat + lat_shift, -90, 90)
        # 保持对称性处理正负纬度
        if belt.base_lat > 0:
            new_lat = max(new_lat, 5) if belt.base_lat == 30 else new_lat
        elif belt.base_lat < 0:
            new_lat = min(new_lat, -5) if belt.base_lat == -30 else new_lat

        shifted_belts.append(PressureBelt(
            name=belt.name,
            name_en=belt.name_en,
            base_lat=new_lat,
            is_low=belt.is_low,
            color=belt.color,
        ))

    return shifted_belts


# ============================================================
# 3. 风带模型
# ============================================================

@dataclass
class WindBelt:
    """单个风带"""
    name: str           # 中文名称
    name_en: str        # 英文缩写
    lat_min: float      # 南界纬度
    lat_max: float      # 北界纬度
    direction: str      # 风向描述 (NE, SE, SW, NW)
    arrow_angle: float  # 箭头指向角度 (度, 0=东, 90=北, -90=南)


def get_wind_belts(pressure_belts: List[PressureBelt]) -> List[WindBelt]:
    """
    根据气压带位置推导风带分布.

    风带位于相邻气压带之间, 风向受气压梯度力和科里奥利力共同作用:
      - 北半球右偏: 东北信风, 西南西风
      - 南半球左偏: 东南信风, 西北西风

    Args:
        pressure_belts: 偏移后的气压带列表

    Returns:
        风带列表
    """
    # 按纬度排序 (从北到南)
    sorted_belts = sorted(pressure_belts, key=lambda b: b.base_lat, reverse=True)

    wind_belts = []
    for i in range(len(sorted_belts) - 1):
        upper = sorted_belts[i]      # 北侧气压带
        lower = sorted_belts[i + 1]  # 南侧气压带

        lat_mid = (upper.base_lat + lower.base_lat) / 2

        # 确定气压梯度方向: 风从高压吹向低压, 受科里奥利力偏转
        if upper.is_low and not lower.is_low:
            # 北低压, 南高压 → 风从南来, 向北吹
            # 北半球右偏 → 西南风; 南半球左偏 → 西北风
            if lat_mid > 0:  # 北半球
                direction = "SW"
                arrow_angle = 135  # 指向东北 (从西南来)
            else:  # 南半球
                direction = "NW"
                arrow_angle = 45   # 指向东南 (从西北来)
        elif not upper.is_low and lower.is_low:
            # 北高压, 南低压 → 风从北来, 向南吹
            if lat_mid > 0:
                direction = "NE"
                arrow_angle = -135  # 指向西南 (从东北来)
            else:
                direction = "SE"
                arrow_angle = -45   # 指向西北 (从东南来)
        elif upper.is_low and lower.is_low:
            # 两个低压之间 → 弱风, 忽略
            continue
        else:
            # 两个高压之间 → 弱风, 忽略
            continue

        # 命名风带
        if abs(upper.base_lat) == 90 or abs(lower.base_lat) == 90:
            if lat_mid > 0:
                name = "极地东风带"
                name_en = "Polar Easterlies"
            else:
                name = "极地东风带"
                name_en = "Polar Easterlies"
        elif abs(upper.base_lat) < 35 and abs(lower.base_lat) < 35:
            if lat_mid > 0:
                name = "东北信风带"
                name_en = "NE Trades"
            else:
                name = "东南信风带"
                name_en = "SE Trades"
        else:
            if lat_mid > 0:
                name = "盛行西风带"
                name_en = "Westerlies"
            else:
                name = "盛行西风带"
                name_en = "Westerlies"

        wind_belts.append(WindBelt(
            name=name,
            name_en=name_en,
            lat_min=lower.base_lat,
            lat_max=upper.base_lat,
            direction=direction,
            arrow_angle=arrow_angle,
        ))

    return wind_belts


# ============================================================
# 4. 三圈环流模型
# ============================================================

@dataclass
class CirculationCell:
    """单个环流圈"""
    name: str
    lat_min: float
    lat_max: float
    is_thermal_direct: bool  # True=直接热力环流, False=间接环流


def get_circulation_cells(
    declination: float,
    shift_amplitude: float = 10.0
) -> List[CirculationCell]:
    """
    计算三圈环流的边界位置.

    - 哈德莱环流 (Hadley): 赤道 ~ 30° (热力直接环流, 低纬)
    - 费雷尔环流 (Ferrel): 30° ~ 60° (间接环流, 中纬)
    - 极地环流 (Polar): 60° ~ 90° (热力直接环流, 高纬)

    Args:
        declination: 太阳直射纬度
        shift_amplitude: 偏移幅度

    Returns:
        环流圈列表
    """
    shift = (declination / 23.5) * shift_amplitude

    cells = []

    # 北半球
    hadley_n_lat = np.clip(30 + shift * 0.8, 25, 35)
    ferrel_n_lat = np.clip(60 + shift * 0.5, 55, 65)

    cells.append(CirculationCell("哈德莱环流 (NH)", 0, hadley_n_lat, True))
    cells.append(CirculationCell("费雷尔环流 (NH)", hadley_n_lat, ferrel_n_lat, False))
    cells.append(CirculationCell("极地环流 (NH)", ferrel_n_lat, 90, True))

    # 南半球
    hadley_s_lat = np.clip(-30 + shift * 0.8, -35, -25)
    ferrel_s_lat = np.clip(-60 + shift * 0.5, -65, -55)

    cells.append(CirculationCell("哈德莱环流 (SH)", hadley_s_lat, 0, True))
    cells.append(CirculationCell("费雷尔环流 (SH)", ferrel_s_lat, hadley_s_lat, False))
    cells.append(CirculationCell("极地环流 (SH)", -90, ferrel_s_lat, True))

    return cells


# ============================================================
# 5. 东亚季风模型
# ============================================================

def get_monsoon_state(month: float) -> Dict:
    """
    判断东亚季风状态.

    夏季 (6-8月): 大陆低压 + 海洋高压 → 东南季风 (海洋→大陆)
    冬季 (12-2月): 大陆高压 + 海洋低压 → 西北季风 (大陆→海洋)
    春秋过渡: 逐渐切换

    Args:
        month: 月份 (1-12)

    Returns:
        季风状态字典, 包含:
        - season: 'summer' | 'winter' | 'transition'
        - land_pressure: 'low' | 'high'
        - ocean_pressure: 'low' | 'high'
        - wind_direction: 风向角度
        - wind_name: 中文名称
        - wind_name_en: 英文名称
        - strength: 季风强度 (0~1)
    """
    # 使用正弦函数平滑过渡
    # 夏季峰值在 7 月, 冬季峰值在 1 月
    monsoon_phase = np.sin(2 * np.pi * (month - 4) / 12)

    if monsoon_phase > 0.3:
        # 夏季模式
        strength = min(1.0, (monsoon_phase - 0.3) / 0.7)
        return {
            "season": "summer",
            "land_pressure": "low",
            "ocean_pressure": "high",
            "wind_direction": -45,  # 东南风 (箭头指向西北, 表示风从东南来)
            "wind_name": "东南季风",
            "wind_name_en": "SE Monsoon",
            "strength": strength,
        }
    elif monsoon_phase < -0.3:
        # 冬季模式
        strength = min(1.0, abs(monsoon_phase + 0.3) / 0.7)
        return {
            "season": "winter",
            "land_pressure": "high",
            "ocean_pressure": "low",
            "wind_direction": 135,  # 西北风 (箭头指向东南, 表示风从西北来)
            "wind_name": "西北季风",
            "wind_name_en": "NW Monsoon",
            "strength": strength,
        }
    else:
        # 过渡期
        return {
            "season": "transition",
            "land_pressure": "neutral",
            "ocean_pressure": "neutral",
            "wind_direction": 0,
            "wind_name": "过渡期弱风",
            "wind_name_en": "Weak Variable",
            "strength": 0.3,
        }


# ============================================================
# 6. 雨带 (ITCZ 降水) 模型
# ============================================================

def get_rain_belt_position(month: float) -> Dict:
    """
    计算雨带 (ITCZ 降水集中区) 位置.

    雨带大致跟随太阳直射点, 但有一定滞后 (约 1 个月).
    北半球夏季雨带北移最远可达 20-25°N (青藏高原南缘).

    Args:
        month: 月份

    Returns:
        包含雨带纬度范围和强度的字典
    """
    # 雨带有约 1 个月的热力滞后
    declination_lag = get_solar_declination(month - 1)

    # 雨带纬度范围: 中心 ± 宽度
    # 大陆效应使北半球雨带比南半球更偏北
    lat_center = declination_lag * 0.9  # 雨带偏移约为直射点的 90%

    # 夏季雨带更宽 (对流更强)
    if abs(lat_center) > 10:
        half_width = 8.0
    else:
        half_width = 5.0

    # 强度: 直射点附近最强
    intensity = 1.0 - abs(declination_lag) / 30.0
    intensity = np.clip(intensity, 0.3, 1.0)

    return {
        "lat_center": lat_center,
        "lat_min": lat_center - half_width,
        "lat_max": lat_center + half_width,
        "intensity": intensity,
        "declination": declination_lag,
    }


# ============================================================
# 7. 气候带模型
# ============================================================

@dataclass
class ClimateZone:
    """单个气候带"""
    name: str           # 中文名称
    name_en: str        # 英文名称
    lat_range: Tuple[float, float]  # 大致纬度范围
    formation: str      # 形成原因
    typical_areas: str  # 典型分布地区
    precipitation: str  # 降水特点
    temperature: str    # 气温特点
    color: str          # 显示颜色


# 基准气候带定义
CLIMATE_ZONES_BASE = [
    ClimateZone(
        "热带雨林气候", "Tropical Rainforest",
        (-5, 5),
        "全年受赤道低压带控制, 盛行上升气流, 高温多雨",
        "亚马孙平原, 刚果盆地, 马来群岛",
        "年降水量 >2000mm, 全年多雨, 无明显干季",
        "年均温 25-28°C, 年较差小 (<3°C)",
        "#006837",
    ),
    ClimateZone(
        "热带草原气候", "Tropical Savanna",
        (5, 15),
        "赤道低压带与信风带交替控制; 夏季受赤道低压控制多雨, 冬季受信风控制干燥",
        "非洲中部, 巴西高原, 印度半岛部分",
        "年降水量 750-1500mm, 干湿季分明",
        "年均温 20-30°C, 年较差 5-10°C",
        "#78c679",
    ),
    ClimateZone(
        "热带沙漠气候", "Tropical Desert",
        (15, 30),
        "常年受副热带高压和信风带控制, 盛行下沉气流",
        "撒哈拉沙漠, 阿拉伯半岛, 澳大利亚中西部",
        "年降水量 <250mm, 极端干燥",
        "夏季炎热 (30-50°C), 年较差和日较差均大",
        "#fed976",
    ),
    ClimateZone(
        "地中海气候", "Mediterranean",
        (30, 40),
        "夏季受副热带高压控制干燥, 冬季受西风带控制多雨",
        "地中海沿岸, 加州, 智利中部, 南非开普敦, 澳大利亚西南",
        "年降水量 300-1000mm, 冬雨夏干",
        "夏季 20-28°C, 冬季 5-15°C",
        "#fdae61",
    ),
    ClimateZone(
        "温带海洋性气候", "Maritime Temperate",
        (40, 60),
        "全年受盛行西风带控制, 沿海暖流增温增湿",
        "西欧, 北美西北海岸, 新西兰, 智利南部",
        "年降水量 700-1000mm, 全年均匀分配",
        "冬暖夏凉, 年均温 10-15°C, 年较差小 (<15°C)",
        "#4575b4",
    ),
    ClimateZone(
        "温带季风气候", "Temperate Monsoon",
        (35, 55),
        "海陆热力性质差异: 夏季受海洋季风影响多雨, 冬季受大陆季风影响干燥",
        "中国华北/东北, 日本, 朝鲜半岛, 俄罗斯远东",
        "年降水量 500-1000mm, 夏雨冬干",
        "夏季 25-30°C, 冬季 -10~5°C, 年较差大",
        "#d73027",
    ),
    ClimateZone(
        "温带大陆性气候", "Continental",
        (40, 60),
        "深居内陆, 远离海洋, 受大陆气团控制",
        "中亚, 蒙古, 北美内陆, 俄罗斯西伯利亚",
        "年降水量 <400mm, 集中在夏季",
        "夏季炎热, 冬季严寒, 年较差极大 (>30°C)",
        "#a6d854",
    ),
    ClimateZone(
        "亚寒带针叶林气候", "Subarctic",
        (55, 70),
        "纬度高, 冬季漫长严寒, 夏季短暂凉爽",
        "西伯利亚, 加拿大北部, 阿拉斯加",
        "年降水量 300-600mm, 集中在夏季, 冬季积雪",
        "冬季 -30~-10°C, 夏季 10-20°C, 年较差极大",
        "#2c7bb6",
    ),
    ClimateZone(
        "极地气候", "Polar",
        (70, 90),
        "纬度高, 太阳辐射极少, 常年受极地高压控制",
        "格陵兰, 南极洲, 北冰洋沿岸",
        "年降水量 <250mm, 以雪为主",
        "最热月 <10°C, 终年严寒",
        "#d9d9d9",
    ),
]


def get_climate_zones(
    declination: float,
    shift_amplitude: float = 10.0
) -> List[ClimateZone]:
    """
    根据太阳直射点位置调整气候带边界.

    Args:
        declination: 太阳直射纬度
        shift_amplitude: 偏移幅度

    Returns:
        偏移后的气候带列表
    """
    shift = (declination / 23.5) * shift_amplitude * 0.7

    shifted = []
    for zone in CLIMATE_ZONES_BASE:
        new_min = zone.lat_range[0] + shift
        new_max = zone.lat_range[1] + shift
        shifted.append(ClimateZone(
            name=zone.name,
            name_en=zone.name_en,
            lat_range=(new_min, new_max),
            formation=zone.formation,
            typical_areas=zone.typical_areas,
            precipitation=zone.precipitation,
            temperature=zone.temperature,
            color=zone.color,
        ))

    return shifted


# ============================================================
# 8. 辅助绘图函数
# ============================================================

def get_lat_ticks() -> Tuple[np.ndarray, List[str]]:
    """获取纬度刻度标签"""
    ticks = np.arange(-90, 91, 15)
    labels = []
    for t in ticks:
        if t > 0:
            labels.append(f"{int(t)}°N")
        elif t < 0:
            labels.append(f"{int(abs(t))}°S")
        else:
            labels.append("0°")
    return ticks, labels


def add_globe_bg(ax, lat_range=(-90, 90)):
    """
    为纬度剖面图添加地球背景色:
    - 低纬度更暖色, 高纬度更冷色
    """
    import matplotlib.pyplot as plt

    y_min, y_max = lat_range
    # 纬度渐变背景
    for lat in np.linspace(y_min, y_max, 200):
        frac = abs(lat) / 90
        # 从热带暖色渐变到极地冷色
        r = 1.0 - frac * 0.4
        g = 1.0 - frac * 0.6
        b = 1.0 - frac * 0.3
        ax.axhspan(lat - 0.5, lat + 0.5, color=(r, g, b), alpha=0.15, zorder=0)

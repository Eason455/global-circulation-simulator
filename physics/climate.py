"""
气候带模型 — Climate Zones
==========================
9 大气候带定义, 支持随太阳直射点偏移联动.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ClimateZone:
    """单个气候带"""
    name: str
    name_en: str
    lat_range: Tuple[float, float]
    formation: str
    typical_areas: str
    precipitation: str
    temperature: str
    color: str


CLIMATE_ZONES_BASE = [
    ClimateZone("热带雨林气候", "Tropical Rainforest", (-5, 5),
        "全年受赤道低压带控制, 盛行上升气流, 高温多雨",
        "亚马孙平原, 刚果盆地, 马来群岛",
        "年降水量 >2000mm, 全年多雨, 无明显干季",
        "年均温 25-28 deg C, 年较差小 (<3 deg C)", "#006837"),
    ClimateZone("热带草原气候", "Tropical Savanna", (5, 15),
        "赤道低压带与信风带交替控制; 夏季受赤道低压控制多雨, 冬季受信风控制干燥",
        "非洲中部, 巴西高原, 印度半岛部分",
        "年降水量 750-1500mm, 干湿季分明",
        "年均温 20-30 deg C, 年较差 5-10 deg C", "#78c679"),
    ClimateZone("热带沙漠气候", "Tropical Desert", (15, 30),
        "常年受副热带高压和信风带控制, 盛行下沉气流",
        "撒哈拉沙漠, 阿拉伯半岛, 澳大利亚中西部",
        "年降水量 <250mm, 极端干燥",
        "夏季炎热 (30-50 deg C), 年较差和日较差均大", "#fed976"),
    ClimateZone("地中海气候", "Mediterranean", (30, 40),
        "夏季受副热带高压控制干燥, 冬季受西风带控制多雨",
        "地中海沿岸, 加州, 智利中部, 南非开普敦, 澳大利亚西南",
        "年降水量 300-1000mm, 冬雨夏干",
        "夏季 20-28 deg C, 冬季 5-15 deg C", "#fdae61"),
    ClimateZone("温带海洋性气候", "Maritime Temperate", (40, 60),
        "全年受盛行西风带控制, 沿海暖流增温增湿",
        "西欧, 北美西北海岸, 新西兰, 智利南部",
        "年降水量 700-1000mm, 全年均匀分配",
        "冬暖夏凉, 年均温 10-15 deg C, 年较差小 (<15 deg C)", "#4575b4"),
    ClimateZone("温带季风气候", "Temperate Monsoon", (35, 55),
        "海陆热力性质差异: 夏季受海洋季风影响多雨, 冬季受大陆季风影响干燥",
        "中国华北/东北, 日本, 朝鲜半岛, 俄罗斯远东",
        "年降水量 500-1000mm, 夏雨冬干",
        "夏季 25-30 deg C, 冬季 -10~5 deg C, 年较差大", "#d73027"),
    ClimateZone("温带大陆性气候", "Continental", (40, 60),
        "深居内陆, 远离海洋, 受大陆气团控制",
        "中亚, 蒙古, 北美内陆, 俄罗斯西伯利亚",
        "年降水量 <400mm, 集中在夏季",
        "夏季炎热, 冬季严寒, 年较差极大 (>30 deg C)", "#a6d854"),
    ClimateZone("亚寒带针叶林气候", "Subarctic", (55, 70),
        "纬度高, 冬季漫长严寒, 夏季短暂凉爽",
        "西伯利亚, 加拿大北部, 阿拉斯加",
        "年降水量 300-600mm, 集中在夏季, 冬季积雪",
        "冬季 -30~-10 deg C, 夏季 10-20 deg C, 年较差极大", "#2c7bb6"),
    ClimateZone("极地气候", "Polar", (70, 90),
        "纬度高, 太阳辐射极少, 常年受极地高压控制",
        "格陵兰, 南极洲, 北冰洋沿岸",
        "年降水量 <250mm, 以雪为主",
        "最热月 <10 deg C, 终年严寒", "#d9d9d9"),
]


def get_climate_zones(
    declination: float, shift_amplitude: float = 10.0
) -> List[ClimateZone]:
    """根据太阳直射点位置调整气候带边界."""
    shift = (declination / 23.5) * shift_amplitude * 0.7
    shifted = []
    for zone in CLIMATE_ZONES_BASE:
        shifted.append(ClimateZone(
            name=zone.name, name_en=zone.name_en,
            lat_range=(zone.lat_range[0] + shift, zone.lat_range[1] + shift),
            formation=zone.formation, typical_areas=zone.typical_areas,
            precipitation=zone.precipitation, temperature=zone.temperature,
            color=zone.color))
    return shifted

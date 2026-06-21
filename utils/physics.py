"""
全球大气环流物理模型 — 兼容层
===========================
此模块向后兼容所有现有导入.
实际实现位于 physics/ 子模块中.

如需直接引用各子模块:
  from physics.solar import get_solar_declination, get_season_name, get_month_name
  from physics.pressure import PressureBelt, PRESSURE_BELTS_BASE, get_pressure_belt_positions, ...
  from physics.wind import WindBelt, get_wind_belts
  from physics.circulation import CirculationCell, get_circulation_cells
  from physics.monsoon import get_monsoon_state, get_monsoon_season
  from physics.rain import get_rain_belt_position
  from physics.climate import ClimateZone, CLIMATE_ZONES_BASE, get_climate_zones
  from physics.helpers import get_lat_ticks, add_globe_bg
"""

from physics import *

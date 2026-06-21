"""
global-circulation-simulator 物理/地理模型层
=========================================

拆分为独立子模块:
  solar.py      — 太阳直射点
  pressure.py   — 气压带
  wind.py       — 风带
  circulation.py — 三圈环流
  monsoon.py    — 东亚季风
  rain.py       — 雨带
  climate.py    — 气候带
  helpers.py    — 绘图辅助函数

向后兼容: utils/physics.py 通过 `from physics import *` 导出所有符号.
"""

from physics.solar import *
from physics.pressure import *
from physics.wind import *
from physics.circulation import *
from physics.monsoon import *
from physics.rain import *
from physics.climate import *
from physics.helpers import *

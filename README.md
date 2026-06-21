# 全球气压带风带季节移动与东亚季风形成交互模拟器

面向高中地理学习的动态可视化教学工具。

## 功能模块

### 模块1: 太阳直射点周年运动
在地球示意图上动态显示太阳直射点位置，支持时间轴拖动。

### 模块2: 全球气压带与风带动态模拟
绘制全球纬度剖面图，显示气压带与风带随太阳直射点的同步偏移。

### 模块3: 三圈环流可视化
哈德莱环流、费雷尔环流、极地环流的流线动画展示。

### 模块4: 东亚季风形成模拟
亚洲大陆-太平洋简化地图，展示夏季东南季风和冬季西北季风。

### 模块5: 雨带移动模拟
ITCZ降水带的季节移动可视化。

### 模块6: 全球气候带联动
气候带分布与气压带/风带联动，点击查看详细信息。

### 模块7: 考试模式
随机出题，自动判分，适合课堂练习。

## 安装与运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## 项目结构

```
global-circulation-simulator/
├── app.py                 # Streamlit 主应用 (UI布局, 交互控制)
├── requirements.txt       # Python 依赖
├── README.md              # 项目说明
├── utils/
│   ├── __init__.py
│   └── physics.py         # 共享物理计算模型
└── modules/
    ├── __init__.py
    ├── solar_declination.py       # 模块1: 太阳直射点
    ├── pressure_wind_belts.py     # 模块2: 气压带与风带
    ├── three_cell_circulation.py  # 模块3: 三圈环流
    ├── east_asian_monsoon.py      # 模块4: 东亚季风
    ├── rain_belt.py               # 模块5: 雨带移动
    ├── climate_zones.py           # 模块6: 气候带联动
    └── exam_mode.py               # 模块7: 考试模式
```

## 使用说明

1. 启动后使用侧边栏控制面板调整月份和显示选项
2. 可开启动画自动播放全年变化
3. 点击 "开始考试" 进入考试模式
4. 在气候带下拉菜单中选择具体类型查看详细信息

## 物理模型

- 太阳赤纬: delta = 23.5 deg × sin(2 pi × (month - 3) / 12)
- 气压带偏移: 随太阳直射点按不同比例偏移 (ITCZ 100%, 副热带 80%, 副极地 50%, 极地 10%)
- 季风判定: 基于海陆热力性质差异的简化正弦模型
- 雨带位置: 太阳直射点滞后约 1 个月

## 技术栈

- Python 3.9+
- Streamlit (Web UI)
- Matplotlib (可视化)
- NumPy (数值计算)

## 参考

- 人教版高中地理选择性必修1
- NASA Earth Observatory
- IPCC 气候系统基础

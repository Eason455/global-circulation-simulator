"""
全球大气环流模拟器 — 主入口
===========================
子页面导航架构: 侧边栏 radio 选择模块, 主区域渲染对应页面.
动画由 main() 统一驱动: 渲染完整页面 → sleep → st.rerun().
"""

import time
import sys
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 中文字体 (跨平台)
# ============================================================
plt.rcParams['font.sans-serif'] = [
    'Microsoft YaHei', 'SimHei',
    'Noto Sans CJK SC', 'Noto Sans SC',
    'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',
    'PingFang SC', 'Heiti SC',
    'STFangsong', 'KaiTi', 'DejaVu Sans',
]
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="全球大气环流与东亚季风 | 交互模拟器",
    page_icon="data:image/svg+xml," + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='14' fill='%230071e3'/%3E%3Ccircle cx='10' cy='12' r='3' fill='white' opacity='.9'/%3E%3Cpath d='M6 22 Q16 28 26 22' stroke='white' stroke-width='1.5' fill='none' opacity='.7'/%3E%3C/svg%3E",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS 加载 — 多重回退
# ============================================================
def load_css():
    css_content = None
    candidates = [
        Path(__file__).resolve().parent / "assets" / "style.css",
        Path(sys.argv[0]).resolve().parent / "assets" / "style.css",
        Path(r"Z:\global-circulation-simulator\assets\style.css"),
    ]
    for css_path in candidates:
        try:
            if css_path.exists():
                css_content = css_path.read_text(encoding="utf-8")
                break
        except Exception:
            continue
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

load_css()

# ============================================================
# 导入
# ============================================================
from ui.sidebar import render_sidebar
from ui.header import render_header
from ui.pages.solar import render_solar_page
from ui.pages.pressure_wind import render_pressure_wind_page
from ui.pages.circulation import render_circulation_page
from ui.pages.monsoon import render_monsoon_page
from ui.pages.rain import render_rain_page
from ui.pages.climate import render_climate_page
from ui.exam import render_exam_mode

# ============================================================
# 会话状态初始化
# ============================================================
def init_session_state():
    defaults = {
        "month": 7.0,
        "anim_speed": "normal",
        "shift_amplitude": 10,
        "animating": False,
        "exam_active": False,
        "exam_questions": [],
        "exam_answers": [],
        "exam_submitted": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# ============================================================
# 页面路由
# ============================================================
PAGE_MAP = {
    "太阳直射点周年运动": render_solar_page,
    "气压带与风带分布":    render_pressure_wind_page,
    "三圈环流":           render_circulation_page,
    "东亚季风形成模拟":    render_monsoon_page,
    "全球降水带移动":      render_rain_page,
    "全球气候带分布":      render_climate_page,
    "考试模式":           render_exam_mode,
}

# ============================================================
# 动画驱动
# ============================================================
ANIM_SPEEDS = {"slow": 0.003, "normal": 0.010, "fast": 0.030}
ANIM_DELAYS = {"slow": 0.06, "normal": 0.03, "fast": 0.015}

def main():
    page = render_sidebar()
    render_header()

    render_func = PAGE_MAP.get(page, render_solar_page)
    render_func()

    # 页脚
    st.divider()
    st.caption(
        "全球大气环流与东亚季风模拟器 · "
        "高中地理教学可视化工具 · "
        "基于大气环流经典理论，仅供教学演示参考"
    )

    # 动画: 渲染完整页面后推进月份并触发下一帧
    if st.session_state.animating:
        step = ANIM_SPEEDS.get(st.session_state.anim_speed, 0.010)
        delay = ANIM_DELAYS.get(st.session_state.anim_speed, 0.03)
        st.session_state.month += step
        if st.session_state.month > 13:
            st.session_state.month -= 12
        time.sleep(delay)
        st.rerun()

if __name__ == "__main__":
    main()

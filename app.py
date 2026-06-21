"""
全球气压带风带季节移动与东亚季风形成交互模拟器
==========================================
面向高中地理学习的动态可视化教学工具.

功能模块:
  1. 太阳直射点周年运动
  2. 全球气压带与风带动态模拟
  3. 三圈环流可视化
  4. 东亚季风形成模拟
  5. 雨带移动模拟
  6. 全球气候带联动
  7. 交互控制面板 + 考试模式

运行方式:
  streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

# 设置中文字体 (跨平台兼容: Windows/Linux/macOS)
plt.rcParams['font.sans-serif'] = [
    'Microsoft YaHei', 'SimHei',
    'Noto Sans CJK SC', 'Noto Sans SC',
    'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',
    'PingFang SC', 'Heiti SC',
    'STFangsong', 'KaiTi',
    'DejaVu Sans',
]
plt.rcParams['axes.unicode_minus'] = False

# 导入各功能模块
from modules.solar_declination import plot_solar_declination
from modules.pressure_wind_belts import plot_pressure_wind_belts
from modules.three_cell_circulation import plot_three_cell_circulation
from modules.east_asian_monsoon import plot_east_asian_monsoon
from modules.rain_belt import plot_rain_belt
from modules.climate_zones import (
    plot_climate_zones,
    get_climate_zone_detail,
    render_climate_detail,
)
from modules.exam_mode import generate_questions, grade_exam
from utils.physics import (
    get_solar_declination,
    get_month_name,
    get_season_name,
)

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
# Apple Design System + Glassmorphism CSS
# ============================================================
st.markdown("""
<style>
/* ============================================================
   DESIGN TOKENS — Apple Human Interface Guidelines
   ============================================================ */
:root {
  --bg-primary: #f5f5f7;
  --bg-secondary: #ffffff;
  --bg-elevated: rgba(255,255,255,0.48);
  --bg-glass: rgba(255,255,255,0.64);
  --text-primary: #1d1d1f;
  --text-secondary: #86868b;
  --text-tertiary: #aeaeb2;
  --accent: #0071e3;
  --accent-hover: #0077ed;
  --success: #34c759;
  --warning: #ff9f0a;
  --danger: #ff3b30;
  --border: rgba(60,60,67,0.12);
  --border-subtle: rgba(60,60,67,0.07);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
  --shadow-md: 0 2px 16px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 40px rgba(0,0,0,0.08);
  --shadow-xl: 0 20px 60px rgba(0,0,0,0.10);
  --radius-sm: 12px;
  --radius: 18px;
  --radius-lg: 24px;
  --radius-xl: 32px;
  --smooth: cubic-bezier(0.25, 0.1, 0, 1);
  --spring: cubic-bezier(0.2, 0.9, 0.4, 1.1);
}

/* ============================================================
   GLOBAL BASE
   ============================================================ */
.stApp {
  background: var(--bg-primary);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
               "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Subtle background texture */
.stApp::before {
  content: '';
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 0;
  pointer-events: none; opacity: 0.025;
  mix-blend-mode: soft-light;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 256px 256px;
}

/* Radial glow (subtle ambient light) */
.stApp::after {
  content: '';
  position: fixed; top: -30%; left: -20%; width: 140%; height: 160%; z-index: 0;
  pointer-events: none;
  background: radial-gradient(ellipse at 50% 35%, rgba(0,113,227,0.03) 0%, transparent 60%),
              radial-gradient(ellipse at 80% 20%, rgba(120,120,128,0.02) 0%, transparent 50%);
}

/* Main content wrapper */
.main .block-container {
  position: relative; z-index: 1;
  padding-top: 1.5rem;
}

/* ============================================================
   SIDEBAR — Frosted Glass
   ============================================================ */
section[data-testid="stSidebar"] {
  background: rgba(245,245,247,0.72) !important;
  backdrop-filter: blur(28px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
  border-right: 0.5px solid var(--border) !important;
  box-shadow: var(--shadow-lg) !important;
}

section[data-testid="stSidebar"] .block-container {
  padding: 1.25rem 1rem;
}

section[data-testid="stSidebar"] h2 {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

section[data-testid="stSidebar"] h3 {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: -0.2px;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin: 1.25rem 0 0.5rem;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
  color: var(--text-primary) !important;
  font-size: 14px;
}

section[data-testid="stSidebar"] hr {
  border-color: var(--border);
  margin: 1rem 0;
}

/* Sidebar metric boxes */
section[data-testid="stSidebar"] div[data-testid="stMetric"] {
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  border: 0.5px solid var(--border-subtle);
  box-shadow: var(--shadow-sm);
}

section[data-testid="stSidebar"] div[data-testid="stMetric"] label {
  font-size: 11px !important;
  color: var(--text-secondary) !important;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

section[data-testid="stSidebar"] div[data-testid="stMetric"] div {
  font-size: 16px !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
}

/* ============================================================
   GLASS CARDS
   ============================================================ */
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-lg);
  border: 0.5px solid var(--border);
  box-shadow: var(--shadow-md);
  padding: 1.5rem;
  transition: all 0.35s var(--smooth);
  margin-bottom: 1rem;
}

.glass-card:hover {
  box-shadow: var(--shadow-lg);
  background: rgba(255,255,255,0.72);
}

/* ============================================================
   BUTTONS — Apple Style
   ============================================================ */
.stButton > button {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC",
               "Microsoft YaHei", sans-serif;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.2px;
  border-radius: var(--radius-xl);
  padding: 10px 20px;
  border: none;
  transition: all 0.3s var(--smooth);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  box-shadow: var(--shadow-sm);
}

.stButton > button:active {
  transform: scale(0.97);
}

/* Primary button */
.stButton > button[kind="primary"],
.stButton > button:has(svg) {
  background: rgba(29,29,31,0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
}

.stButton > button[kind="primary"]:hover,
.stButton > button:has(svg):hover {
  background: rgba(0,0,0,0.92);
  box-shadow: var(--shadow-md);
}

/* Secondary button */
.stButton > button[kind="secondary"] {
  background: rgba(60,60,67,0.08);
  color: var(--text-primary);
}

.stButton > button[kind="secondary"]:hover {
  background: rgba(60,60,67,0.12);
  box-shadow: var(--shadow-sm);
}

/* ============================================================
   SLIDERS & RADIO — Refined
   ============================================================ */
div[data-testid="stSlider"] > div {
  padding: 0 2px;
}

.stRadio > div {
  gap: 6px;
}

.stRadio label {
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  border: 0.5px solid var(--border);
  background: rgba(255,255,255,0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.25s var(--smooth);
  font-size: 13px !important;
}

.stRadio label:hover {
  background: var(--bg-glass);
  border-color: var(--accent);
}

/* ============================================================
   CHECKBOXES — Clean
   ============================================================ */
.stCheckbox label {
  padding: 6px 0;
  font-size: 14px;
  color: var(--text-primary);
}

/* ============================================================
   EXPANDER — Knowledge Panel
   ============================================================ */
.streamlit-expanderHeader {
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: var(--radius);
  border: 0.5px solid var(--border);
  padding: 12px 16px;
  box-shadow: var(--shadow-sm);
}

.streamlit-expanderHeader:hover {
  box-shadow: var(--shadow-md);
}

.streamlit-expanderContent {
  background: rgba(255,255,255,0.4);
  border-radius: 0 0 var(--radius) var(--radius);
  border: 0.5px solid var(--border-subtle);
  border-top: none;
  padding: 1rem 1.5rem;
}

/* ============================================================
   TYPOGRAPHY
   ============================================================ */
h1 {
  font-size: 32px !important;
  font-weight: 700 !important;
  letter-spacing: -0.025em !important;
  color: var(--text-primary) !important;
  margin-bottom: 0.15rem !important;
}

h2 {
  font-size: 20px !important;
  font-weight: 700 !important;
  letter-spacing: -0.3px !important;
  color: var(--text-primary) !important;
}

h3 {
  font-size: 17px !important;
  font-weight: 600 !important;
  letter-spacing: -0.2px !important;
  color: var(--text-secondary) !important;
}

h4 {
  font-size: 15px !important;
  font-weight: 600 !important;
  letter-spacing: -0.1px !important;
  color: var(--text-primary) !important;
}

/* Caption */
.caption-text {
  font-size: 13px;
  color: var(--text-secondary);
  letter-spacing: -0.1px;
}

/* ============================================================
   STATUS BADGE — Apple-style pill
   ============================================================ */
.status-pill {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1px;
  background: rgba(0,113,227,0.1);
  color: var(--accent);
}

/* ============================================================
   METRIC BOX — Dashboard
   ============================================================ */
.metric-glass {
  background: var(--bg-glass);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-radius: var(--radius-lg);
  border: 0.5px solid var(--border);
  padding: 20px 16px;
  text-align: center;
  box-shadow: var(--shadow-md);
  transition: all 0.35s var(--smooth);
}

.metric-glass:hover {
  box-shadow: var(--shadow-lg);
}

.metric-glass .value {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--text-primary);
}

.metric-glass .label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-top: 4px;
}

/* ============================================================
   EXAM CARDS
   ============================================================ */
.exam-correct {
  background: rgba(52,199,89,0.08);
  border-left: 3px solid var(--success);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  margin: 8px 0;
}

.exam-wrong {
  background: rgba(255,59,48,0.06);
  border-left: 3px solid var(--danger);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  margin: 8px 0;
}

.exam-score {
  background: var(--bg-glass);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-xl);
  padding: 28px;
  text-align: center;
  border: 0.5px solid var(--border);
  box-shadow: var(--shadow-lg);
}

.exam-score .score-num {
  font-size: 56px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1;
}

/* ============================================================
   SELECT BOX — Apple style
   ============================================================ */
.stSelectbox > div > div {
  border-radius: var(--radius-sm) !important;
  border: 0.5px solid var(--border) !important;
  background: rgba(255,255,255,0.6) !important;
}

/* ============================================================
   DIVIDER — Subtle
   ============================================================ */
hr {
  border: none;
  border-top: 0.5px solid var(--border);
  margin: 0.5rem 0;
}

/* ============================================================
   TABS
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: rgba(60,60,67,0.04);
  border-radius: var(--radius-xl);
  padding: 3px;
}

.stTabs [data-baseweb="tab"] {
  border-radius: var(--radius-xl);
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: white;
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 初始化会话状态
# ============================================================
def init_session_state():
    """初始化 Streamlit 会话状态变量"""
    defaults = {
        "month": 7.0,              # 当前月份 (默认7月=夏季)
        "anim_speed": "normal",    # 动画速度: slow/normal/fast
        "shift_amplitude": 10,     # 风带移动幅度: 5/10/15
        "show_solar": True,        # 显示太阳直射点
        "show_circulation": True,  # 显示三圈环流
        "show_wind": True,         # 显示风带
        "show_monsoon": True,      # 显示季风
        "show_rain": True,         # 显示雨带
        "show_climate": True,      # 显示气候带
        "highlight_climate": None, # 高亮气候带名称
        "animating": False,        # 是否正在播放动画
        "exam_active": False,      # 考试模式是否激活
        "exam_questions": [],      # 考试题目
        "exam_answers": [],        # 用户答案
        "exam_submitted": False,   # 是否已提交
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ============================================================
# 侧边栏: 交互控制面板
# ============================================================
def render_sidebar() -> None:
    """渲染侧边栏控制面板 — Apple 毛玻璃风格"""
    with st.sidebar:
        st.markdown('<div style="font-size:18px;font-weight:700;letter-spacing:-0.3px;color:#1d1d1f;">控制面板</div>', unsafe_allow_html=True)
        st.caption("全球大气环流模拟器")

        # ---- 月份滑块 ----
        st.markdown("##### 月份选择")
        month = st.slider(
            "拖动选择月份",
            min_value=0.1,
            max_value=12.9,
            value=st.session_state.month,
            step=0.1,
            format="%.1f",
            key="month_slider",
        )
        st.session_state.month = month

        decl = get_solar_declination(month)
        decl_str = f"{abs(decl):.1f}" + ("°N" if decl >= 0 else "°S")
        season = get_season_name(month)
        month_name = get_month_name(month)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("月份", month_name)
        with col2:
            st.metric("季节", season)
        with col3:
            st.metric("直射纬度", decl_str)

        st.divider()

        # ---- 动画控制 ----
        st.markdown("##### 动画控制")
        anim_speed = st.select_slider(
            "速度",
            options=["slow", "normal", "fast"],
            value=st.session_state.anim_speed,
            format_func=lambda x: {"slow": "慢速", "normal": "正常", "fast": "快速"}[x],
            key="anim_speed_select",
        )
        st.session_state.anim_speed = anim_speed

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("播放动画", use_container_width=True, type="primary"):
                st.session_state.animating = True
                st.rerun()
        with col_b:
            if st.button("停止", use_container_width=True):
                st.session_state.animating = False
                st.rerun()

        st.divider()

        # ---- 风带移动幅度 ----
        st.markdown("##### 移动幅度")
        shift_amplitude = st.radio(
            "气压带/风带季节移动幅度",
            options=[5, 10, 15],
            index=1,
            format_func=lambda x: "±" + str(x) + "°",
            horizontal=True,
            key="shift_radio",
        )
        st.session_state.shift_amplitude = shift_amplitude

        st.divider()

        # ---- 显示开关 ----
        st.markdown("##### 显示开关")
        st.session_state.show_solar = st.checkbox("太阳直射点", value=True)
        st.session_state.show_circulation = st.checkbox("三圈环流", value=True)
        st.session_state.show_wind = st.checkbox("气压带与风带", value=True)
        st.session_state.show_monsoon = st.checkbox("东亚季风", value=True)
        st.session_state.show_rain = st.checkbox("雨带移动 (ITCZ)", value=True)
        st.session_state.show_climate = st.checkbox("气候带联动", value=True)

        st.divider()

        # ---- 考试模式 ----
        st.markdown("##### 考试模式")
        if not st.session_state.exam_active:
            if st.button("开始考试", use_container_width=True, type="primary"):
                st.session_state.exam_active = True
                st.session_state.exam_questions = generate_questions(4)
                st.session_state.exam_answers = [-1] * 4
                st.session_state.exam_submitted = False
                st.rerun()
        else:
            if st.button("退出考试", use_container_width=True):
                st.session_state.exam_active = False
                st.session_state.exam_submitted = False
                st.rerun()

        st.divider()

        # ---- 图例说明 ----
        st.markdown("##### 图例说明")
        st.markdown("""
        <div style="font-size:12px; color:#86868b; line-height:1.7;">
        <b style="color:#1d1d1f;">气压带标记:</b><br>
        <span style="color:#00b894;">L</span> = 低压 (上升气流, 多云雨)<br>
        <span style="color:#e17055;">H</span> = 高压 (下沉气流, 晴燥)<br><br>
        <b style="color:#1d1d1f;">环流颜色:</b><br>
        <span style="color:#d63031;">红色</span> = 上升气流<br>
        <span style="color:#0984e3;">蓝色</span> = 下沉气流<br><br>
        <b style="color:#1d1d1f;">气压带缩写:</b><br>
        ITCZ = 赤道低压带<br>
        STH = 副热带高压带<br>
        SPL = 副极地低压带<br>
        PHP = 极地高压带
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 动画循环
# ============================================================
def handle_animation():
    """处理自动动画播放"""
    if st.session_state.animating:
        speeds = {"slow": 0.05, "normal": 0.12, "fast": 0.3}
        step = speeds.get(st.session_state.anim_speed, 0.12)

        new_month = st.session_state.month + step
        if new_month > 13:
            new_month -= 12
        st.session_state.month = new_month

        # 使用 Streamlit 的自动刷新
        import time
        time.sleep(0.3)
        st.rerun()


# ============================================================
# 页面标题和状态栏
# ============================================================
def render_header():
    """渲染页面标题和信息栏 — Apple 风格"""
    col_title, col_status = st.columns([3, 1])

    with col_title:
        st.title("全球大气环流与东亚季风")
        st.markdown(
            '<span class="caption-text">交互式地理教学工具 &middot; '
            '基于大气环流经典理论 &middot; '
            '参考人教版高中地理选择性必修1</span>',
            unsafe_allow_html=True,
        )

    with col_status:
        month = st.session_state.month
        decl = get_solar_declination(month)
        season = get_season_name(month)
        decl_str = f"{abs(decl):.1f}" + ("°N" if decl >= 0 else "°S")

        st.markdown(f"""
        <div class="metric-glass">
            <div class="value">{get_month_name(month)}</div>
            <div class="label">{season} &middot; 直射 {decl_str}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 主可视化布局
# ============================================================
def render_main_visualizations():
    """渲染主可视化区域 (上排: 全球环流 + 季风, 下排: 气候带)"""

    # ---- 第一行: 太阳直射点 + 气压带风带 + 三圈环流 ----
    st.divider()
    st.subheader("一、全球大气环流系统")

    active_panels = []
    if st.session_state.show_solar:
        active_panels.append("solar")
    if st.session_state.show_wind:
        active_panels.append("wind")
    if st.session_state.show_circulation:
        active_panels.append("circulation")

    if active_panels:
        cols = st.columns(len(active_panels))

        for col, panel in zip(cols, active_panels):
            with col:
                if panel == "solar":
                    st.markdown("#### 太阳直射点周年运动")
                    fig, ax = plt.subplots(figsize=(5, 4.5))
                    plot_solar_declination(ax, st.session_state.month)
                    st.pyplot(fig)
                    plt.close(fig)

                elif panel == "wind":
                    st.markdown("#### 气压带与风带分布")
                    fig, ax = plt.subplots(figsize=(5, 5.5))
                    plot_pressure_wind_belts(
                        ax,
                        st.session_state.month,
                        st.session_state.shift_amplitude,
                    )
                    st.pyplot(fig)
                    plt.close(fig)

                elif panel == "circulation":
                    st.markdown("#### 三圈环流")
                    fig, ax = plt.subplots(figsize=(6, 4.5))
                    plot_three_cell_circulation(
                        ax,
                        st.session_state.month,
                        st.session_state.shift_amplitude,
                    )
                    st.pyplot(fig)
                    plt.close(fig)
    else:
        st.info("请在侧边栏开启至少一个显示选项。")

    # ---- 第二行: 东亚季风 + 雨带移动 ----
    st.divider()
    st.subheader("二、东亚季风与降水系统")

    panels_row2 = []
    if st.session_state.show_monsoon:
        panels_row2.append("monsoon")
    if st.session_state.show_rain:
        panels_row2.append("rain")

    if panels_row2:
        cols = st.columns(len(panels_row2))

        for col, panel in zip(cols, panels_row2):
            with col:
                if panel == "monsoon":
                    st.markdown("#### 东亚季风形成模拟")
                    fig, ax = plt.subplots(figsize=(5.5, 5))
                    plot_east_asian_monsoon(ax, st.session_state.month)
                    st.pyplot(fig)
                    plt.close(fig)

                elif panel == "rain":
                    st.markdown("#### 全球降水带 (ITCZ) 移动")
                    fig, ax = plt.subplots(figsize=(6, 3))
                    plot_rain_belt(ax, st.session_state.month)
                    st.pyplot(fig)
                    plt.close(fig)
    else:
        st.info("请在侧边栏开启至少一个显示选项。")

    # ---- 第三行: 气候带联动 ----
    if st.session_state.show_climate:
        st.divider()
        st.subheader("三、全球气候带与气压带联动")

        climate_names_cn = [
            "热带雨林气候", "热带草原气候", "热带沙漠气候",
            "地中海气候", "温带海洋性气候", "温带季风气候",
            "温带大陆性气候", "亚寒带针叶林气候", "极地气候",
        ]

        highlight = st.selectbox(
            "选择气候带查看详细信息 (选择「无」可浏览全局)",
            ["无"] + climate_names_cn,
            key="climate_selector",
        )
        st.session_state.highlight_climate = (
            None if highlight == "无" else highlight
        )

        col_cz_left, col_cz_right = st.columns([2, 1])

        with col_cz_left:
            fig, ax = plt.subplots(figsize=(7, 6))
            plot_climate_zones(
                ax,
                st.session_state.month,
                st.session_state.shift_amplitude,
                st.session_state.highlight_climate,
            )
            st.pyplot(fig)
            plt.close(fig)

        with col_cz_right:
            if st.session_state.highlight_climate:
                zone = get_climate_zone_detail(st.session_state.highlight_climate)
                if zone:
                    st.markdown("#### 气候带详情")
                    st.markdown(render_climate_detail(zone), unsafe_allow_html=True)
            else:
                st.markdown("#### 使用提示")
                st.markdown("""
                <div class="glass-card" style="font-size:13px; line-height:1.6;">
                <p style="color:#1d1d1f; font-weight:600;">选择气候带即可查看：</p>
                <ul style="color:#86868b; padding-left:18px;">
                    <li>形成原因</li>
                    <li>典型分布地区</li>
                    <li>降水特点</li>
                    <li>气温特点</li>
                </ul>
                <p style="color:#aeaeb2; font-size:12px;">左侧图中被选中的气候带会高亮显示。</p>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# 考试模式
# ============================================================
def render_exam_mode():
    """渲染考试模式界面 — Apple 风格"""
    st.divider()
    st.subheader("考试模式")

    if not st.session_state.exam_submitted:
        st.markdown("""
        <div class="glass-card" style="font-size:13px; line-height:1.6; margin-bottom:1.25rem; border-left:3px solid var(--accent);">
            <b style="color:#1d1d1f;">考试说明：</b>
            系统随机选择月份，请根据已学知识判断
            气压带位置、风带方向、季风状态和雨带位置。
            每题只有一个正确答案。
        </div>
        """, unsafe_allow_html=True)

        questions = st.session_state.exam_questions
        for i, q in enumerate(questions):
            month_int = int(round(q.month))
            season = get_season_name(q.month)
            decl = get_solar_declination(q.month)
            decl_str = f"{abs(decl):.1f}" + ("°N" if decl >= 0 else "°S")

            st.markdown(f"""
            <div style="
                background: var(--bg-glass);
                backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
                padding: 12px 16px;
                border-radius: var(--radius-sm);
                border: 0.5px solid var(--border);
                margin-bottom: 0.5rem;
            ">
                <b style="color:#1d1d1f;">第 {i+1} 题</b>
                <span style="color:#86868b;"> &middot; {month_int}月 ({season}) &middot; 直射 {decl_str}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**{q.question_text}**")

            answer = st.radio(
                f"第 {i+1} 题答案",
                options=list(range(len(q.options))),
                format_func=lambda x, q=q: f"{chr(65+x)}. {q.options[x]}",
                key=f"exam_q_{i}",
                index=None,
            )
            if answer is not None:
                st.session_state.exam_answers[i] = answer

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("提交答卷", use_container_width=True, type="primary"):
                if -1 in st.session_state.exam_answers:
                    st.error("请完成所有题目后再提交！")
                else:
                    st.session_state.exam_submitted = True
                    st.rerun()
        with col_btn2:
            if st.button("重新出题", use_container_width=True):
                st.session_state.exam_questions = generate_questions(4)
                st.session_state.exam_answers = [-1] * 4
                st.rerun()

    else:
        questions = st.session_state.exam_questions
        answers = st.session_state.exam_answers
        score, total, feedback = grade_exam(questions, answers)

        percentage = score / total * 100
        grade_color = (
            "var(--success)" if percentage >= 80 else
            "var(--warning)" if percentage >= 60 else
            "var(--danger)"
        )
        grade_text = (
            "优秀" if percentage >= 80 else
            "良好" if percentage >= 60 else
            "需要加强"
        )

        st.markdown(f"""
        <div class="exam-score" style="margin-bottom:1.5rem;">
            <div class="score-num" style="color:{grade_color};">{score}/{total}</div>
            <div style="font-size:14px; color:#86868b; margin-top:4px;">{grade_text} ({percentage:.0f}%)</div>
        </div>
        """, unsafe_allow_html=True)

        for i, fb in enumerate(feedback):
            is_ok = fb["is_correct"]
            marker = "[OK]" if is_ok else "[X]"
            css_class = "exam-correct" if is_ok else "exam-wrong"
            color = "#34c759" if is_ok else "#ff3b30"

            correct_info = (
                "" if is_ok
                else f" | 正确答案: {fb['correct_answer']}"
            )
            st.markdown(f"""
            <div class="{css_class}">
                <b style="color:{color};">{marker} 第{i+1}题:</b> {fb['question']}<br>
                <span style="color:{color}; font-size:13px;">
                    你的答案: {fb['user_answer']}{correct_info}
                </span><br>
                <small style="color:#aeaeb2;">{fb['explanation']}</small>
            </div>
            """, unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("重新出题", use_container_width=True):
                st.session_state.exam_questions = generate_questions(4)
                st.session_state.exam_answers = [-1] * 4
                st.session_state.exam_submitted = False
                st.rerun()
        with col_r2:
            if st.button("退出考试模式", use_container_width=True):
                st.session_state.exam_active = False
                st.session_state.exam_submitted = False
                st.rerun()


# ============================================================
# 知识点面板
# ============================================================
def render_knowledge_panel():
    """渲染知识总结面板 (可折叠) — 毛玻璃风格"""
    with st.expander("知识点总结 (点击展开)", expanded=False):
        month = st.session_state.month
        decl = get_solar_declination(month)
        season = get_season_name(month)
        shift = st.session_state.shift_amplitude

        tab1, tab2, tab3, tab4 = st.tabs([
            "气压带风带", "三圈环流", "东亚季风", "降水与气候"
        ])

        with tab1:
            st.markdown(f"""
            ### 气压带与风带 — 当前状态 ({get_month_name(month)})

            **气压带分布 (基准 ± 季节移动 {shift}°):**

            | 气压带 | 基准纬度 | 当前纬度 (估算) | 类型 |
            |--------|---------|----------------|------|
            | 赤道低压带 (ITCZ) | 0° | {decl*1.0:.1f}° | 低压 (热力) |
            | 副热带高压带 (NH) | 30°N | {30+decl*0.8:.0f}°N | 高压 (动力) |
            | 副极地低压带 (NH) | 60°N | {60+decl*0.5:.0f}°N | 低压 (动力) |
            | 极地高压带 (NH) | 90°N | ~90°N | 高压 (热力) |

            **风带风向:**
            - 低纬度: 东北信风 (NH) / 东南信风 (SH)
            - 中纬度: 盛行西风 (SW 在 NH, NW 在 SH)
            - 高纬度: 极地东风

            **季节效应:** 北半球{season}，所有气压带/风带整体向{'北' if decl > 0 else '南'}偏移约 {abs(decl)*0.8:.1f}°。
            """)

        with tab2:
            st.markdown(f"""
            ### 三圈环流 — 当前状态 ({get_month_name(month)})

            **哈德莱环流 (Hadley Cell) | 0° ~ {30+decl*0.8:.0f}°:**
            - 热力直接环流 (低纬度)
            - 赤道受热上升 → 高空向极地输送 → 副热带下沉 → 近地面向赤道回流
            - 形成信风带和副热带无风带

            **费雷尔环流 (Ferrel Cell) | {30+decl*0.8:.0f}° ~ {60+decl*0.5:.0f}°:**
            - 间接环流 (中纬度, 由两侧环流带动)
            - 副热带高空向极地 → 副极地上升 → 高空向赤道 → 副热带下沉
            - 形成盛行西风带

            **极地环流 (Polar Cell) | {60+decl*0.5:.0f}° ~ 90°:**
            - 热力直接环流 (高纬度)
            - 极地冷却下沉 → 近地面向赤道 → 副极地上升 → 高空向极地
            - 形成极地东风带

            **关键记忆:**
            - 上升气流 = 低压 = 多云雨
            - 下沉气流 = 高压 = 晴朗
            - 赤道低压和极地高压是**热力**成因
            - 副热带高压和副极地低压是**动力**成因
            """)

        with tab3:
            st.markdown(f"""
            ### 东亚季风 — 当前状态 ({get_month_name(month)})

            **形成原因:** 海陆热力性质差异

            亚洲大陆 (世界最大大陆) 与 太平洋 (世界最大大洋) 之间的温度差:

            **夏季 ({3}-{8}月):**
            - 大陆升温快 → 形成亚洲低压 (热低压)
            - 海洋升温慢 → 太平洋高压 (副热带高压)
            - 风从海洋吹向大陆 → **东南季风**
            - 带来丰沛降水 (中国东部雨季)

            **冬季 ({9}-{2}月):**
            - 大陆降温快 → 形成亚洲高压 (冷高压, 西伯利亚高压)
            - 海洋降温慢 → 太平洋低压 (阿留申低压)
            - 风从大陆吹向海洋 → **西北季风**
            - 寒冷干燥 (中国北方寒潮)

            **当前状态:** 北半球{season}，
            {'大陆形成热低压，东南季风盛行' if decl > 5 else '大陆形成冷高压，西北季风盛行' if decl < -5 else '处于季风过渡期'}
            """)

        with tab4:
            st.markdown(f"""
            ### 降水带与气候 — 当前状态 ({get_month_name(month)})

            **ITCZ 降水带:**
            - 跟随太阳直射点移动，约有 1 个月滞后
            - {month:.0f}月: 雨带大致位于 {abs(decl)*0.9:.1f}°{'N' if decl > 0 else 'S'} 附近
            - 北半球夏季雨带最北可达 20-25°N

            **主要气候类型与气压带风带关系:**

            | 气候类型 | 控制因素 | 降水特征 |
            |---------|---------|---------|
            | 热带雨林 | 全年赤道低压 | 全年多雨 |
            | 热带草原 | 赤道低压+信风交替 | 干湿季分明 |
            | 热带沙漠 | 全年副高+信风 | 终年干燥 |
            | 地中海 | 副高(夏)+西风(冬) | 冬雨夏干 |
            | 温带海洋 | 全年西风 | 全年均匀 |
            | 温带季风 | 海陆热力差异 | 夏雨冬干 |

            **当前受影响最显著区域:** {'北半球热带/亚热带地区' if decl > 5 else '南半球热带地区' if decl < -5 else '赤道附近'}
            """)


# ============================================================
# 主函数
# ============================================================
def main():
    """主应用入口"""

    # 渲染侧边栏
    render_sidebar()

    # 处理动画
    handle_animation()

    # 渲染标题栏
    render_header()

    # 根据模式渲染内容
    if st.session_state.exam_active:
        render_exam_mode()
    else:
        render_main_visualizations()
        render_knowledge_panel()

    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align:center; color:#aeaeb2; font-size:12px; letter-spacing:-0.1px;'>"
        "全球大气环流与东亚季风模拟器 v1.0 &middot; "
        "高中地理教学可视化工具 &middot; "
        "基于大气环流经典理论，仅供教学演示参考 &middot; "
        "2025 Educational Use"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

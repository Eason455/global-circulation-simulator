"""
全球气压带风带季节移动与东亚季风形成交互模拟器
==========================================
面向高中地理学习的动态可视化教学工具.

架构: app.py (页面编排) -> ui/ (侧边栏/标题/面板/考试) -> modules/ (可视化) -> utils/ (物理模型)

运行: streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import time
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
# 加载 CSS
# ============================================================
def load_css():
    """从 assets/style.css 加载 Apple Design System 样式"""
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("style.css not found — UI may not render correctly.")

load_css()

# ============================================================
# 导入 UI 组件
# ============================================================
from ui.sidebar import render_sidebar
from ui.header import render_header
from ui.panels import render_main_visualizations, render_knowledge_panel
from ui.exam import render_exam_mode

# ============================================================
# 会话状态初始化
# ============================================================
def init_session_state():
    """初始化 Streamlit 会话状态变量"""
    defaults = {
        "anim_speed": "normal",
        "shift_amplitude": 10,
        "show_solar": True,
        "show_circulation": True,
        "show_wind": True,
        "show_monsoon": True,
        "show_rain": True,
        "show_climate": True,
        "highlight_climate": None,
        "animating": False,
        "exam_active": False,
        "exam_questions": [],
        "exam_answers": [],
        "exam_submitted": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    # month 的初始值在 handle_animation 首次调用时设定

init_session_state()

# ============================================================
# 动画循环
# ============================================================
def handle_animation():
    """自动推进月份 (支持慢速/正常/快速).
    必须在 render_sidebar() 之前调用, 以确保写入 st.session_state.month
    时 slider widget (key='month') 尚未渲染. """
    # 首次运行时 slider 尚未渲染, 设定默认值
    if "month" not in st.session_state:
        st.session_state.month = 7.0

    if st.session_state.animating:
        speeds = {"slow": 0.05, "normal": 0.12, "fast": 0.3}
        step = speeds.get(st.session_state.anim_speed, 0.12)

        new_month = st.session_state.month + step
        if new_month > 13:
            new_month -= 12
        st.session_state.month = new_month

        time.sleep(0.3)
        st.rerun()

# ============================================================
# 页脚
# ============================================================
def render_footer():
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

# ============================================================
# 主入口
# ============================================================
def main():
    handle_animation()
    render_sidebar()
    render_header()

    if st.session_state.exam_active:
        render_exam_mode()
    else:
        render_main_visualizations()
        render_knowledge_panel()

    render_footer()

if __name__ == "__main__":
    main()

"""
全球气压带风带季节移动与东亚季风形成交互模拟器
==========================================
面向高中地理学习的动态可视化教学工具.

架构: app.py (页面编排) -> ui/ (侧边栏/标题/面板/考试) -> modules/ (可视化) -> utils/ (物理模型)

运行: streamlit run app.py

动画方案: st.empty() 占位符 + while 循环,
每帧更新图表, 自动推进月份, 不受 st.rerun() 丢弃输出的限制.
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
# CSS 加载 — 多重回退策略
# ============================================================
def load_css():
    """加载 Apple Design System 样式, 多重回退确保文件找到."""
    css_content = None

    # 策略1: __file__ 相对路径
    try:
        css_path = Path(__file__).resolve().parent / "assets" / "style.css"
        if css_path.exists():
            css_content = css_path.read_text(encoding="utf-8")
    except Exception:
        pass

    # 策略2: sys.argv[0] 相对路径
    if css_content is None:
        try:
            script_dir = Path(sys.argv[0]).resolve().parent
            css_path = script_dir / "assets" / "style.css"
            if css_path.exists():
                css_content = css_path.read_text(encoding="utf-8")
        except Exception:
            pass

    # 策略3: 硬编码绝对路径
    if css_content is None:
        hard_path = Path(r"Z:\global-circulation-simulator\assets\style.css")
        if hard_path.exists():
            css_content = hard_path.read_text(encoding="utf-8")

    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
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
        "month": 7.0,
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

init_session_state()

# ============================================================
# 动画循环 — 使用 st.empty() 占位符
# ============================================================
def run_animation():
    """
    在 st.empty() 占位符中循环渲染可视化面板,
    每帧推进月份, 实现流畅动画.

    这是 Streamlit 中动画的唯一可靠方案:
    - 不使用 st.rerun() (那会丢弃渲染输出)
    - 不使用 JS URL 导航 (浏览器闪烁, 速度不可控)
    - while 循环内直接更新占位符, 浏览器实时接收帧

    限制: 循环期间侧边栏控件不响应 (Streamlit 同步特性).
    动画自动运行约 20 秒后停止, 或点击"停止"后等待当前帧结束.
    """
    speeds = {"slow": 0.05, "normal": 0.15, "fast": 0.35}
    delays = {"slow": 0.6, "normal": 0.3, "fast": 0.1}

    step = speeds.get(st.session_state.anim_speed, 0.15)
    delay = delays.get(st.session_state.anim_speed, 0.3)

    # 最大帧数: 覆盖约 12 个月 (一次完整年循环)
    max_frames = int(12 / step) + 5

    ph = st.empty()

    for frame in range(max_frames):
        if not st.session_state.animating:
            break

        # 渲染当前帧到占位符
        with ph.container():
            render_main_visualizations()
            render_knowledge_panel()

        # 等前端渲染
        time.sleep(delay)

        # 推进月份 (模运算回绕, 避免边界漂移)
        st.session_state.month = ((st.session_state.month - 1 + step) % 12) + 1

    # 动画结束
    st.session_state.animating = False

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
    render_sidebar()
    render_header()

    if st.session_state.animating:
        run_animation()
    elif st.session_state.exam_active:
        render_exam_mode()
    else:
        render_main_visualizations()
        render_knowledge_panel()

    render_footer()

if __name__ == "__main__":
    main()

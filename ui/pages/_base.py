"""
模块页面共享基础设施
===================
- render_animation_button(): 播放 + 停止按钮对
- fig_to_html_img(): matplotlib Figure → base64 <img> 标签
- run_single_chart_animation(): 单图动画循环 (st.empty + base64 img, 零闪烁)
"""

import time
import io
import base64
import streamlit as st
import matplotlib.pyplot as plt


def render_animation_button(label: str = "播放动画") -> bool:
    """渲染播放/停止按钮对, 返回是否刚按下播放."""
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(label, use_container_width=True, type="primary",
                     key=f"play_{label}"):
            st.session_state.animating = True
            return True
    with col_b:
        if st.button("停止", use_container_width=True):
            st.session_state.animating = False
            st.rerun()
    return False


def fig_to_html_img(fig, dpi=100) -> str:
    """matplotlib Figure → <img src='data:image/png;base64,...'> 字符串."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return f'<img src="data:image/png;base64,{b64}" style="width:100%;max-width:800px;border-radius:12px;display:block;margin:0 auto;" />'


def run_single_chart_animation(plot_fn, figsize=(6, 5), plot_kwargs=None, container=None):
    """
    单个图表的动画循环.

    使用 st.empty() 占位符 + 单个 base64 <img> 替换 —— 零闪烁.
    自动从 st.session_state 读取 month / anim_speed, 推进月份.

    Args:
        plot_fn: callable(ax, month, **plot_kwargs) — 模块的 plot 函数
        figsize: matplotlib figure size
        plot_kwargs: 传给 plot_fn 的额外关键字参数 (如 shift_amplitude)
        container: Streamlit 容器 (默认创建 st.empty())
    """
    speeds = {"slow": 0.003, "normal": 0.008, "fast": 0.020}
    delays = {"slow": 0.016, "normal": 0.016, "fast": 0.016}
    # 60fps target; actual fps limited by matplotlib render speed
    step = speeds.get(st.session_state.anim_speed, 0.15)
    delay = delays.get(st.session_state.anim_speed, 0.3)
    max_frames = int(12 / step) + 5

    if plot_kwargs is None:
        plot_kwargs = {}
    if container is None:
        container = st.empty()

    try:
        for _ in range(max_frames):
            if not st.session_state.animating:
                break
            month = st.session_state.month
            fig, ax = plt.subplots(figsize=figsize)
            plot_fn(ax, month, **plot_kwargs)
            img_html = fig_to_html_img(fig)
            container.markdown(img_html, unsafe_allow_html=True)
            time.sleep(delay)
            st.session_state.month = ((month - 1 + step) % 12) + 1
    finally:
        st.session_state.animating = False

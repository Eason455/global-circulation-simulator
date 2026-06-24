"""
模块页面共享基础设施
===================
- render_animation_button(): 播放 + 停止按钮对
- run_single_chart_animation(): 单图动画 (st.pyplot + st.rerun, 与静态图同渲染路径)
"""

import time
import streamlit as st
import matplotlib.pyplot as plt


def render_animation_button():
    """渲染播放/停止按钮对."""
    col_a, col_b = st.columns(2)
    with col_a:
        st.button("播放动画", use_container_width=True, type="primary",
                  key="btn_play", on_click=lambda: setattr(st.session_state, "animating", True))
    with col_b:
        st.button("停止", use_container_width=True,
                  key="btn_stop", on_click=_stop_animation)


def _stop_animation():
    st.session_state.animating = False


def run_single_chart_animation(plot_fn, figsize=(6, 5), plot_kwargs=None):
    """
    单图表动画 — 使用 st.pyplot() + st.rerun().

    与静态图使用完全相同的渲染路径 (st.pyplot), 因此:
    - 图表尺寸不变 (无跳变)
    - 利用 Streamlit 原生图像渲染 (比 base64 快)
    - 单图表场景下 st.rerun() 可靠, 每帧完整渲染一个图表

    Args:
        plot_fn: callable(ax, month, **plot_kwargs) — 模块的 plot 函数
        figsize: matplotlib figure size (须与静态图一致)
        plot_kwargs: 额外关键字参数 (如 shift_amplitude)
    """
    speeds = {"slow": 0.003, "normal": 0.008, "fast": 0.020}
    delays = {"slow": 0.07, "normal": 0.04, "fast": 0.02}

    step = speeds.get(st.session_state.anim_speed, 0.008)
    delay = delays.get(st.session_state.anim_speed, 0.04)

    if plot_kwargs is None:
        plot_kwargs = {}

    # 推进月份
    st.session_state.month += step
    if st.session_state.month > 13:
        st.session_state.month -= 12

    # 渲染图表 — 与静态视图使用完全相同的 st.pyplot()
    fig, ax = plt.subplots(figsize=figsize)
    plot_fn(ax, st.session_state.month, **plot_kwargs)
    st.pyplot(fig)
    plt.close(fig)

    # 延迟后触发下一帧
    time.sleep(delay)
    st.rerun()

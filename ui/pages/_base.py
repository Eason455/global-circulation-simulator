"""
模块页面共享基础设施
===================
- render_animation_button(): 播放 + 停止按钮对
  (动画循环由 app.py 的 main() 统一驱动, 页面函数只负责渲染)
"""

import streamlit as st


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
    st.rerun()

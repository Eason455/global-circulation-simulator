"""
页面标题栏
========
Apple 风格, 左侧标题 + 右侧月份玻璃卡片.
"""

import streamlit as st
from utils.physics import get_solar_declination, get_month_name, get_season_name


def render_header() -> None:
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

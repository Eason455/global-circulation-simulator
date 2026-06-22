"""
侧边栏控制面板
============
Apple 毛玻璃风格, 包含月份/动画/幅度/显示/考试所有控制项.
动画播放时滑块替换为进度指示器, 避免 Streamlit widget key 写入限制.
"""

import streamlit as st
from utils.physics import get_solar_declination, get_month_name, get_season_name
from modules.exam_mode import generate_questions


def render_sidebar() -> None:
    """渲染侧边栏控制面板 — Apple 毛玻璃风格"""
    with st.sidebar:
        st.markdown(
            '<div style="font-size:18px;font-weight:700;letter-spacing:-0.3px;color:#1d1d1f;">'
            '控制面板</div>',
            unsafe_allow_html=True,
        )
        st.caption("全球大气环流模拟器")

        # ---- 月份选择 ----
        st.markdown("##### 月份选择")

        if st.session_state.animating:
            # 动画播放中: 显示当前月份进度条, 不显示滑块
            _render_animating_month_display()
        else:
            # 手动模式: 显示滑块
            _render_month_slider()

        # 当前月份信息卡片
        month = st.session_state.month
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


def _render_month_slider():
    """手动模式: 显示月份滑块, 用户自由拖动."""
    month = st.slider(
        "拖动选择月份",
        min_value=0.1,
        max_value=12.9,
        step=0.1,
        format="%.1f",
        key="month_slider",
    )
    st.session_state.month = month


def _render_animating_month_display():
    """动画模式: 显示当前月份进度条, 不显示滑块."""
    month = st.session_state.month
    month_name = get_month_name(month)
    decl = get_solar_declination(month)

    st.markdown(f"""
    <div style="
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: var(--radius);
        border: 0.5px solid var(--border);
        padding: 16px;
        text-align: center;
        margin-bottom: 8px;
    ">
        <div style="font-size:24px; font-weight:700; color:var(--accent);">{month_name}</div>
        <div style="font-size:13px; color:var(--text-secondary);">
            {abs(decl):.1f}°{' N' if decl >= 0 else ' S'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 月份进度条 — 使用 0.1~12.9 范围映射到 0~1
    raw = (month - 1) / 11
    if raw < 0.0:
        progress = 0.0
    elif raw > 1.0:
        progress = 1.0
    else:
        progress = raw
    st.progress(float(progress))
    st.caption(f"全年进度 · {((month - 1) / 11 * 100):.0f}%")

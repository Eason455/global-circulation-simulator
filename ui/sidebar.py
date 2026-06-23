"""
侧边栏控制面板 — 子页面导航架构
=============================
Radio 选择模块页面 + 全局控制 (月份/速度/幅度).
"""
import streamlit as st
from utils.physics import get_solar_declination, get_month_name, get_season_name
from modules.exam_mode import generate_questions

PAGES = [
    "太阳直射点周年运动",
    "气压带与风带分布",
    "三圈环流",
    "东亚季风形成模拟",
    "全球降水带移动",
    "全球气候带分布",
    "考试模式",
]


def render_sidebar() -> str:
    """渲染侧边栏; 返回当前选中的页面名称."""
    with st.sidebar:
        st.markdown(
            '<div style="font-size:18px;font-weight:700;letter-spacing:-0.3px;color:#1d1d1f;">'
            '全球大气环流模拟器</div>',
            unsafe_allow_html=True,
        )
        st.caption("高中地理教学可视化工具")

        st.divider()

        # ---- 模块导航 ----
        st.markdown("##### 模块导航")

        # 找到当前页面在列表中的索引
        current_idx = _get_current_page_index()

        page = st.radio(
            "选择模块",
            options=PAGES,
            index=current_idx,
            label_visibility="collapsed",
            key="page_selector",
        )

        # 考试模式自动激活/停用
        if page == "考试模式" and not st.session_state.exam_active:
            st.session_state.exam_active = True
            st.session_state.exam_questions = generate_questions(4)
            st.session_state.exam_answers = [-1] * 4
            st.session_state.exam_submitted = False
            st.rerun()
        elif page != "考试模式" and st.session_state.exam_active:
            st.session_state.exam_active = False
            st.session_state.exam_submitted = False

        st.divider()

        # ---- 全局控制 ----
        st.markdown("##### 全局控制")

        # 月份
        if st.session_state.animating:
            _render_animating_month_display()
        else:
            _render_month_slider()

        # 月份信息卡片
        month = st.session_state.month
        decl = get_solar_declination(month)
        decl_str = f"{abs(decl):.1f}" + ("°N" if decl >= 0 else "°S")
        season = get_season_name(month)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("月份", get_month_name(month))
        with col2:
            st.metric("季节", season)
        with col3:
            st.metric("直射纬度", decl_str)

        st.divider()

        # ---- 动画设置 ----
        st.markdown("##### 动画设置")
        anim_speed = st.select_slider(
            "速度",
            options=["slow", "normal", "fast"],
            value=st.session_state.anim_speed,
            format_func=lambda x: {"slow": "慢速", "normal": "正常", "fast": "快速"}[x],
            key="anim_speed_select",
        )
        st.session_state.anim_speed = anim_speed

        st.divider()

        # ---- 移动幅度 ----
        st.markdown("##### 移动幅度")
        shift = st.radio(
            "气压带/风带季节移动幅度",
            options=[5, 10, 15],
            index=1,
            format_func=lambda x: "±" + str(x) + "°",
            horizontal=True,
            key="shift_radio",
        )
        st.session_state.shift_amplitude = shift

        st.divider()

        # ---- 图例 ----
        st.markdown("##### 图例说明")
        st.markdown("""
        <div style="font-size:12px; color:#86868b; line-height:1.7;">
        <span style="color:#00b894;">L</span> = 低压 (上升, 多云雨)<br>
        <span style="color:#e17055;">H</span> = 高压 (下沉, 晴燥)<br>
        <span style="color:#d63031;">红</span> = 上升 &nbsp; <span style="color:#0984e3;">蓝</span> = 下沉<br>
        <span style="color:#86868b;">ITCZ/STH/SPL/PHP</span>
        </div>
        """, unsafe_allow_html=True)

    return page


def _get_current_page_index() -> int:
    """根据当前状态推断应该在导航中显示的页面索引."""
    if st.session_state.get("exam_active"):
        return 6  # 考试模式
    # 尝试从之前的 page_selector 读取
    prev = st.session_state.get("page_selector")
    if prev in PAGES and prev != "考试模式":
        return PAGES.index(prev)
    return 0


def _render_month_slider():
    """手动模式: 月份滑块."""
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
    """动画模式: 月份进度条 (只读)."""
    month = st.session_state.month
    month_name = get_month_name(month)
    decl = get_solar_declination(month)

    st.markdown(f"""
    <div style="
        background: var(--bg-glass, rgba(255,255,255,0.64));
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 18px;
        border: 0.5px solid var(--border, rgba(60,60,67,0.12));
        padding: 16px;
        text-align: center;
        margin-bottom: 8px;
    ">
        <div style="font-size:24px; font-weight:700; color:var(--accent, #0071e3);">{month_name}</div>
        <div style="font-size:13px; color:var(--text-secondary, #86868b);">
            {abs(decl):.1f}°{' N' if decl >= 0 else ' S'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    raw = (month - 1) / 11
    if raw < 0.0:
        progress = 0.0
    elif raw > 1.0:
        progress = 1.0
    else:
        progress = raw
    st.progress(float(progress))
    st.caption(f"全年进度 · {((month - 1) / 11 * 100):.0f}%")

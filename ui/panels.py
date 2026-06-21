"""
主可视化面板 & 知识点面板
======================
布局: 上排 (全球环流) / 中排 (季风+降水) / 下排 (气候带联动) + 可折叠知识面板.
"""

import streamlit as st
import matplotlib.pyplot as plt

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
from utils.physics import get_solar_declination, get_month_name, get_season_name, get_monsoon_season


def render_main_visualizations() -> None:
    """渲染三行可视化面板"""

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
                    _render_solar_panel()
                elif panel == "wind":
                    _render_wind_panel()
                elif panel == "circulation":
                    _render_circulation_panel()
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
                    _render_monsoon_panel()
                elif panel == "rain":
                    _render_rain_panel()
    else:
        st.info("请在侧边栏开启至少一个显示选项。")

    # ---- 第三行: 气候带联动 ----
    if st.session_state.show_climate:
        _render_climate_panel()


def render_knowledge_panel() -> None:
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
            from utils.physics import get_monsoon_state
            monsoon = get_monsoon_state(month)
            ms = monsoon["season"]
            current_desc = {
                "summer": "大陆形成热低压，东南季风盛行",
                "winter": "大陆形成冷高压，西北季风盛行",
                "transition": "处于季风过渡期，风向多变",
            }.get(ms, "处于季风过渡期")

            st.markdown(f"""
            ### 东亚季风 — 当前状态 ({get_month_name(month)})

            **形成原因:** 海陆热力性质差异

            亚洲大陆 (世界最大大陆) 与 太平洋 (世界最大大洋) 之间的温度差:

            **夏季 (5~9月):**
            - 大陆升温快 → 形成亚洲低压 (热低压)
            - 海洋升温慢 → 太平洋高压 (副热带高压)
            - 风从海洋吹向大陆 → **东南季风**
            - 带来丰沛降水 (中国东部雨季)

            **冬季 (11~次年2月):**
            - 大陆降温快 → 形成亚洲高压 (冷高压, 西伯利亚高压)
            - 海洋降温慢 → 太平洋低压 (阿留申低压)
            - 风从大陆吹向海洋 → **西北季风**
            - 寒冷干燥 (中国北方寒潮)

            **过渡期 (3~4月, 10月):**
            - 海陆热力差异减弱
            - 季风较弱，风向多变

            **当前状态:** 北半球{season}，{current_desc}
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


# ---- 行内辅助渲染函数 ----

def _render_solar_panel() -> None:
    st.markdown("#### 太阳直射点周年运动")
    fig, ax = plt.subplots(figsize=(5, 4.5))
    plot_solar_declination(ax, st.session_state.month)
    st.pyplot(fig)
    plt.close(fig)


def _render_wind_panel() -> None:
    st.markdown("#### 气压带与风带分布")
    fig, ax = plt.subplots(figsize=(5, 5.5))
    plot_pressure_wind_belts(
        ax,
        st.session_state.month,
        st.session_state.shift_amplitude,
    )
    st.pyplot(fig)
    plt.close(fig)


def _render_circulation_panel() -> None:
    st.markdown("#### 三圈环流")
    fig, ax = plt.subplots(figsize=(6, 4.5))
    plot_three_cell_circulation(
        ax,
        st.session_state.month,
        st.session_state.shift_amplitude,
    )
    st.pyplot(fig)
    plt.close(fig)


def _render_monsoon_panel() -> None:
    st.markdown("#### 东亚季风形成模拟")
    fig, ax = plt.subplots(figsize=(5.5, 5))
    plot_east_asian_monsoon(ax, st.session_state.month)
    st.pyplot(fig)
    plt.close(fig)


def _render_rain_panel() -> None:
    st.markdown("#### 全球降水带 (ITCZ) 移动")
    fig, ax = plt.subplots(figsize=(6, 3))
    plot_rain_belt(ax, st.session_state.month)
    st.pyplot(fig)
    plt.close(fig)


def _render_climate_panel() -> None:
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

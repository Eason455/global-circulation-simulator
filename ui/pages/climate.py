"""
全球气候带分布 — 子页面
=======================
9 个气候带色块 + 气压带联动, 支持选择气候带查看详情.
"""
import streamlit as st
import matplotlib.pyplot as plt
from modules.climate_zones import (
    plot_climate_zones,
    get_climate_zone_detail,
    render_climate_detail,
)
from utils.physics import get_solar_declination, get_month_name, get_season_name
from ui.pages._base import render_animation_button


def render_climate_page():
    st.subheader("全球气候带分布")

    climate_names_cn = [
        "热带雨林气候", "热带草原气候", "热带沙漠气候",
        "地中海气候", "温带海洋性气候", "温带季风气候",
        "温带大陆性气候", "亚寒带针叶林气候", "极地气候",
    ]

    highlight = st.selectbox(
        "选择气候带查看详细信息 (选择「无」浏览全局)",
        ["无"] + climate_names_cn,
        key="climate_page_selector",
    )
    highlight_zone = None if highlight == "无" else highlight

    render_animation_button()

    amp = st.session_state.shift_amplitude
    month = st.session_state.month

    col_left, col_right = st.columns([2, 1])
    with col_left:
        fig, ax = plt.subplots(figsize=(8, 7))
        plot_climate_zones(ax, month, amp, highlight_zone)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with col_right:
        if highlight_zone:
            zone = get_climate_zone_detail(highlight_zone)
            if zone:
                st.markdown("#### 气候带详情")
                st.markdown(render_climate_detail(zone), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="font-size:13px; line-height:1.6;">
            <p style="color:#1d1d1f; font-weight:600;">选择气候带即可查看：</p>
            <ul style="color:#86868b; padding-left:18px;">
                <li>形成原因</li>
                <li>典型分布地区</li>
                <li>降水特点</li>
                <li>气温特点</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

    decl = get_solar_declination(month)
    season = get_season_name(month)

    with st.expander("知识点 — 气候带与气压带风带关系", expanded=False):
        st.markdown(f"""
### 气候带 — {get_month_name(month)}

**气候形成的核心逻辑:** 气候带分布主要由**气压带和风带**的位置决定。

| 气候类型 | 控制因素 | 降水特征 |
|---------|---------|---------|
| 热带雨林 | 全年赤道低压 | 全年多雨 |
| 热带草原 | 赤道低压+信风交替 | 干湿季分明 |
| 热带沙漠 | 全年副高+信风 | 终年干燥 |
| 地中海 | 副高(夏)+西风(冬) | 冬雨夏干 |
| 温带海洋 | 全年西风 | 全年均匀 |
| 温带季风 | 海陆热力差异 | 夏雨冬干 |
| 温带大陆性 | 深居内陆 | 全年干燥 |
| 亚寒带针叶林 | 纬度高, 受极地气团影响 | 少量夏季降水 |
| 极地气候 | 全年极地高压 | 终年少雪 |

**当前受影响最显著区域:** {'北半球热带/亚热带' if decl > 5 else '南半球热带' if decl < -5 else '赤道附近'}

**学习提示:** 结合气压带风带图一起看，注意气候带边界随气压带季节移动而变化。
""")

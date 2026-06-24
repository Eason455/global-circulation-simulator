"""
太阳直射点周年运动 — 子页面
===========================
地球剖面图: 太阳直射点位置 + 回归线 + 赤道.
"""
import streamlit as st
import matplotlib.pyplot as plt
from modules.solar_declination import plot_solar_declination
from utils.physics import get_solar_declination, get_month_name, get_season_name
from ui.pages._base import render_animation_button, run_single_chart_animation


def render_solar_page():
    st.subheader("太阳直射点周年运动")

    render_animation_button()

    if st.session_state.animating:
        run_single_chart_animation(
            plot_fn=plot_solar_declination,
            figsize=(5.5, 5),
        )
    else:
        fig, ax = plt.subplots(figsize=(5.5, 5))
        plot_solar_declination(ax, st.session_state.month)
        st.pyplot(fig)
        plt.close(fig)

    # 知识点
    month = st.session_state.month
    decl = get_solar_declination(month)
    decl_str = f"{abs(decl):.1f}" + ("°N" if decl >= 0 else "°S")
    season = get_season_name(month)

    with st.expander("知识点 — 太阳直射点回归运动", expanded=False):
        st.markdown(f"""
### 当前状态 ({get_month_name(month)})

- **太阳直射纬度:** {decl_str}
- **北半球季节:** {season}

### 回归运动规律

太阳直射点在南北回归线之间有规律地往返移动，根本原因是**黄赤交角**（约 23.5°）。

| 节气 | 日期 (约) | 直射纬度 |
|------|----------|---------|
| 春分 | 3月21日 | 赤道 (0°) |
| 夏至 | 6月22日 | 北回归线 (23.5°N) |
| 秋分 | 9月23日 | 赤道 (0°) |
| 冬至 | 12月22日 | 南回归线 (23.5°S) |

### 地理意义

太阳直射点的回归运动是以下现象的根本原因:
- 昼夜长短的季节变化
- 正午太阳高度的季节变化
- 四季更替
- 气压带和风带的季节移动
- 季风环流的形成与变化

### 周期

一个回归年约为 **365.2422天** (365天5时48分46秒)。
""")

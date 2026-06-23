"""
东亚季风形成模拟 — 子页面
=========================
亚洲大陆-太平洋简化地图: 东南季风 (夏) / 西北季风 (冬).
"""
import streamlit as st
import matplotlib.pyplot as plt
from modules.east_asian_monsoon import plot_east_asian_monsoon
from utils.physics import get_solar_declination, get_month_name, get_season_name
from utils.physics import get_monsoon_state
from ui.pages._base import render_animation_button, run_single_chart_animation


def render_monsoon_page():
    st.subheader("东亚季风形成模拟")

    render_animation_button("播放动画")

    if st.session_state.animating:
        run_single_chart_animation(
            plot_fn=plot_east_asian_monsoon,
            figsize=(6, 5.5),
        )
    else:
        fig, ax = plt.subplots(figsize=(6, 5.5))
        plot_east_asian_monsoon(ax, st.session_state.month)
        st.pyplot(fig)
        plt.close(fig)

    month = st.session_state.month
    decl = get_solar_declination(month)
    season = get_season_name(month)
    monsoon = get_monsoon_state(month)
    ms = monsoon["season"]
    current_desc = {
        "summer": "大陆形成热低压，东南季风盛行，带来丰沛降水",
        "winter": "大陆形成冷高压，西北季风盛行，寒冷干燥",
        "transition": "处于季风过渡期，风向多变，强度较弱",
    }.get(ms, "处于季风过渡期")

    with st.expander("知识点 — 东亚季风", expanded=False):
        st.markdown(f"""
### 东亚季风 — {get_month_name(month)}

**形成原因:** 海陆热力性质差异

亚洲大陆 (世界最大大陆) 与 太平洋 (世界最大大洋) 之间的温度差。

**夏季 (5~9月):**
- 大陆升温快 → 形成**亚洲低压** (热低压)
- 海洋升温慢 → **太平洋高压** (副热带高压)
- 风从海洋吹向大陆 → **东南季风**
- 带来丰沛降水 (中国东部雨季)

**冬季 (11~次年2月):**
- 大陆降温快 → 形成**亚洲高压** (冷高压, 西伯利亚高压)
- 海洋降温慢 → **太平洋低压** (阿留申低压)
- 风从大陆吹向海洋 → **西北季风**
- 寒冷干燥 (中国北方寒潮)

**过渡期 (3~4月, 10月):**
- 海陆热力差异减弱
- 季风较弱，风向多变

**当前状态:** 北半球{season}，{current_desc}

### 为什么东亚季风最典型?

1. **欧亚大陆**是世界最大的大陆 — 热容量差异最大
2. **太平洋**是世界最大的大洋
3. 背靠世界屋脊**青藏高原** — 加强了海陆热力差异
4. 东亚位于大陆东岸 — 海陆对比最显著的位置
""")

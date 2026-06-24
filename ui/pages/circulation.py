"""
三圈环流 — 子页面
================
纬度-高度剖面图: 哈德莱环流 / 费雷尔环流 / 极地环流.
"""
import streamlit as st
import matplotlib.pyplot as plt
from modules.three_cell_circulation import plot_three_cell_circulation
from utils.physics import get_solar_declination, get_month_name
from ui.pages._base import render_animation_button


def render_circulation_page():
    st.subheader("三圈环流")
    render_animation_button()

    amp = st.session_state.shift_amplitude
    month = st.session_state.month
    decl = get_solar_declination(month)

    fig, ax = plt.subplots(figsize=(8, 5))
    plot_three_cell_circulation(ax, month, amp)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    with st.expander("知识点 — 三圈环流", expanded=False):
        st.markdown(f"""
### 三圈环流 — {get_month_name(month)}

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

### 关键记忆

| 环流圈 | 类型 | 纬度范围 | 近地面风带 |
|--------|------|---------|-----------|
| 哈德莱 (Hadley) | 直接热力 | 0°~30° | 信风带 |
| 费雷尔 (Ferrel) | 间接 | 30°~60° | 盛行西风 |
| 极地 (Polar) | 直接热力 | 60°~90° | 极地东风 |

- ↑ 红色竖线 = 上升气流 (低压区, 多云雨)
- ↓ 蓝色竖线 = 下沉气流 (高压区, 晴朗)

**记忆口诀:** 「热升冷降, 低压多云雨, 高压晴燥」
""")

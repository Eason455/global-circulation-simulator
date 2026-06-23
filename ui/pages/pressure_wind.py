"""
气压带与风带分布 — 子页面
=========================
全球纬度剖面图: 7个气压带 + 6个风带, 季节移动.
"""
import streamlit as st
import matplotlib.pyplot as plt
from modules.pressure_wind_belts import plot_pressure_wind_belts
from utils.physics import get_solar_declination, get_month_name, get_season_name
from ui.pages._base import render_animation_button, run_single_chart_animation


def render_pressure_wind_page():
    st.subheader("气压带与风带分布")

    render_animation_button("播放动画")

    amp = st.session_state.shift_amplitude
    month = st.session_state.month
    decl = get_solar_declination(month)
    season = get_season_name(month)

    if st.session_state.animating:
        run_single_chart_animation(
            plot_fn=plot_pressure_wind_belts,
            figsize=(6, 6),
            plot_kwargs={"shift_amplitude": amp},
        )
    else:
        fig, ax = plt.subplots(figsize=(6, 6))
        plot_pressure_wind_belts(ax, month, amp)
        st.pyplot(fig)
        plt.close(fig)

    with st.expander("知识点 — 气压带与风带", expanded=False):
        st.markdown(f"""
### 气压带与风带 — {get_month_name(month)}

**气压带分布 (基准 ± 季节移动 {amp}°):**

| 气压带 | 缩写 | 基准纬度 | 当前纬度 (估) | 类型 | 成因 |
|--------|------|---------|-------------|------|------|
| 极地高压带 | PHP | 90° | ~90° | 高压 | 热力 |
| 副极地低压带 | SPL | 60° | {60+decl*0.5:.0f}° | 低压 | 动力 |
| 副热带高压带 | STH | 30° | {30+decl*0.8:.0f}° | 高压 | 动力 |
| 赤道低压带 | ITCZ | 0° | {decl*1.0:.1f}° | 低压 | 热力 |

**风带风向 (由气压梯度力 + 地转偏向力共同决定):**

| 风带 | 纬度范围 | 北半球风向 | 南半球风向 |
|------|---------|-----------|-----------|
| 信风带 (Trade Winds) | 0°~30° | 东北风 | 东南风 |
| 盛行西风带 (Westerlies) | 30°~60° | 西南风 | 西北风 |
| 极地东风带 (Polar Easterlies) | 60°~90° | 东北风 | 东南风 |

**当前季节效应:** 北半球{season}，所有气压带/风带整体向{'北' if decl > 0 else '南'}偏移约 {abs(decl)*0.8:.1f}°。

**关键记忆:**
- 低压 = 上升气流 = 多云雨 (赤道低压、副极地低压)
- 高压 = 下沉气流 = 晴朗干燥 (副热带高压、极地高压)
- 赤道低压 (ITCZ) 和极地高压 (PHP) 是**热力成因**
- 副热带高压 (STH) 和副极地低压 (SPL) 是**动力成因**
""")

"""
全球降水带移动 — 子页面
=======================
纬向分布图: ITCZ 雨带位置随季节移动.
"""
import streamlit as st
import matplotlib.pyplot as plt
from modules.rain_belt import plot_rain_belt
from utils.physics import get_solar_declination, get_month_name, get_season_name
from ui.pages._base import render_animation_button, run_single_chart_animation


def render_rain_page():
    st.subheader("全球降水带 (ITCZ) 移动")

    render_animation_button()

    if st.session_state.animating:
        run_single_chart_animation(
            plot_fn=plot_rain_belt,
            figsize=(9, 3.5),
        )
    else:
        fig, ax = plt.subplots(figsize=(9, 3.5))
        plot_rain_belt(ax, st.session_state.month)
        st.pyplot(fig)
        plt.close(fig)

    month = st.session_state.month
    decl = get_solar_declination(month)
    season = get_season_name(month)

    with st.expander("知识点 — 降水带与 ITCZ", expanded=False):
        st.markdown(f"""
### 全球降水带 — {get_month_name(month)}

**ITCZ (热带辐合带) 降水带:**
- 跟随太阳直射点移动，约有 **1 个月滞后**
- {month:.0f}月: 雨带大致位于 {abs(decl)*0.9:.1f}°{'N' if decl > 0 else 'S'} 附近
- 北半球夏季雨带最北可达 20-25°N (青藏高原南缘)

### 降水带类型

| 降水带 | 纬度 | 成因 | 特点 |
|--------|------|------|------|
| 赤道多雨带 | 0°~10° | 全年赤道低压上升气流 | 年降水 >2000mm |
| 副热带少雨带 | 15°~30° | 全年副高下沉气流 | 年降水 <250mm (沙漠) |
| 中纬多雨带 | 40°~60° | 西风带 + 锋面活动 | 年降水 500-1000mm |
| 极地少雨带 | 70°~90° | 极地高压 + 低温 | 年降水 <250mm (冰雪) |

### 降水与气压带关系

**口诀:** 「低压上升多云雨, 高压下沉晴燥」
- 赤道低压带 (ITCZ) → 全年多雨
- 副热带高压带 (STH) → 干燥沙模
- 副极地低压带 (SPL) → 中纬度降水
- 极地高压带 (PHP) → 极地干燥

**当前影响:** 北半球{season}，
{'雨带偏北, 东亚/南亚进入雨季' if decl > 10 else '雨带偏南, 澳大利亚北部进入雨季' if decl < -10 else '雨带位于赤道附近'}
""")

"""
全球气压带风带季节移动与东亚季风形成交互模拟器
==========================================
面向高中地理学习的动态可视化教学工具.

功能模块:
  1. 太阳直射点周年运动
  2. 全球气压带与风带动态模拟
  3. 三圈环流可视化
  4. 东亚季风形成模拟
  5. 雨带移动模拟
  6. 全球气候带联动
  7. 交互控制面板 + 考试模式

运行方式:
  streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

# 设置中文字体 (跨平台兼容: Windows/Linux/macOS)
plt.rcParams['font.sans-serif'] = [
    'Microsoft YaHei', 'SimHei',
    'Noto Sans CJK SC', 'Noto Sans SC',
    'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',
    'PingFang SC', 'Heiti SC',
    'STFangsong', 'KaiTi',
    'DejaVu Sans',
]
plt.rcParams['axes.unicode_minus'] = False

# 导入各功能模块
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
from modules.exam_mode import generate_questions, grade_exam
from utils.physics import (
    get_solar_declination,
    get_month_name,
    get_season_name,
)

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="全球大气环流与东亚季风模拟器",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义 CSS 主题 (学术简洁风格, 参考 NASA/国家地理)
st.markdown("""
<style>
    /* 全局字体和颜色 */
    .stApp {
        background-color: #f8f9fa;
    }
    /* 标题 */
    h1, h2, h3 {
        color: #2d3436;
        font-weight: 700;
    }
    /* 卡片容器 */
    .stCard {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background-color: #2d3436;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #dfe6e9 !important;
    }
    /* 按钮 */
    .stButton > button {
        background-color: #0984e3;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #2d3436, #636e72);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 初始化会话状态
# ============================================================
def init_session_state():
    """初始化 Streamlit 会话状态变量"""
    defaults = {
        "month": 7.0,              # 当前月份 (默认7月=夏季)
        "anim_speed": "normal",    # 动画速度: slow/normal/fast
        "shift_amplitude": 10,     # 风带移动幅度: 5/10/15
        "show_solar": True,        # 显示太阳直射点
        "show_circulation": True,  # 显示三圈环流
        "show_wind": True,         # 显示风带
        "show_monsoon": True,      # 显示季风
        "show_rain": True,         # 显示雨带
        "show_climate": True,      # 显示气候带
        "highlight_climate": None, # 高亮气候带名称
        "animating": False,        # 是否正在播放动画
        "exam_active": False,      # 考试模式是否激活
        "exam_questions": [],      # 考试题目
        "exam_answers": [],        # 用户答案
        "exam_submitted": False,   # 是否已提交
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ============================================================
# 侧边栏: 交互控制面板
# ============================================================
def render_sidebar() -> None:
    """渲染侧边栏控制面板"""
    with st.sidebar:
        st.title("🎛️ 控制面板")

        # ---- 月份滑块 ----
        st.markdown("### 📅 月份选择")
        month = st.slider(
            "拖动选择月份",
            min_value=0.1,  # 1月上旬
            max_value=12.9, # 12月下旬
            value=st.session_state.month,
            step=0.1,
            format="%.1f 月",
            key="month_slider",
        )
        st.session_state.month = month

        # 当前月份信息
        decl = get_solar_declination(month)
        decl_str = f"{abs(decl):.1f}°{'N' if decl >= 0 else 'S'}"
        season = get_season_name(month)
        month_name = get_month_name(month)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("月份", month_name)
        with col2:
            st.metric("北半球", season)
        with col3:
            st.metric("直射纬度", decl_str)

        st.divider()

        # ---- 动画控制 ----
        st.markdown("### ▶️ 动画控制")
        anim_speed = st.select_slider(
            "动画速度",
            options=["slow", "normal", "fast"],
            value=st.session_state.anim_speed,
            format_func=lambda x: {"slow": "🐢 慢速", "normal": "▶️ 正常", "fast": "⚡ 快速"}[x],
            key="anim_speed_select",
        )
        st.session_state.anim_speed = anim_speed

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("▶ 播放动画", use_container_width=True):
                st.session_state.animating = True
                st.rerun()
        with col_b:
            if st.button("⏸ 停止", use_container_width=True):
                st.session_state.animating = False
                st.rerun()

        st.divider()

        # ---- 风带移动幅度 ----
        st.markdown("### ↔️ 风带移动幅度")
        shift_amplitude = st.radio(
            "气压带/风带季节移动幅度",
            options=[5, 10, 15],
            index=1,
            format_func=lambda x: f"±{x}°",
            horizontal=True,
            key="shift_radio",
        )
        st.session_state.shift_amplitude = shift_amplitude

        st.divider()

        # ---- 显示开关 ----
        st.markdown("### 👁️ 显示开关")
        st.session_state.show_solar = st.checkbox("☀️ 太阳直射点", value=True)
        st.session_state.show_circulation = st.checkbox("🔄 三圈环流", value=True)
        st.session_state.show_wind = st.checkbox("💨 气压带/风带", value=True)
        st.session_state.show_monsoon = st.checkbox("🌏 东亚季风", value=True)
        st.session_state.show_rain = st.checkbox("🌧️ 雨带移动", value=True)
        st.session_state.show_climate = st.checkbox("🌍 气候带联动", value=True)

        st.divider()

        # ---- 考试模式 ----
        st.markdown("### 📝 考试模式")
        if not st.session_state.exam_active:
            if st.button("🎯 开始考试", use_container_width=True):
                st.session_state.exam_active = True
                st.session_state.exam_questions = generate_questions(4)
                st.session_state.exam_answers = [-1] * 4
                st.session_state.exam_submitted = False
                st.rerun()
        else:
            if st.button("🔙 退出考试", use_container_width=True):
                st.session_state.exam_active = False
                st.session_state.exam_submitted = False
                st.rerun()

        st.divider()

        # ---- 图例说明 ----
        st.markdown("### ℹ️ 图例与说明")
        st.markdown("""
        <div style="font-size:0.8rem; color:#b2bec3;">
        <b>气压带标记:</b><br>
        <span style="color:#00b894;">L</span> = 低压 (上升气流, 多云雨)<br>
        <span style="color:#e17055;">H</span> = 高压 (下沉气流, 晴燥)<br><br>
        <b>环流颜色:</b><br>
        <span style="color:#d63031;">红色</span> = 上升气流<br>
        <span style="color:#0984e3;">蓝色</span> = 下沉气流<br><br>
        <b>气压带缩写:</b><br>
        ITCZ = 赤道低压带<br>
        STH = 副热带高压带<br>
        SPL = 副极地低压带<br>
        PHP = 极地高压带<br>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 动画循环
# ============================================================
def handle_animation():
    """处理自动动画播放"""
    if st.session_state.animating:
        speeds = {"slow": 0.05, "normal": 0.12, "fast": 0.3}
        step = speeds.get(st.session_state.anim_speed, 0.12)

        new_month = st.session_state.month + step
        if new_month > 13:
            new_month -= 12
        st.session_state.month = new_month

        # 使用 Streamlit 的自动刷新
        import time
        time.sleep(0.3)
        st.rerun()


# ============================================================
# 页面标题和状态栏
# ============================================================
def render_header():
    """渲染页面标题和信息栏"""
    col_title, col_status = st.columns([3, 1])

    with col_title:
        st.title("全球大气环流与东亚季风模拟器")
        st.caption(
            "Global Atmospheric Circulation & East Asian Monsoon Simulator | "
            "高中地理教学可视化工具 | "
            "参考: 人教版高中地理选择性必修1"
        )

    with col_status:
        month = st.session_state.month
        decl = get_solar_declination(month)
        season = get_season_name(month)

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #0984e3, #074b8a);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            text-align: center;
            font-size: 0.9rem;
        ">
            <div style="font-size:1.5rem; font-weight:bold;">{get_month_name(month)}</div>
            <div>{season} | 直射 {abs(decl):.1f}°{'N' if decl >= 0 else 'S'}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 主可视化布局
# ============================================================
def render_main_visualizations():
    """渲染主可视化区域 (上排: 全球环流 + 季风, 下排: 气候带)"""

    # ---- 第一行: 太阳直射点 + 气压带风带 + 三圈环流 ----
    st.markdown("---")
    st.subheader("一、全球大气环流系统")

    # 根据显示开关决定列数
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
                    st.markdown("#### ☀️ 太阳直射点周年运动")
                    fig, ax = plt.subplots(figsize=(5, 4.5))
                    plot_solar_declination(ax, st.session_state.month)
                    st.pyplot(fig)
                    plt.close(fig)

                elif panel == "wind":
                    st.markdown("#### 💨 气压带与风带分布")
                    fig, ax = plt.subplots(figsize=(5, 5.5))
                    plot_pressure_wind_belts(
                        ax,
                        st.session_state.month,
                        st.session_state.shift_amplitude,
                    )
                    st.pyplot(fig)
                    plt.close(fig)

                elif panel == "circulation":
                    st.markdown("#### 🔄 三圈环流")
                    fig, ax = plt.subplots(figsize=(6, 4.5))
                    plot_three_cell_circulation(
                        ax,
                        st.session_state.month,
                        st.session_state.shift_amplitude,
                    )
                    st.pyplot(fig)
                    plt.close(fig)
    else:
        st.info("请在侧边栏开启至少一个显示选项以查看全球环流图。")

    # ---- 第二行: 东亚季风 + 雨带移动 ----
    st.markdown("---")
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
                    st.markdown("#### 🌏 东亚季风形成模拟")
                    fig, ax = plt.subplots(figsize=(5.5, 5))
                    plot_east_asian_monsoon(ax, st.session_state.month)
                    st.pyplot(fig)
                    plt.close(fig)

                elif panel == "rain":
                    st.markdown("#### 🌧️ 全球降水带 (ITCZ) 移动")
                    fig, ax = plt.subplots(figsize=(6, 3))
                    plot_rain_belt(ax, st.session_state.month)
                    st.pyplot(fig)
                    plt.close(fig)
    else:
        st.info("请在侧边栏开启至少一个显示选项以查看季风与降水图。")

    # ---- 第三行: 气候带联动 ----
    if st.session_state.show_climate:
        st.markdown("---")
        st.subheader("三、全球气候带与气压带联动")

        # 气候带选择器
        climate_names = [
            "热带雨林气候", "热带草原气候", "热带沙漠气候",
            "地中海气候", "温带海洋性气候", "温带季风气候",
            "温带大陆性气候", "亚寒带针叶林气候", "极地气候",
        ]

        highlight = st.selectbox(
            "点击气候带查看详细信息 (或选择「无」查看全局)",
            ["无"] + climate_names,
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
                    st.markdown("#### 📋 气候带详情")
                    st.markdown(render_climate_detail(zone), unsafe_allow_html=True)
            else:
                st.markdown("#### 📋 使用提示")
                st.markdown("""
                <div style="
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                    font-size: 0.9rem;
                ">
                <p>从上方的下拉菜单中选择一个气候带，即可查看:</p>
                <ul>
                    <li>形成原因</li>
                    <li>典型分布地区</li>
                    <li>降水特点</li>
                    <li>气温特点</li>
                </ul>
                <p>左侧图中该气候带会被高亮显示。</p>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# 考试模式
# ============================================================
def render_exam_mode():
    """渲染考试模式界面"""
    st.markdown("---")
    st.subheader("📝 考试模式")

    if not st.session_state.exam_submitted:
        st.markdown(f"""
        <div style="
            background: #ffeaa7;
            padding: 10px 15px;
            border-radius: 6px;
            border-left: 4px solid #fdcb6e;
            margin-bottom: 1rem;
        ">
            <b>考试说明:</b> 系统随机选择月份，请根据已学知识判断
            气压带位置、风带方向、季风状态和雨带位置。
            每题只有一个正确答案。
        </div>
        """, unsafe_allow_html=True)

        # 显示题目
        questions = st.session_state.exam_questions
        for i, q in enumerate(questions):
            # 随机显示的月份信息
            month_int = int(round(q.month))
            season = get_season_name(q.month)
            decl = get_solar_declination(q.month)
            decl_str = f"{abs(decl):.1f}°{'N' if decl >= 0 else 'S'}"

            st.markdown(f"""
            <div style="
                background: white;
                padding: 12px 16px;
                border-radius: 8px;
                border: 1px solid #dee2e6;
                margin-bottom: 0.5rem;
            ">
                <b>第 {i+1} 题</b>
                <span style="color:#636e72;"> | {month_int}月 ({season}) | 直射: {decl_str}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**{q.question_text}**")

            # 选项 (radio button)
            answer = st.radio(
                f"选择答案 (第{i+1}题)",
                options=list(range(len(q.options))),
                format_func=lambda x, q=q: f"{chr(65+x)}. {q.options[x]}",
                key=f"exam_q_{i}",
                index=None,
            )
            if answer is not None:
                st.session_state.exam_answers[i] = answer

        # 提交按钮
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("📩 提交答卷", use_container_width=True, type="primary"):
                if -1 in st.session_state.exam_answers:
                    st.error("请完成所有题目后再提交!")
                else:
                    st.session_state.exam_submitted = True
                    st.rerun()
        with col_btn2:
            if st.button("🔄 重新出题", use_container_width=True):
                st.session_state.exam_questions = generate_questions(4)
                st.session_state.exam_answers = [-1] * 4
                st.rerun()

    else:
        # 显示考试结果
        questions = st.session_state.exam_questions
        answers = st.session_state.exam_answers
        score, total, feedback = grade_exam(questions, answers)

        # 成绩卡片
        percentage = score / total * 100
        grade_color = (
            "#00b894" if percentage >= 80 else
            "#fdcb6e" if percentage >= 60 else
            "#d63031"
        )
        grade_text = (
            "优秀 [OK]" if percentage >= 80 else
            "良好" if percentage >= 60 else
            "需要加强"
        )

        st.markdown(f"""
        <div style="
            background: {grade_color};
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 1.5rem;
        ">
            <div style="font-size:3rem; font-weight:bold;">{score}/{total}</div>
            <div style="font-size:1.2rem;">{grade_text} ({percentage:.0f}%)</div>
        </div>
        """, unsafe_allow_html=True)

        # 逐题反馈
        for i, fb in enumerate(feedback):
            icon = "✅" if fb["is_correct"] else "❌"
            bg = "#e6fff2" if fb["is_correct"] else "#fff0f0"
            border = "#00b894" if fb["is_correct"] else "#d63031"

            correct_info = (
                "" if fb["is_correct"]
                else f" | 正确答案: {fb['correct_answer']}"
            )
            st.markdown(f"""
            <div style="
                background: {bg};
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid {border};
                margin-bottom: 0.8rem;
            ">
                <b>{icon} 第{i+1}题:</b> {fb['question']}<br>
                <span style="color: {'#00b894' if fb['is_correct'] else '#d63031'};">
                    你的答案: {fb['user_answer']}{correct_info}
                </span><br>
                <small style="color:#636e72;">{fb['explanation']}</small>
            </div>
            """, unsafe_allow_html=True)

        # 重新考试
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 重新出题", use_container_width=True):
                st.session_state.exam_questions = generate_questions(4)
                st.session_state.exam_answers = [-1] * 4
                st.session_state.exam_submitted = False
                st.rerun()
        with col_r2:
            if st.button("🔙 退出考试模式", use_container_width=True):
                st.session_state.exam_active = False
                st.session_state.exam_submitted = False
                st.rerun()


# ============================================================
# 知识点面板
# ============================================================
def render_knowledge_panel():
    """渲染知识总结面板 (可折叠)"""
    with st.expander("📚 知识点总结 (点击展开)", expanded=False):
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
            st.markdown(f"""
            ### 东亚季风 — 当前状态 ({get_month_name(month)})

            **形成原因:** 海陆热力性质差异

            亚洲大陆 (世界最大大陆) 与 太平洋 (世界最大大洋) 之间的温度差:

            **夏季 ({3}-{8}月):**
            - 大陆升温快 → 形成亚洲低压 (热低压)
            - 海洋升温慢 → 太平洋高压 (副热带高压)
            - 风从海洋吹向大陆 → **东南季风**
            - 带来丰沛降水 (中国东部雨季)

            **冬季 ({9}-{2}月):**
            - 大陆降温快 → 形成亚洲高压 (冷高压, 西伯利亚高压)
            - 海洋降温慢 → 太平洋低压 (阿留申低压)
            - 风从大陆吹向海洋 → **西北季风**
            - 寒冷干燥 (中国北方寒潮)

            **当前状态:** 北半球{season}，
            {'大陆形成热低压，东南季风盛行' if decl > 5 else '大陆形成冷高压，西北季风盛行' if decl < -5 else '处于季风过渡期'}
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


# ============================================================
# 主函数
# ============================================================
def main():
    """主应用入口"""

    # 渲染侧边栏
    render_sidebar()

    # 处理动画
    handle_animation()

    # 渲染标题栏
    render_header()

    # 根据模式渲染内容
    if st.session_state.exam_active:
        render_exam_mode()
    else:
        render_main_visualizations()
        render_knowledge_panel()

    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#636e72; font-size:0.8rem;'>"
        "全球大气环流与东亚季风模拟器 v1.0 | "
        "面向高中地理教学 | "
        "数据基于大气环流经典理论, 仅供教学演示参考 | "
        "&copy; 2025 Educational Use"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

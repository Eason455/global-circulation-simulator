"""
考试模式面板
==========
随机出题, 用户作答, 自动判分, 逐题反馈.
"""

import streamlit as st
from modules.exam_mode import generate_questions, grade_exam
from utils.physics import get_solar_declination, get_season_name


def render_exam_mode() -> None:
    """渲染考试模式界面 — Apple 风格"""
    st.divider()
    st.subheader("考试模式")

    if not st.session_state.exam_submitted:
        _render_exam_questions()
    else:
        _render_exam_results()


def _render_exam_questions() -> None:
    """渲染题目和作答区域"""
    st.markdown("""
    <div class="glass-card" style="font-size:13px; line-height:1.6; margin-bottom:1.25rem; border-left:3px solid var(--accent);">
        <b style="color:#1d1d1f;">考试说明：</b>
        系统随机选择月份，请根据已学知识判断
        气压带位置、风带方向、季风状态和雨带位置。
        每题只有一个正确答案。
    </div>
    """, unsafe_allow_html=True)

    questions = st.session_state.exam_questions
    for i, q in enumerate(questions):
        month_int = int(round(q.month))
        season = get_season_name(q.month)
        decl = get_solar_declination(q.month)
        decl_str = f"{abs(decl):.1f}" + ("°N" if decl >= 0 else "°S")

        st.markdown(f"""
        <div style="
            background: var(--bg-glass);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            padding: 12px 16px;
            border-radius: var(--radius-sm);
            border: 0.5px solid var(--border);
            margin-bottom: 0.5rem;
        ">
            <b style="color:#1d1d1f;">第 {i+1} 题</b>
            <span style="color:#86868b;"> &middot; {month_int}月 ({season}) &middot; 直射 {decl_str}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**{q.question_text}**")

        answer = st.radio(
            f"第 {i+1} 题答案",
            options=list(range(len(q.options))),
            format_func=lambda x, q=q: f"{chr(65+x)}. {q.options[x]}",
            key=f"exam_q_{i}",
            index=None,
        )
        if answer is not None:
            st.session_state.exam_answers[i] = answer

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        if st.button("提交答卷", use_container_width=True, type="primary"):
            if -1 in st.session_state.exam_answers:
                st.error("请完成所有题目后再提交！")
            else:
                st.session_state.exam_submitted = True
                st.rerun()
    with col_btn2:
        if st.button("重新出题", use_container_width=True):
            st.session_state.exam_questions = generate_questions(4)
            st.session_state.exam_answers = [-1] * 4
            st.rerun()


def _render_exam_results() -> None:
    """渲染考试结果和逐题反馈"""
    questions = st.session_state.exam_questions
    answers = st.session_state.exam_answers
    score, total, feedback = grade_exam(questions, answers)

    percentage = score / total * 100
    grade_color = (
        "var(--success)" if percentage >= 80 else
        "var(--warning)" if percentage >= 60 else
        "var(--danger)"
    )
    grade_text = (
        "优秀" if percentage >= 80 else
        "良好" if percentage >= 60 else
        "需要加强"
    )

    st.markdown(f"""
    <div class="exam-score" style="margin-bottom:1.5rem;">
        <div class="score-num" style="color:{grade_color};">{score}/{total}</div>
        <div style="font-size:14px; color:#86868b; margin-top:4px;">{grade_text} ({percentage:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

    for i, fb in enumerate(feedback):
        is_ok = fb["is_correct"]
        marker = "[OK]" if is_ok else "[X]"
        css_class = "exam-correct" if is_ok else "exam-wrong"
        color = "#34c759" if is_ok else "#ff3b30"

        correct_info = (
            "" if is_ok
            else f" | 正确答案: {fb['correct_answer']}"
        )
        st.markdown(f"""
        <div class="{css_class}">
            <b style="color:{color};">{marker} 第{i+1}题:</b> {fb['question']}<br>
            <span style="color:{color}; font-size:13px;">
                你的答案: {fb['user_answer']}{correct_info}
            </span><br>
            <small style="color:#aeaeb2;">{fb['explanation']}</small>
        </div>
        """, unsafe_allow_html=True)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("重新出题", use_container_width=True):
            st.session_state.exam_questions = generate_questions(4)
            st.session_state.exam_answers = [-1] * 4
            st.session_state.exam_submitted = False
            st.rerun()
    with col_r2:
        if st.button("退出考试模式", use_container_width=True):
            st.session_state.exam_active = False
            st.session_state.exam_submitted = False
            st.session_state.page_selector = "太阳直射点周年运动"
            st.rerun()

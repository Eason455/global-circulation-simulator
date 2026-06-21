"""
模块7: 考试模式 (加分功能)
=======================
随机选择月份, 用户判断气压带/风带/季风/雨带位置,
系统自动判分.
"""

import random
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

from utils.physics import (
    get_solar_declination,
    get_pressure_belt_positions,
    get_wind_belts,
    get_monsoon_state,
    get_rain_belt_position,
    get_season_name,
)


@dataclass
class ExamQuestion:
    """考试题目"""
    id: str
    month: float
    question_type: str
    question_text: str
    options: List[str]
    correct_index: int
    explanation: str


def generate_questions(n_questions: int = 4) -> List[ExamQuestion]:
    """生成一组随机考试题, 题型顺序随机打乱."""
    questions = []
    type_pool = ["pressure", "wind", "monsoon", "rain"]

    for i in range(n_questions):
        # 每个题型至少出现一次, 剩余随机抽取
        if i < len(type_pool):
            q_type = type_pool[i]
        else:
            q_type = random.choice(type_pool)
        # 随机打乱顺序
        random.shuffle(type_pool)

        month = random.uniform(0.5, 12.5)
        if month > 12:
            month -= 12
        if month < 1:
            month += 12

        decl = get_solar_declination(month)
        pressure_belts = get_pressure_belt_positions(decl, 10.0)
        wind_belts = get_wind_belts(pressure_belts)
        monsoon = get_monsoon_state(month)
        rain = get_rain_belt_position(month)
        season = get_season_name(month)

        if q_type == "pressure":
            q = _gen_pressure_question(month, season, decl, pressure_belts)
        elif q_type == "wind":
            q = _gen_wind_question(month, season, wind_belts)
        elif q_type == "monsoon":
            q = _gen_monsoon_question(month, season, monsoon)
        else:
            q = _gen_rain_question(month, season, rain)

        questions.append(q)

    return questions


def _gen_pressure_question(month, season, decl, belts) -> ExamQuestion:
    """生成气压带相关考题"""
    from utils.physics import get_month_name
    month_label = get_month_name(month)
    decl_str = f"{abs(decl):.1f}°{'N' if decl >= 0 else 'S'}"
    itcz = next((b for b in belts if b.name == "赤道低压带"), None)
    if itcz:
        belt_lat = abs(itcz.base_lat)
        belt_hemi = "N" if itcz.base_lat >= 0 else "S"
        correct_text = f"{belt_lat:.0f}°{belt_hemi} 附近"
    else:
        correct_text = "约5°N-5°S"

    return ExamQuestion(
        id=f"p_{month:.1f}",
        month=month,
        question_type="pressure",
        question_text=(
            f"{month_label} ({season}), 太阳直射点位于 {decl_str}。"
            f"此时赤道低压带 (ITCZ) 的主体位置在哪?"
        ),
        options=[
            "赤道附近 (0°)",
            f"北半球 {correct_text}" if decl > 0 else f"南半球 {correct_text}",
            "南半球" if decl > 0 else "北半球",
            "不发生移动",
        ],
        correct_index=1,
        explanation=(
            f"太阳直射点位于 {decl_str}, "
            f"赤道低压带跟随太阳直射点向{'北' if decl > 0 else '南'}移动, "
            f"大致位于 {correct_text}。"
        ),
    )


def _gen_wind_question(month, season, wind_belts) -> ExamQuestion:
    """生成风带相关考题"""
    nh_westerlies = next(
        (w for w in wind_belts if "西风带" in w.name and w.lat_min > 10),
        None
    )

    if nh_westerlies:
        return ExamQuestion(
            id=f"w_{month}",
            month=month,
            question_type="wind",
            question_text=(
                f"{int(round(month))}月 ({season}), 北半球中纬度地区盛行什么风?"
            ),
            options=[
                "东北信风",
                "东南信风",
                "盛行西风",
                "极地东风",
            ],
            correct_index=2,
            explanation=(
                f"北半球中纬度 ({nh_westerlies.lat_min:.0f}° ~ "
                f"{nh_westerlies.lat_max:.0f}°) "
                f"盛行西风带, 风向为{nh_westerlies.direction_cn}风。"
            ),
        )
    else:
        return ExamQuestion(
            id=f"w_{month}",
            month=month,
            question_type="wind",
            question_text=f"{int(round(month))}月 ({season}), 北半球低纬度地区盛行什么风?",
            options=["东北信风", "东南信风", "盛行西风", "极地东风"],
            correct_index=0,
            explanation="北半球低纬度盛行东北信风, 受科里奥利力影响向右偏转。",
        )


def _gen_monsoon_question(month, season, monsoon) -> ExamQuestion:
    """生成季风相关考题"""
    from utils.physics import get_month_name
    month_label = get_month_name(month)
    if monsoon["season"] == "summer":
        return ExamQuestion(
            id=f"m_{month:.1f}",
            month=month,
            question_type="monsoon",
            question_text=(
                f"{month_label} ({season}), 东亚地区盛行什么季风? 风向如何?"
            ),
            options=[
                "西北季风 (大陆→海洋)",
                "东南季风 (海洋→大陆)",
                "东北季风 (大陆→海洋)",
                "西南季风 (海洋→大陆)",
            ],
            correct_index=1,
            explanation=(
                f"{month}月为夏季, 大陆形成热低压, 海洋为高压, "
                f"风从海洋吹向大陆, 受地转偏向力影响形成东南季风。"
            ),
        )
    elif monsoon["season"] == "winter":
        return ExamQuestion(
            id=f"m_{month:.1f}",
            month=month,
            question_type="monsoon",
            question_text=(
                f"{month_label} ({season}), 东亚地区盛行什么季风? 风向如何?"
            ),
            options=[
                "西北季风 (大陆→海洋)",
                "东南季风 (海洋→大陆)",
                "西南季风 (海洋→大陆)",
                "东北季风 (大陆→海洋)",
            ],
            correct_index=0,
            explanation=(
                f"{month}月为冬季, 大陆形成冷高压, 海洋为低压, "
                f"风从大陆吹向海洋, 受地转偏向力影响形成西北季风。"
            ),
        )
    else:
        return ExamQuestion(
            id=f"m_{month:.1f}",
            month=month,
            question_type="monsoon",
            question_text=f"{month_label} ({season}), 东亚季风处于什么状态?",
            options=[
                "夏季风 (东南风)",
                "冬季风 (西北风)",
                "过渡期 (季风较弱, 风向多变)",
                "不存在季风",
            ],
            correct_index=2,
            explanation="春秋过渡季节, 海陆热力差异减弱, 季风不稳定。",
        )


def _gen_rain_question(month, season, rain) -> ExamQuestion:
    """生成雨带相关考题"""
    from utils.physics import get_month_name
    month_label = get_month_name(month)
    lat = rain["lat_center"]
    lat_str = f"{abs(lat):.1f}°{'N' if lat >= 0 else 'S'}"

    if abs(lat) > 15:
        anomaly = "偏北" if lat > 15 else "偏南"
    else:
        anomaly = "正常"

    return ExamQuestion(
        id=f"r_{month:.1f}",
        month=month,
        question_type="rain",
        question_text=(
            f"{month_label} ({season}), 全球主要雨带 (ITCZ降水带) 位置在哪?"
        ),
        options=[
            "赤道附近 (0° 附近)",
            f"北半球 {lat_str} 附近",
            f"南半球 {lat_str} 附近",
            "与气压带无关, 随机分布",
        ],
        correct_index=1 if lat >= 0 else 2,
        explanation=(
            f"ITCZ 雨带跟随太阳直射点移动, {month_label}雨带大致位于 {lat_str}, "
            f"位置{anomaly}。"
        ),
    )


def grade_exam(questions: List[ExamQuestion],
               answers: List[int]) -> Tuple[int, int, List[Dict]]:
    """批改考卷."""
    total = len(questions)
    score = 0
    feedback = []

    for q, ans in zip(questions, answers):
        is_correct = (ans == q.correct_index)
        if is_correct:
            score += 1

        feedback.append({
            "question": q.question_text,
            "user_answer": q.options[ans] if 0 <= ans < len(q.options) else "未作答",
            "correct_answer": q.options[q.correct_index],
            "is_correct": is_correct,
            "explanation": q.explanation,
        })

    return score, total, feedback

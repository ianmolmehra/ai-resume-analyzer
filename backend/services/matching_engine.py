from typing import List, Dict, Tuple, Optional
from schemas.match import MatchResponse, SkillGapItem, SkillMatchDetail, ScoreCard, LearningResource
from services.skill_extractor import extract_skills, get_learning_path, SKILL_DATABASE
from services.jd_analyzer import analyze_job_description
from schemas.resume import ParsedResumeData
from datetime import datetime


EDUCATION_RANK = {
    "PhD": 7, "Master's": 6, "MBA": 6, "M.Tech": 5, "M.E": 5,
    "Bachelor's": 4, "B.Tech": 4, "B.E": 4, "BA": 3,
    "Associate": 2, "Diploma": 1,
}


def compute_skill_match(
    candidate_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str],
) -> Tuple[float, List[SkillMatchDetail], List[str], List[str]]:
    candidate_set = {s.lower() for s in candidate_skills}
    all_required = {s.lower(): s for s in required_skills}
    all_preferred = {s.lower(): s for s in preferred_skills}

    matched = []
    missing = []
    details = []

    # Required skills (weight: 1.0)
    required_matched = 0
    for sk_lower, sk_orig in all_required.items():
        if sk_lower in candidate_set:
            matched.append(sk_orig)
            required_matched += 1
            details.append(SkillMatchDetail(skill=sk_orig, matched=True, confidence=0.9, category=SKILL_DATABASE.get(sk_orig, {}).get("category", "Other")))
        else:
            missing.append(sk_orig)
            details.append(SkillMatchDetail(skill=sk_orig, matched=False, category=SKILL_DATABASE.get(sk_orig, {}).get("category", "Other")))

    # Preferred skills (weight: 0.5)
    preferred_matched = 0
    for sk_lower, sk_orig in all_preferred.items():
        if sk_lower in candidate_set:
            matched.append(sk_orig)
            preferred_matched += 1
            details.append(SkillMatchDetail(skill=sk_orig, matched=True, confidence=0.7, category=SKILL_DATABASE.get(sk_orig, {}).get("category", "Other")))

    required_score = (required_matched / len(required_skills) * 100) if required_skills else 100.0
    preferred_bonus = (preferred_matched / len(preferred_skills) * 15) if preferred_skills else 0.0
    skill_score = min(100.0, required_score * 0.85 + preferred_bonus)

    return round(skill_score, 1), details, list(dict.fromkeys(matched)), list(dict.fromkeys(missing))


def compute_experience_match(candidate_years: float, required_years: float) -> float:
    if required_years <= 0:
        return 100.0
    if candidate_years >= required_years:
        return min(100.0, 85.0 + (candidate_years - required_years) * 5)
    ratio = candidate_years / required_years
    return round(min(100.0, ratio * 85.0), 1)


def compute_education_match(candidate_education: Optional[str], required_education: Optional[str]) -> float:
    if not required_education:
        return 90.0
    if not candidate_education:
        return 40.0
    req_rank = max((v for k, v in EDUCATION_RANK.items() if k.lower() in required_education.lower()), default=0)
    cand_rank = max((v for k, v in EDUCATION_RANK.items() if k.lower() in candidate_education.lower()), default=0)
    if cand_rank >= req_rank:
        return 100.0
    elif cand_rank == req_rank - 1:
        return 75.0
    elif cand_rank == req_rank - 2:
        return 50.0
    return 30.0


def compute_project_relevance(project_texts: List[str], required_skills: List[str]) -> float:
    if not project_texts or not required_skills:
        return 50.0
    req_lower = {s.lower() for s in required_skills}
    all_text = " ".join(project_texts).lower()
    hits = sum(1 for s in req_lower if s in all_text)
    score = (hits / len(required_skills)) * 100 if required_skills else 50.0
    return round(min(100.0, score), 1)


def compute_keyword_match(resume_text: str, jd_keywords: List[str]) -> float:
    if not jd_keywords:
        return 75.0
    text_lower = resume_text.lower()
    hits = sum(1 for kw in jd_keywords if kw.lower() in text_lower)
    return round((hits / len(jd_keywords)) * 100, 1)


def compute_ats_score(
    resume_text: str,
    candidate_data: ParsedResumeData,
    jd_keywords: List[str]
) -> float:
    score = 0.0
    # Has contact info
    if candidate_data.email: score += 10
    if candidate_data.phone: score += 5
    if candidate_data.full_name: score += 10
    # Has sections
    if candidate_data.education: score += 15
    if candidate_data.experience: score += 15
    if candidate_data.skills: score += 10
    # Keyword density
    kw_score = compute_keyword_match(resume_text, jd_keywords)
    score += kw_score * 0.35
    return round(min(100.0, score), 1)


def compute_resume_quality(candidate_data: ParsedResumeData, resume_text: str) -> float:
    score = 0.0
    if candidate_data.full_name: score += 10
    if candidate_data.email: score += 8
    if candidate_data.phone: score += 5
    if candidate_data.linkedin_url: score += 5
    if candidate_data.github_url: score += 5
    if candidate_data.summary: score += 8
    if candidate_data.education: score += 12
    if candidate_data.experience: score += 15
    if candidate_data.projects: score += 10
    if candidate_data.certifications: score += 7
    if candidate_data.skills: score += 10
    # Length bonus
    words = len(resume_text.split())
    if 300 <= words <= 1000: score += 5
    return round(min(100.0, score), 1)


def compute_technical_score(skills: List, resume_text: str) -> float:
    if not skills:
        return 0.0
    high_value = sum(1 for s in skills if s.category in ["AI/ML", "Cloud", "DevOps", "Programming"])
    base = min(70.0, len(skills) * 3.5)
    bonus = min(30.0, high_value * 4.0)
    return round(min(100.0, base + bonus), 1)


def compute_employability(
    skill_score: float,
    exp_score: float,
    edu_score: float,
    quality_score: float,
) -> float:
    return round(
        skill_score * 0.35 +
        exp_score * 0.25 +
        edu_score * 0.20 +
        quality_score * 0.20,
        1
    )


def generate_recommendations(
    missing_skills: List[str],
    exp_match: float,
    edu_match: float,
    overall: float,
) -> List[str]:
    recs = []
    if missing_skills:
        top3 = missing_skills[:3]
        recs.append(f"Acquire key missing skills: {', '.join(top3)} to significantly boost your match score.")
    if exp_match < 70:
        recs.append("Gain more hands-on experience through internships, freelance projects, or open-source contributions.")
    if edu_match < 70:
        recs.append("Consider pursuing relevant certifications or higher education to meet the job requirements.")
    if overall < 50:
        recs.append("Your profile needs significant improvement. Focus on building a strong portfolio with projects showcasing the required skills.")
    elif overall < 70:
        recs.append("You have a moderate match. Strengthen your weakest areas to become a stronger candidate.")
    elif overall >= 85:
        recs.append("Excellent match! Tailor your resume language to mirror the job description keywords.")

    recs.append("Ensure your LinkedIn profile is up-to-date and consistent with your resume.")
    recs.append("Add quantifiable achievements to your experience section (e.g., 'Reduced latency by 40%').")
    return recs


def generate_improvement_suggestions(candidate_data: ParsedResumeData, resume_text: str) -> List[str]:
    suggestions = []
    if not candidate_data.summary:
        suggestions.append("Add a professional summary/objective at the top of your resume.")
    if not candidate_data.linkedin_url:
        suggestions.append("Include your LinkedIn profile URL.")
    if not candidate_data.github_url:
        suggestions.append("Add your GitHub profile to showcase your code.")
    if len(candidate_data.experience) < 2:
        suggestions.append("Add more work experience entries or internships.")
    if len(candidate_data.projects) < 2:
        suggestions.append("Include at least 2-3 notable projects with tech stack details.")
    if not candidate_data.certifications:
        suggestions.append("Add relevant certifications to boost credibility.")
    words = len(resume_text.split())
    if words < 300:
        suggestions.append("Your resume is too short. Expand on your experience and projects.")
    elif words > 1200:
        suggestions.append("Your resume may be too long. Keep it concise (1-2 pages).")
    suggestions.append("Use action verbs to start bullet points (e.g., 'Developed', 'Optimized', 'Led').")
    suggestions.append("Quantify your achievements wherever possible.")
    return suggestions


def build_skill_gap_analysis(missing_skills: List[str], required_skills: List[str]) -> List[SkillGapItem]:
    gap = []
    total = len(required_skills) if required_skills else 1
    for i, skill in enumerate(missing_skills):
        priority = "High" if i < total * 0.4 else ("Medium" if i < total * 0.7 else "Low")
        lp = get_learning_path(skill)
        gap.append(SkillGapItem(
            skill=skill,
            category=SKILL_DATABASE.get(skill, {}).get("category", "Other"),
            priority=priority,
            learning_path=[LearningResource(**r) for r in lp],
        ))
    return gap


def match_resume_to_jd(
    candidate_data: ParsedResumeData,
    resume_text: str,
    jd_data: Dict,
    resume_id: int,
    jd_id: int,
) -> Dict:
    candidate_skill_names = [s.name for s in candidate_data.skills]

    required_skills = jd_data.get("required_skills", [])
    preferred_skills = jd_data.get("preferred_skills", [])
    jd_keywords = jd_data.get("keywords", [])

    skill_score, skill_details, matched, missing = compute_skill_match(
        candidate_skill_names, required_skills, preferred_skills
    )
    exp_score = compute_experience_match(
        candidate_data.total_experience_years,
        jd_data.get("experience_required", 0.0)
    )
    edu_score = compute_education_match(
        candidate_data.highest_education,
        jd_data.get("education_required")
    )
    project_texts = [
        (p.description or "") + " " + " ".join(p.tech_stack or [])
        for p in candidate_data.projects
    ]
    proj_score = compute_project_relevance(project_texts, required_skills)
    kw_score = compute_keyword_match(resume_text, jd_keywords)

    overall = round(
        skill_score * 0.40 +
        exp_score * 0.25 +
        edu_score * 0.15 +
        proj_score * 0.10 +
        kw_score * 0.10,
        1
    )

    ats = compute_ats_score(resume_text, candidate_data, jd_keywords)
    quality = compute_resume_quality(candidate_data, resume_text)
    tech_score = compute_technical_score(candidate_data.skills, resume_text)
    employability = compute_employability(skill_score, exp_score, edu_score, quality)

    skill_gap = build_skill_gap_analysis(missing, required_skills)
    recommendations = generate_recommendations(missing, exp_score, edu_score, overall)
    suggestions = generate_improvement_suggestions(candidate_data, resume_text)

    kw_opt = [kw for kw in jd_keywords if kw.lower() not in resume_text.lower()][:10]

    return {
        "resume_id": resume_id,
        "job_description_id": jd_id,
        "overall_match_score": overall,
        "skill_match_score": skill_score,
        "experience_match_score": exp_score,
        "education_match_score": edu_score,
        "project_relevance_score": proj_score,
        "keyword_match_score": kw_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_details": skill_details,
        "skill_gap_analysis": skill_gap,
        "recommendations": recommendations,
        "improvement_suggestions": suggestions,
        "ats_compatibility": ats,
        "keyword_optimization": kw_opt,
        "scorecard": ScoreCard(
            ats_score=ats,
            resume_quality_score=quality,
            technical_skill_score=tech_score,
            employability_score=employability,
        ),
    }

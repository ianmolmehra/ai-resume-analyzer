import re
from typing import List, Dict, Optional
from schemas.job_description import JobDescriptionCreate, JobDescriptionResponse
from services.skill_extractor import extract_skills, SKILL_DATABASE
from utils.text_processor import clean_text, extract_years_of_experience


EDUCATION_REQUIREMENTS = {
    "phd": "PhD",
    "doctorate": "PhD",
    "master": "Master's",
    "msc": "Master's",
    "m.tech": "M.Tech",
    "mba": "MBA",
    "bachelor": "Bachelor's",
    "bsc": "Bachelor's",
    "b.tech": "B.Tech",
    "b.e": "B.E",
    "associate": "Associate",
    "diploma": "Diploma",
}


def split_required_preferred(text: str) -> tuple[str, str]:
    """Try to split JD text into required and preferred sections."""
    required_text = text
    preferred_text = ""

    preferred_patterns = [
        r'(?:preferred|nice to have|bonus|plus|advantageous|desired)[\s:]+(.*?)(?=required|must have|$)',
        r'(.*?)(?=preferred|nice to have|bonus|plus|advantageous)',
    ]

    for pattern in preferred_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            preferred_text = match.group(1)
            break

    return required_text, preferred_text


def extract_required_education(text: str) -> Optional[str]:
    text_lower = text.lower()
    for key, val in EDUCATION_REQUIREMENTS.items():
        if re.search(rf'\b{re.escape(key)}\b', text_lower):
            return val
    return None


def extract_keywords(text: str) -> List[str]:
    """Extract important keywords from JD for ATS matching."""
    # Common JD keywords beyond skills
    keyword_patterns = [
        r'\b(?:agile|scrum|kanban|lean|waterfall)\b',
        r'\b(?:team player|collaboration|communication|leadership|problem.solving)\b',
        r'\b(?:cross.functional|stakeholder|client.facing|customer.success)\b',
        r'\b(?:startup|enterprise|b2b|b2c|saas|paas|iaas)\b',
    ]
    keywords = []
    for pattern in keyword_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend([m.strip() for m in matches])

    # Also include skill names as keywords
    skills = extract_skills(text)
    keywords.extend([s.name for s in skills])

    return list(dict.fromkeys(keywords))  # deduplicate preserving order


def analyze_job_description(text: str, title: str = None, company: str = None) -> Dict:
    cleaned = clean_text(text)

    required_text, preferred_text = split_required_preferred(cleaned)

    required_skills_raw = extract_skills(required_text)
    preferred_skills_raw = extract_skills(preferred_text) if preferred_text else []

    # High confidence = required, lower = preferred
    required_skills = [s.name for s in required_skills_raw if s.confidence_score >= 0.65]
    preferred_skills = [s.name for s in preferred_skills_raw if s.name not in required_skills]

    experience_years = extract_years_of_experience(cleaned)
    education = extract_required_education(cleaned)
    keywords = extract_keywords(cleaned)

    return {
        "title": title,
        "company": company,
        "raw_text": text,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_required": experience_years,
        "education_required": education,
        "keywords": keywords,
    }

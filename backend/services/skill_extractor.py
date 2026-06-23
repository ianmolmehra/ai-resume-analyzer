import re
from typing import List, Dict, Tuple
from schemas.resume import SkillWithConfidence

# Master skill dictionary: skill_name -> {category, aliases, weight}
SKILL_DATABASE: Dict[str, Dict] = {
    # Programming
    "Python": {"category": "Programming", "aliases": ["python3", "py"], "weight": 1.0},
    "Java": {"category": "Programming", "aliases": ["java8", "java11", "java17"], "weight": 1.0},
    "C++": {"category": "Programming", "aliases": ["cpp", "c plus plus"], "weight": 1.0},
    "C": {"category": "Programming", "aliases": [], "weight": 0.8},
    "C#": {"category": "Programming", "aliases": ["csharp", "c sharp"], "weight": 1.0},
    "JavaScript": {"category": "Programming", "aliases": ["js", "es6", "es2015", "ecmascript"], "weight": 1.0},
    "TypeScript": {"category": "Programming", "aliases": ["ts"], "weight": 1.0},
    "Go": {"category": "Programming", "aliases": ["golang"], "weight": 1.0},
    "Rust": {"category": "Programming", "aliases": [], "weight": 1.0},
    "Ruby": {"category": "Programming", "aliases": ["ruby on rails", "ror"], "weight": 1.0},
    "PHP": {"category": "Programming", "aliases": [], "weight": 0.9},
    "Swift": {"category": "Programming", "aliases": [], "weight": 1.0},
    "Kotlin": {"category": "Programming", "aliases": [], "weight": 1.0},
    "R": {"category": "Programming", "aliases": ["r programming", "r language"], "weight": 0.9},
    "Scala": {"category": "Programming", "aliases": [], "weight": 1.0},
    "MATLAB": {"category": "Programming", "aliases": [], "weight": 0.9},
    "Shell": {"category": "Programming", "aliases": ["bash", "shell scripting", "bash scripting"], "weight": 0.9},

    # Databases
    "SQL": {"category": "Database", "aliases": ["structured query language"], "weight": 1.0},
    "MySQL": {"category": "Database", "aliases": [], "weight": 1.0},
    "PostgreSQL": {"category": "Database", "aliases": ["postgres"], "weight": 1.0},
    "MongoDB": {"category": "Database", "aliases": ["mongo"], "weight": 1.0},
    "Redis": {"category": "Database", "aliases": [], "weight": 1.0},
    "SQLite": {"category": "Database", "aliases": [], "weight": 0.8},
    "Oracle": {"category": "Database", "aliases": ["oracle db", "oracle database"], "weight": 1.0},
    "Cassandra": {"category": "Database", "aliases": ["apache cassandra"], "weight": 1.0},
    "Elasticsearch": {"category": "Database", "aliases": ["elastic search", "elastic"], "weight": 1.0},
    "DynamoDB": {"category": "Database", "aliases": ["dynamodb"], "weight": 1.0},
    "Neo4j": {"category": "Database", "aliases": [], "weight": 0.9},
    "Firebase": {"category": "Database", "aliases": [], "weight": 0.9},

    # Data Analytics
    "Excel": {"category": "Data Analytics", "aliases": ["microsoft excel", "ms excel", "advanced excel"], "weight": 0.9},
    "Power BI": {"category": "Data Analytics", "aliases": ["powerbi", "power bi"], "weight": 1.0},
    "Tableau": {"category": "Data Analytics", "aliases": [], "weight": 1.0},
    "Pandas": {"category": "Data Analytics", "aliases": [], "weight": 1.0},
    "NumPy": {"category": "Data Analytics", "aliases": ["numpy"], "weight": 1.0},
    "Matplotlib": {"category": "Data Analytics", "aliases": [], "weight": 0.9},
    "Seaborn": {"category": "Data Analytics", "aliases": [], "weight": 0.9},
    "Plotly": {"category": "Data Analytics", "aliases": [], "weight": 0.9},
    "Looker": {"category": "Data Analytics", "aliases": [], "weight": 0.9},
    "Qlik": {"category": "Data Analytics", "aliases": ["qlikview", "qlik sense"], "weight": 0.9},
    "SPSS": {"category": "Data Analytics", "aliases": [], "weight": 0.8},
    "SAS": {"category": "Data Analytics", "aliases": [], "weight": 0.9},

    # AI/ML
    "Machine Learning": {"category": "AI/ML", "aliases": ["ml", "machine-learning"], "weight": 1.0},
    "Deep Learning": {"category": "AI/ML", "aliases": ["dl", "deep-learning"], "weight": 1.0},
    "NLP": {"category": "AI/ML", "aliases": ["natural language processing", "natural-language processing"], "weight": 1.0},
    "Computer Vision": {"category": "AI/ML", "aliases": ["cv", "image processing"], "weight": 1.0},
    "TensorFlow": {"category": "AI/ML", "aliases": ["tf"], "weight": 1.0},
    "PyTorch": {"category": "AI/ML", "aliases": ["torch"], "weight": 1.0},
    "Scikit-learn": {"category": "AI/ML", "aliases": ["sklearn", "scikit learn"], "weight": 1.0},
    "Keras": {"category": "AI/ML", "aliases": [], "weight": 1.0},
    "Hugging Face": {"category": "AI/ML", "aliases": ["huggingface", "transformers"], "weight": 1.0},
    "OpenCV": {"category": "AI/ML", "aliases": ["cv2"], "weight": 1.0},
    "XGBoost": {"category": "AI/ML", "aliases": ["xgb"], "weight": 1.0},
    "LightGBM": {"category": "AI/ML", "aliases": ["lgbm"], "weight": 1.0},
    "NLTK": {"category": "AI/ML", "aliases": [], "weight": 0.9},
    "spaCy": {"category": "AI/ML", "aliases": ["spacy"], "weight": 0.9},
    "MLflow": {"category": "AI/ML", "aliases": [], "weight": 0.9},
    "LangChain": {"category": "AI/ML", "aliases": [], "weight": 1.0},

    # Cloud
    "AWS": {"category": "Cloud", "aliases": ["amazon web services", "amazon aws"], "weight": 1.0},
    "Azure": {"category": "Cloud", "aliases": ["microsoft azure", "ms azure"], "weight": 1.0},
    "GCP": {"category": "Cloud", "aliases": ["google cloud platform", "google cloud"], "weight": 1.0},
    "Heroku": {"category": "Cloud", "aliases": [], "weight": 0.8},
    "DigitalOcean": {"category": "Cloud", "aliases": ["digital ocean", "do"], "weight": 0.8},
    "Cloudflare": {"category": "Cloud", "aliases": [], "weight": 0.8},

    # DevOps
    "Docker": {"category": "DevOps", "aliases": ["containerization", "containers"], "weight": 1.0},
    "Kubernetes": {"category": "DevOps", "aliases": ["k8s", "kube"], "weight": 1.0},
    "Git": {"category": "DevOps", "aliases": ["github", "gitlab", "bitbucket", "version control"], "weight": 1.0},
    "CI/CD": {"category": "DevOps", "aliases": ["cicd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci"], "weight": 1.0},
    "Terraform": {"category": "DevOps", "aliases": [], "weight": 1.0},
    "Ansible": {"category": "DevOps", "aliases": [], "weight": 1.0},
    "Linux": {"category": "DevOps", "aliases": ["unix", "ubuntu", "centos", "rhel", "debian"], "weight": 0.9},
    "Nginx": {"category": "DevOps", "aliases": [], "weight": 0.9},

    # Frameworks
    "React": {"category": "Framework", "aliases": ["reactjs", "react.js"], "weight": 1.0},
    "Angular": {"category": "Framework", "aliases": ["angularjs", "angular.js"], "weight": 1.0},
    "Vue": {"category": "Framework", "aliases": ["vuejs", "vue.js"], "weight": 1.0},
    "Node.js": {"category": "Framework", "aliases": ["nodejs", "node"], "weight": 1.0},
    "Django": {"category": "Framework", "aliases": [], "weight": 1.0},
    "Flask": {"category": "Framework", "aliases": [], "weight": 1.0},
    "FastAPI": {"category": "Framework", "aliases": [], "weight": 1.0},
    "Spring": {"category": "Framework", "aliases": ["spring boot", "spring framework"], "weight": 1.0},
    "Express": {"category": "Framework", "aliases": ["express.js", "expressjs"], "weight": 1.0},
    "Next.js": {"category": "Framework", "aliases": ["nextjs"], "weight": 1.0},
    "GraphQL": {"category": "Framework", "aliases": [], "weight": 1.0},
    "REST API": {"category": "Framework", "aliases": ["restful api", "rest apis", "restful", "restful apis"], "weight": 0.9},
    "Microservices": {"category": "Framework", "aliases": ["micro-services", "microservice"], "weight": 0.9},
    "Apache Spark": {"category": "Framework", "aliases": ["spark", "pyspark"], "weight": 1.0},
    "Hadoop": {"category": "Framework", "aliases": ["apache hadoop", "hdfs"], "weight": 1.0},
    "Kafka": {"category": "Framework", "aliases": ["apache kafka"], "weight": 1.0},
}

LEARNING_PATHS: Dict[str, List[Dict]] = {
    "Docker": [
        {"title": "Docker for Beginners", "level": "Beginner", "platform": "Docker Docs"},
        {"title": "Docker Compose", "level": "Intermediate", "platform": "Udemy"},
        {"title": "Container Orchestration", "level": "Advanced", "platform": "Kubernetes Docs"},
    ],
    "AWS": [
        {"title": "AWS Cloud Practitioner", "level": "Beginner", "platform": "AWS Training"},
        {"title": "AWS Solutions Architect Associate", "level": "Intermediate", "platform": "A Cloud Guru"},
        {"title": "AWS DevOps Professional", "level": "Advanced", "platform": "AWS Training"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Basics", "level": "Beginner", "platform": "Kubernetes.io"},
        {"title": "CKA Certification Prep", "level": "Intermediate", "platform": "Linux Foundation"},
        {"title": "Advanced Kubernetes Patterns", "level": "Advanced", "platform": "O'Reilly"},
    ],
    "Machine Learning": [
        {"title": "ML Crash Course", "level": "Beginner", "platform": "Google"},
        {"title": "Machine Learning Specialization", "level": "Intermediate", "platform": "Coursera (Andrew Ng)"},
        {"title": "Advanced ML Techniques", "level": "Advanced", "platform": "Fast.ai"},
    ],
    "Deep Learning": [
        {"title": "Neural Networks & Deep Learning", "level": "Beginner", "platform": "Coursera"},
        {"title": "Deep Learning Specialization", "level": "Intermediate", "platform": "Coursera (Andrew Ng)"},
        {"title": "Advanced Deep Learning", "level": "Advanced", "platform": "Fast.ai"},
    ],
    "DEFAULT": [
        {"title": "Fundamentals Course", "level": "Beginner", "platform": "Coursera/Udemy"},
        {"title": "Intermediate Practice", "level": "Intermediate", "platform": "Pluralsight"},
        {"title": "Advanced Projects", "level": "Advanced", "platform": "GitHub"},
    ]
}


def build_skill_patterns() -> List[Tuple[str, str, str]]:
    """Returns list of (pattern, canonical_name, category)"""
    patterns = []
    for skill_name, info in SKILL_DATABASE.items():
        all_names = [skill_name] + info.get("aliases", [])
        category = info["category"]
        for name in all_names:
            escaped = re.escape(name)
            if len(name) <= 3:
                pattern = rf'(?<![A-Za-z]){escaped}(?![A-Za-z])'
            else:
                pattern = rf'\b{escaped}\b'
            patterns.append((pattern, skill_name, category))
    return patterns


SKILL_PATTERNS = build_skill_patterns()


def extract_skills(text: str) -> List[SkillWithConfidence]:
    """Extract skills from text using pattern matching."""
    text_lower = text.lower()
    found: Dict[str, dict] = {}

    for pattern, canonical, category in SKILL_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            count = len(matches)
            if canonical not in found:
                confidence = min(0.95, 0.6 + (count * 0.1))
                proficiency = "Intermediate"
                if count >= 5:
                    proficiency = "Advanced"
                    confidence = min(0.98, confidence + 0.1)
                elif count == 1:
                    proficiency = "Beginner"
                    confidence = max(0.55, confidence - 0.1)

                found[canonical] = {
                    "name": canonical,
                    "category": category,
                    "confidence_score": confidence,
                    "proficiency_level": proficiency,
                    "count": count,
                }
            else:
                # Boost confidence if seen again
                found[canonical]["count"] += count
                found[canonical]["confidence_score"] = min(0.99, found[canonical]["confidence_score"] + 0.05)

    result = [SkillWithConfidence(**{k: v for k, v in s.items() if k != "count"}) for s in found.values()]
    result.sort(key=lambda x: x.confidence_score, reverse=True)
    return result


def get_skill_categories(skills: List[SkillWithConfidence]) -> Dict[str, List[str]]:
    categories: Dict[str, List[str]] = {}
    for skill in skills:
        categories.setdefault(skill.category, []).append(skill.name)
    return categories


def get_learning_path(skill_name: str) -> List[Dict]:
    return LEARNING_PATHS.get(skill_name, LEARNING_PATHS["DEFAULT"])


def get_all_skills() -> List[Dict]:
    return [{"name": k, "category": v["category"]} for k, v in SKILL_DATABASE.items()]

-- ============================================================
--  AI Resume Analyzer — MySQL Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS resume_analyzer
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE resume_analyzer;

-- ── Candidates ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS candidates (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(255)  NOT NULL,
    email         VARCHAR(255)  UNIQUE,
    phone         VARCHAR(50),
    linkedin_url  VARCHAR(500),
    github_url    VARCHAR(500),
    location      VARCHAR(255),
    summary       TEXT,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- ── Resumes ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resumes (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id           INT NOT NULL,
    filename               VARCHAR(500) NOT NULL,
    file_path              VARCHAR(1000) NOT NULL,
    file_type              VARCHAR(10),
    file_size_kb           FLOAT,
    raw_text               LONGTEXT,
    education              JSON,
    experience             JSON,
    projects               JSON,
    certifications         JSON,
    ats_score              FLOAT DEFAULT 0,
    resume_quality_score   FLOAT DEFAULT 0,
    technical_skill_score  FLOAT DEFAULT 0,
    employability_score    FLOAT DEFAULT 0,
    total_experience_years FLOAT DEFAULT 0,
    highest_education      VARCHAR(255),
    status                 VARCHAR(50) DEFAULT 'parsed',
    created_at             DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    INDEX idx_candidate (candidate_id),
    INDEX idx_ats (ats_score),
    INDEX idx_employability (employability_score)
) ENGINE=InnoDB;

-- ── Skills ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS skills (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    category   VARCHAR(50)  DEFAULT 'Other',
    aliases    VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_category (category)
) ENGINE=InnoDB;

-- ── Candidate Skills (junction) ───────────────────────────────
CREATE TABLE IF NOT EXISTS candidate_skills (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id      INT NOT NULL,
    skill_id          INT NOT NULL,
    confidence_score  FLOAT DEFAULT 0,
    years_of_experience FLOAT DEFAULT 0,
    proficiency_level VARCHAR(50) DEFAULT 'Beginner',
    source            VARCHAR(100),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_cand_skill (candidate_id, skill_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id)     REFERENCES skills(id)     ON DELETE CASCADE,
    INDEX idx_candidate (candidate_id),
    INDEX idx_skill (skill_id)
) ENGINE=InnoDB;

-- ── Job Descriptions ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_descriptions (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    title               VARCHAR(255),
    company             VARCHAR(255),
    raw_text            LONGTEXT NOT NULL,
    required_skills     JSON,
    preferred_skills    JSON,
    experience_required FLOAT DEFAULT 0,
    education_required  VARCHAR(255),
    keywords            JSON,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_company (company)
) ENGINE=InnoDB;

-- ── Match Reports ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS match_reports (
    id                       INT AUTO_INCREMENT PRIMARY KEY,
    resume_id                INT NOT NULL,
    job_description_id       INT NOT NULL,
    overall_match_score      FLOAT DEFAULT 0,
    skill_match_score        FLOAT DEFAULT 0,
    experience_match_score   FLOAT DEFAULT 0,
    education_match_score    FLOAT DEFAULT 0,
    project_relevance_score  FLOAT DEFAULT 0,
    keyword_match_score      FLOAT DEFAULT 0,
    matched_skills           JSON,
    missing_skills           JSON,
    skill_gap_analysis       JSON,
    recommendations          JSON,
    improvement_suggestions  JSON,
    ats_compatibility        FLOAT DEFAULT 0,
    keyword_optimization     JSON,
    report_path              VARCHAR(1000),
    created_at               DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id)          REFERENCES resumes(id)          ON DELETE CASCADE,
    FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE,
    INDEX idx_resume (resume_id),
    INDEX idx_overall (overall_match_score)
) ENGINE=InnoDB;

-- ── Analytics Events ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analytics (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    event_type  VARCHAR(100),
    metadata    JSON,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event (event_type),
    INDEX idx_date  (created_at)
) ENGINE=InnoDB;

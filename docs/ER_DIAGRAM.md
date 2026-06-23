# Database ER Diagram

```
┌─────────────────────┐         ┌───────────────────────────┐
│      candidates     │         │          resumes           │
├─────────────────────┤         ├───────────────────────────┤
│ PK  id              │◄────────│ FK  candidate_id           │
│     full_name       │  1   N  │ PK  id                     │
│     email (unique)  │         │     filename               │
│     phone           │         │     file_path              │
│     linkedin_url    │         │     file_type              │
│     github_url      │         │     raw_text               │
│     location        │         │     education   (JSON)     │
│     summary         │         │     experience  (JSON)     │
│     created_at      │         │     projects    (JSON)     │
└─────────────────────┘         │     certifications (JSON)  │
           │                    │     ats_score              │
           │ 1                  │     resume_quality_score   │
           │                    │     technical_skill_score  │
           │ N                  │     employability_score    │
┌─────────────────────┐         │     total_experience_years │
│  candidate_skills   │         │     highest_education      │
├─────────────────────┤         │     status                 │
│ FK  candidate_id    │         │     created_at             │
│ FK  skill_id        │         └─────────────┬─────────────┘
│     confidence_score│                       │ 1
│     proficiency_lvl │                       │
│     created_at      │                       │ N
└──────────┬──────────┘         ┌─────────────▼─────────────┐
           │                    │       match_reports         │
           │ N                  ├───────────────────────────┤
           │ 1                  │ PK  id                     │
┌──────────▼──────────┐         │ FK  resume_id              │
│        skills       │         │ FK  job_description_id     │
├─────────────────────┤         │     overall_match_score    │
│ PK  id              │         │     skill_match_score      │
│     name (unique)   │         │     experience_match_score │
│     category        │         │     education_match_score  │
│     aliases         │         │     project_relevance_score│
│     created_at      │         │     keyword_match_score    │
└─────────────────────┘         │     matched_skills  (JSON) │
                                │     missing_skills  (JSON) │
┌─────────────────────┐         │     skill_gap_analysis(JSON│
│  job_descriptions   │         │     recommendations (JSON) │
├─────────────────────┤         │     ats_compatibility      │
│ PK  id              │◄──── N  │     report_path            │
│     title           │    1    │     created_at             │
│     company         │         └───────────────────────────┘
│     raw_text        │
│     required_skills │         ┌───────────────────────────┐
│     preferred_skills│         │         analytics          │
│     experience_req  │         ├───────────────────────────┤
│     education_req   │         │ PK  id                     │
│     keywords (JSON) │         │     event_type             │
│     created_at      │         │     metadata    (JSON)     │
└─────────────────────┘         │     created_at             │
                                └───────────────────────────┘
```

## Relationships

| Relationship | Type | Description |
|---|---|---|
| candidates → resumes | 1:N | One candidate can have multiple resumes |
| candidates → candidate_skills | 1:N | One candidate has many skills |
| skills → candidate_skills | 1:N | One skill can belong to many candidates |
| resumes → match_reports | 1:N | One resume can be matched against many JDs |
| job_descriptions → match_reports | 1:N | One JD can be matched against many resumes |

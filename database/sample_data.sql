USE resume_analyzer;

-- ── Sample Candidates ─────────────────────────────────────────
INSERT INTO candidates (full_name, email, phone, linkedin_url, github_url, location) VALUES
('Anmol Mehra',    'anmol@example.com',   '+91-9876543210', 'linkedin.com/in/anmolmehra', 'github.com/anmolmehra', 'Bangalore, India'),
('Priya Sharma',   'priya@example.com',   '+91-9123456789', 'linkedin.com/in/priyasharma','github.com/priyasharma','Mumbai, India'),
('Rahul Verma',    'rahul@example.com',   '+91-9988776655', 'linkedin.com/in/rahulverma', 'github.com/rahulverma', 'Delhi, India'),
('Sara Khan',      'sara@example.com',    '+91-9871234567', 'linkedin.com/in/sarakhan',   'github.com/sarakhan',   'Hyderabad, India'),
('David Chen',     'david@example.com',   '+1-4155551234',  'linkedin.com/in/davidchen',  'github.com/davidchen',  'San Francisco, USA');

-- ── Sample Skills ─────────────────────────────────────────────
INSERT INTO skills (name, category) VALUES
('Python',         'Programming'),  ('Java',          'Programming'),
('JavaScript',     'Programming'),  ('SQL',           'Database'),
('MySQL',          'Database'),     ('PostgreSQL',    'Database'),
('Machine Learning','AI/ML'),       ('Deep Learning', 'AI/ML'),
('TensorFlow',     'AI/ML'),        ('Scikit-learn',  'AI/ML'),
('AWS',            'Cloud'),        ('Docker',        'DevOps'),
('Git',            'DevOps'),       ('React',         'Framework'),
('FastAPI',        'Framework'),    ('Power BI',      'Data Analytics'),
('Pandas',         'Data Analytics'),('NLP',          'AI/ML'),
('Kubernetes',     'DevOps'),       ('Azure',         'Cloud');

-- ── Sample Resumes ────────────────────────────────────────────
INSERT INTO resumes (candidate_id, filename, file_path, file_type, file_size_kb,
    ats_score, resume_quality_score, technical_skill_score, employability_score,
    total_experience_years, highest_education, status) VALUES
(1, 'anmol_resume.pdf',  '/uploads/anmol_resume.pdf',  '.pdf', 245.3, 82.5, 78.0, 88.0, 83.2, 3.5, "B.Tech",  'parsed'),
(2, 'priya_resume.pdf',  '/uploads/priya_resume.pdf',  '.pdf', 198.7, 76.0, 72.5, 91.0, 79.8, 5.0, "Master's",'parsed'),
(3, 'rahul_resume.docx', '/uploads/rahul_resume.docx', '.docx',312.1, 65.0, 68.0, 74.5, 69.2, 2.0, "B.Tech",  'parsed'),
(4, 'sara_resume.pdf',   '/uploads/sara_resume.pdf',   '.pdf', 178.4, 88.0, 85.5, 79.0, 84.6, 4.5, "Master's",'parsed'),
(5, 'david_resume.pdf',  '/uploads/david_resume.pdf',  '.pdf', 267.9, 91.0, 89.0, 94.0, 91.5, 7.0, "PhD",     'parsed');

-- ── Sample Candidate Skills ───────────────────────────────────
INSERT INTO candidate_skills (candidate_id, skill_id, confidence_score, proficiency_level) VALUES
(1,1,0.95,'Expert'),(1,4,0.90,'Advanced'),(1,8,0.82,'Intermediate'),(1,9,0.78,'Intermediate'),
(1,11,0.70,'Beginner'),(1,12,0.75,'Intermediate'),(1,13,0.88,'Advanced'),(1,15,0.85,'Advanced'),
(2,1,0.92,'Expert'),(2,7,0.88,'Advanced'),(2,8,0.85,'Advanced'),(2,9,0.90,'Advanced'),
(2,10,0.87,'Advanced'),(2,18,0.80,'Intermediate'),(2,16,0.72,'Intermediate'),
(3,2,0.88,'Advanced'),(3,4,0.85,'Advanced'),(3,5,0.80,'Intermediate'),(3,14,0.75,'Intermediate'),
(3,13,0.82,'Advanced'),
(4,1,0.93,'Expert'),(4,4,0.91,'Expert'),(4,6,0.85,'Advanced'),(4,7,0.88,'Advanced'),
(4,17,0.90,'Expert'),(4,18,0.85,'Advanced'),(4,11,0.78,'Intermediate'),
(5,1,0.98,'Expert'),(5,3,0.90,'Advanced'),(5,7,0.95,'Expert'),(5,9,0.92,'Expert'),
(5,11,0.88,'Advanced'),(5,12,0.85,'Advanced'),(5,19,0.80,'Intermediate'),(5,20,0.75,'Intermediate');

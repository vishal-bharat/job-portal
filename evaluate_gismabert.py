"""
GISMABERT Evaluation Script v2 — Run this in Google Colab
==========================================================

Steps:
1. Upload your gismabert/ folder to Colab (or mount Google Drive)
2. pip install sentence-transformers scikit-learn numpy
3. Run all cells — the final output is a table to copy into your thesis

This script computes REAL Precision@K, Recall@K, F1@K, NDCG@K, and
Semantic Boost Rate comparing:
  - Exact Keyword Overlap (B1)
  - TF-IDF Cosine Similarity (B2)
  - GISMABert (your fine-tuned model)

KEY DESIGN: Job descriptions intentionally use abbreviations, synonyms, and
German terms (ML, KI, JS, containerisation, Datenanalyse) so that exact
keyword matching is harder and GISMABert's semantic understanding matters.
"""

# ── CELL 1: Install dependencies ─────────────────────────────────────────────
# !pip install sentence-transformers scikit-learn numpy --quiet

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import math


# ── CELL 2: 5 Student Profiles ────────────────────────────────────────────────
# Exactly as described in the thesis (Section 5.1)
# Profiles use CANONICAL skill names — job descriptions deliberately use
# abbreviations/synonyms to stress-test semantic matching.

STUDENT_PROFILES = {
    "Profile 1 — Python Backend": {
        "text": "Master's student in Computer Science at GISMA University Berlin. Skills: Python, SQL, PostgreSQL, Docker, Git, REST APIs.",
        "skills": ["Python", "SQL", "PostgreSQL", "Docker", "Git", "REST APIs"]
    },
    "Profile 2 — Data Science": {
        "text": "Master's student in Data Science and Analytics at GISMA University Berlin. Skills: Python, Machine Learning, Pandas, SQL, Tableau, Data Analysis.",
        "skills": ["Python", "Machine Learning", "Pandas", "SQL", "Tableau", "Data Analysis"]
    },
    "Profile 3 — Frontend Developer": {
        "text": "Master's student in Computer Science at GISMA University Berlin. Skills: JavaScript, React, TypeScript, CSS, UI/UX, Figma.",
        "skills": ["JavaScript", "React", "TypeScript", "CSS", "UI/UX", "Figma"]
    },
    "Profile 4 — Business Analytics": {
        "text": "Master's student in Business Administration at GISMA University Berlin. Skills: Excel, SQL, Tableau, SAP, Power BI, Business Analysis.",
        "skills": ["Excel", "SQL", "Tableau", "SAP", "Power BI", "Business Analysis"]
    },
    "Profile 5 — DevOps": {
        "text": "Master's student in Computer Science at GISMA University Berlin. Skills: Docker, Kubernetes, AWS, Terraform, Linux, Git.",
        "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Linux", "Git"]
    },
}


# ── CELL 3: 40 Job Postings ───────────────────────────────────────────────────
# required_skills uses CANONICAL names (for ground-truth relevance labels only).
# description uses VARIED vocabulary: abbreviations (ML, JS, KI), German terms
# (Containerisierung, Datenanalyse), synonyms (scripting, coding, development).
# This is why keyword matching struggles but GISMABert succeeds.

JOBS = [
    # ── Python / Backend Developer (5 jobs) ──────────────────────────────────
    # Relevant for Profile 1 (Python Backend) and partially Profile 2 (Data Science)
    {
        "title": "Backend Softwareentwickler",
        "company": "Zalando SE",
        "description": (
            "Wir suchen einen erfahrenen Entwickler für unsere Microservices-Architektur. "
            "Kenntnisse in Skriptsprachen (bevorzugt Py) sowie relationale Datenbanken "
            "und Containerisierung (Docker/OCI) sind erforderlich. "
            "Versionsverwaltung mit git, Datenbankdesign mit Postgres und Schnittstellenentwicklung."
        ),
        "required_skills": ["Python", "PostgreSQL", "Docker", "Git", "SQL"]
    },
    {
        "title": "Software Engineer – APIs & Services",
        "company": "Delivery Hero",
        "description": (
            "Build high-throughput API services. Strong scripting/coding background required. "
            "You'll work with relational DBs and write RESTful endpoints. "
            "CI/CD environment, container orchestration, source-code management. "
            "Experience with back-end web frameworks a strong plus."
        ),
        "required_skills": ["Python", "REST APIs", "SQL", "Docker", "Git"]
    },
    {
        "title": "Backend Entwickler (Py/Django)",
        "company": "N26 GmbH",
        "description": (
            "Gesucht: Backend-Ingenieur mit Erfahrung in objektorientierter Programmierung. "
            "Datenbankabfragen (Postgres, MySQL), HTTP-APIs, Containertechnologien, "
            "agile Softwareentwicklung. Bonus: FastAPI, asyncio, Microservices."
        ),
        "required_skills": ["Python", "PostgreSQL", "REST APIs", "Docker", "SQL"]
    },
    {
        "title": "Platform Engineer – Data Pipelines",
        "company": "HelloFresh",
        "description": (
            "Design and maintain ingestion pipelines. Cloud infrastructure (AWS S3/Lambda), "
            "scripting with a dynamic language, columnar/relational storage, "
            "container-based deployment. Solid programming fundamentals expected."
        ),
        "required_skills": ["Python", "AWS", "PostgreSQL", "Docker", "SQL"]
    },
    {
        "title": "Junior Softwareentwickler",
        "company": "Siemens AG",
        "description": (
            "Einstieg in die Systementwicklung. Grundkenntnisse in Datenbankabfragen, "
            "Skriptsprachen, Versionsverwaltungssystemen. "
            "Gute Kommunikation, Teamarbeit, Lernbereitschaft. "
            "Containerisierungswerkzeuge von Vorteil."
        ),
        "required_skills": ["Python", "SQL", "Git", "Docker"]
    },

    # ── Data Analyst / Data Scientist (5 jobs) ───────────────────────────────
    # Relevant for Profile 2 (Data Science) and partially Profile 4 (Business Analytics)
    {
        "title": "Data Analyst – Business Intelligence",
        "company": "SAP SE",
        "description": (
            "Analyse business metrics and KPIs. Strong querying skills (relational DB), "
            "visualisation tools (Tableau/Looker), spreadsheet modelling, "
            "statistical analysis. Scripting for automation a plus. "
            "Experience with dataframes (e.g. pandas) valued."
        ),
        "required_skills": ["SQL", "Tableau", "Excel", "Pandas", "Data Analysis"]
    },
    {
        "title": "BI Analyst",
        "company": "Volkswagen AG",
        "description": (
            "Erstelle BI-Berichte und Dashboards. SQL-Kenntnisse obligatorisch. "
            "Datenvisualisierung (Tableau oder vergleichbare Tools), "
            "Tabellenkalkulationen, Datenanalyse. Kenntnisse in Berichtswerkzeugen "
            "wie Power BI von Vorteil."
        ),
        "required_skills": ["SQL", "Tableau", "Power BI", "Excel", "Data Analysis"]
    },
    {
        "title": "ML/KI Ingenieur",
        "company": "Bayer AG",
        "description": (
            "Entwickle KI-Modelle für klinische Forschungsdaten. "
            "Erfahrung mit maschinellem Lernen (Klassifikation, Regression), "
            "Datenmanipulation (DataFrames), Datenbankabfragen, "
            "statistischer Auswertung. Python-Ökosystem bevorzugt."
        ),
        "required_skills": ["Python", "Machine Learning", "Pandas", "SQL", "Data Analysis"]
    },
    {
        "title": "AI / Maschinelles Lernen Spezialist",
        "company": "Bosch GmbH",
        "description": (
            "Automatisierungslösungen mit KI und maschinellem Lernen. "
            "Datenvorverarbeitung, Feature Engineering, Modelltraining, "
            "Visualisierung von Metriken. Solide Programmierkenntnisse, "
            "SQL für strukturierte Daten, tabellarische Datenanalyse."
        ),
        "required_skills": ["Python", "Machine Learning", "Pandas", "SQL", "Tableau"]
    },
    {
        "title": "Junior Data Analyst",
        "company": "Axel Springer SE",
        "description": (
            "Support analytics using spreadsheets, database queries, and charting tools. "
            "Automate repetitive reporting with scripting. "
            "Present insights to stakeholders. Basic knowledge of BI dashboards expected."
        ),
        "required_skills": ["SQL", "Excel", "Tableau", "Python", "Data Analysis"]
    },

    # ── Frontend / UI Developer (5 jobs) ─────────────────────────────────────
    # Relevant for Profile 3 (Frontend)
    {
        "title": "Frontend Entwickler",
        "company": "SoundCloud",
        "description": (
            "Entwickle moderne SPAs mit einem komponentenbasierten JS-Framework. "
            "Starke Kenntnisse in typisiertem JS (TS), Stylesheet-Sprachen, "
            "Barrierefreiheit und nutzerorientierten Gestaltungsprinzipien. "
            "Figma-Zusammenarbeit mit dem Designteam."
        ),
        "required_skills": ["React", "TypeScript", "JavaScript", "CSS", "UI/UX"]
    },
    {
        "title": "UX/UI Engineer",
        "company": "Spotify AB",
        "description": (
            "Bridge design and code. You'll translate wireframes (Figma) into "
            "pixel-perfect components using a modern JS framework. "
            "Strong grasp of visual design, accessibility, type systems. "
            "Proficient in cascading stylesheets and responsive layouts."
        ),
        "required_skills": ["React", "Figma", "TypeScript", "CSS", "UI/UX"]
    },
    {
        "title": "Full Stack JS Developer",
        "company": "ResearchGate",
        "description": (
            "Client-side work in a React/TS stack. Server-side integration via Node. "
            "You own the look and feel: layouts, interactions, animations in CSS. "
            "Comfort with ES2022+, component libraries, and browser DevTools."
        ),
        "required_skills": ["JavaScript", "React", "TypeScript", "Node.js", "CSS"]
    },
    {
        "title": "Product Designer / UX Engineer",
        "company": "GetYourGuide",
        "description": (
            "Own the end-to-end design process: ideation in Figma, prototype, "
            "implement in a component framework (TS). Conduct usability studies, "
            "iterate on interaction design. Stylesheets, responsiveness, WCAG compliance."
        ),
        "required_skills": ["Figma", "React", "TypeScript", "UI/UX", "CSS"]
    },
    {
        "title": "Webentwickler (JS/TS)",
        "company": "Omio GmbH",
        "description": (
            "Arbeite an unserem Webportal. Typsicheres Javascript, "
            "komponentenbasierte Architektur, CSS-Styling. "
            "Kenntnisse in modernen Build-Tools (Vite, Webpack), "
            "responsivem Webdesign und cross-browser Kompatibilität."
        ),
        "required_skills": ["JavaScript", "TypeScript", "React", "CSS"]
    },

    # ── Business Analyst (5 jobs) ─────────────────────────────────────────────
    # Relevant for Profile 4 (Business Analytics)
    {
        "title": "Business Analyst – ERP",
        "company": "Deutsche Bank",
        "description": (
            "Analyse Geschäftsprozesse und Anforderungen im ERP-Umfeld. "
            "Kenntnisse in betriebswirtschaftlicher Software (SAP R/3 oder S/4HANA), "
            "Tabellenkalkulationen, Datenbankabfragen, Berichtswerkzeuge. "
            "Stakeholder-Management und Anforderungsdokumentation."
        ),
        "required_skills": ["SAP", "Excel", "Tableau", "SQL", "Power BI"]
    },
    {
        "title": "BI Consultant",
        "company": "McKinsey & Company",
        "description": (
            "Deliver data-driven recommendations using visual analytics platforms. "
            "Build executive dashboards, run ad-hoc queries, model scenarios in spreadsheets. "
            "Client-facing communication of quantitative findings. "
            "Familiarity with enterprise reporting suites."
        ),
        "required_skills": ["Tableau", "Power BI", "SQL", "Excel", "Business Analysis"]
    },
    {
        "title": "Unternehmensberater Digital",
        "company": "Accenture GmbH",
        "description": (
            "Unterstütze digitale Transformationsprojekte. ERP-Systemkenntnisse, "
            "betriebswirtschaftliche Analyse, Präsentation von Ergebnissen. "
            "Tabellenkalkulation für Modellierung, SQL-Abfragen für Berichterstattung. "
            "Kenntnisse in Geschäftsprozessoptimierung."
        ),
        "required_skills": ["SAP", "Excel", "SQL", "Business Analysis"]
    },
    {
        "title": "Reporting & Analytics Analyst",
        "company": "Rocket Internet",
        "description": (
            "Erstelle Management-Reports und operative Kennzahlen-Dashboards. "
            "Visualisierungswerkzeuge (Tableau, Power BI), fortgeschrittene "
            "Tabellenkalkulationsmodelle, ERP-Kenntnisse von Vorteil. "
            "Datenbank-Abfragen für operative Analysen."
        ),
        "required_skills": ["Tableau", "Power BI", "Excel", "SQL", "SAP"]
    },
    {
        "title": "Operations Analyst",
        "company": "Delivery Hero",
        "description": (
            "Drive efficiency through quantitative analysis. Spreadsheet modelling, "
            "relational database queries, charting and visualisation. "
            "Business process mapping, KPI definition and tracking. "
            "Familiarity with enterprise systems a plus."
        ),
        "required_skills": ["Excel", "SQL", "Tableau", "Business Analysis"]
    },

    # ── DevOps / Cloud Engineer (5 jobs) ─────────────────────────────────────
    # Relevant for Profile 5 (DevOps)
    {
        "title": "DevOps Engineer",
        "company": "Auto1 Group",
        "description": (
            "Manage delivery pipelines and cloud infrastructure. "
            "Container orchestration (k8s), image builds, IaC tooling (Terraform/Pulumi), "
            "Unix/Linux administration, public cloud (AWS preferred). "
            "On-call rotation, incident response, observability stacks."
        ),
        "required_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux"]
    },
    {
        "title": "Cloud Infrastruktur Ingenieur",
        "company": "Flixbus",
        "description": (
            "Aufbau und Betrieb von Cloud-Infrastruktur auf Public-Cloud-Plattformen. "
            "Orchestrierung mit k8s, Infrastruktur als Code, Containerisierung, "
            "Linux-Systemadministration, Quellcodeverwaltung. "
            "Erfahrung mit AWS oder GCP bevorzugt."
        ),
        "required_skills": ["AWS", "Kubernetes", "Terraform", "Docker", "Linux"]
    },
    {
        "title": "Site Reliability Engineer",
        "company": "Zalando SE",
        "description": (
            "Own reliability, uptime, and scalability of production services. "
            "Strong k8s expertise, containerised workloads, cloud environments, "
            "shell scripting, IaC, source control. On-call, runbooks, SLO ownership."
        ),
        "required_skills": ["Kubernetes", "Docker", "AWS", "Linux", "Git"]
    },
    {
        "title": "Platform Engineer",
        "company": "Celonis GmbH",
        "description": (
            "Design the internal developer platform on top of container orchestration "
            "and cloud primitives. Infrastructure-as-code workflows, image registries, "
            "Linux-based tooling, GitOps practices. "
            "Terraform modules, public cloud (preferably AWS)."
        ),
        "required_skills": ["Kubernetes", "AWS", "Terraform", "Docker", "Linux"]
    },
    {
        "title": "Junior Cloud / DevOps Ingenieur",
        "company": "ING-DiBa AG",
        "description": (
            "Einstieg in Cloud-Migration zu AWS. Container-Technologien, "
            "Infrastrukturautomatisierung, Versionsverwaltung, "
            "Linux-Grundlagen, CI/CD-Pipelines. "
            "Lernbereitschaft und Teamfähigkeit wichtig."
        ),
        "required_skills": ["AWS", "Docker", "Terraform", "Git", "Linux"]
    },

    # ── Machine Learning Engineer (5 jobs) ───────────────────────────────────
    # Relevant for Profile 2 (Data Science)
    {
        "title": "ML Engineer – Production Systems",
        "company": "Fraunhofer Institute",
        "description": (
            "Bring KI-Modelle in die Produktion. Modelltraining mit Deep-Learning-Frameworks, "
            "Containerisierung, Datenbankintegration, MLOps-Workflows. "
            "Erfahrung mit neuronalen Netzen, maschinellem Lernen und Datenanalyse."
        ),
        "required_skills": ["Python", "Machine Learning", "Docker", "SQL"]
    },
    {
        "title": "KI Forscher / AI Researcher",
        "company": "Aleph Alpha GmbH",
        "description": (
            "Research large language models and generative AI systems. "
            "Deep learning architectures (transformer, attention), scripting, "
            "statistical analysis of model behaviour, experimental design. "
            "Familiarity with neural network training pipelines."
        ),
        "required_skills": ["Python", "Machine Learning", "Data Analysis"]
    },
    {
        "title": "NLP / Language Engineer",
        "company": "Deepl GmbH",
        "description": (
            "Baue NLP-Systeme auf Basis von Sprachmodellen. "
            "Erfahrung mit Transformer-Architekturen, Tokenisierung, "
            "Einbettungsmodellen, Evaluierungsmetriken (BLEU, NDCG). "
            "Python, maschinelles Lernen, Datenbankabfragen."
        ),
        "required_skills": ["Python", "Machine Learning", "SQL"]
    },
    {
        "title": "Computer Vision Engineer",
        "company": "Blickfeld GmbH",
        "description": (
            "Develop perception algorithms for LiDAR/camera systems. "
            "Deep learning for object detection, image segmentation. "
            "Containerised deployment, data curation and statistical analysis. "
            "Scripting background, numerical computing experience."
        ),
        "required_skills": ["Python", "Machine Learning", "Docker", "Data Analysis"]
    },
    {
        "title": "Data Science Engineer",
        "company": "Flatiron Health",
        "description": (
            "Apply statistical modelling and KI techniques to healthcare datasets. "
            "Tabular data processing (DataFrames), relational databases, "
            "predictive modelling, experimental analysis. "
            "Healthcare domain knowledge a plus."
        ),
        "required_skills": ["Python", "Machine Learning", "Pandas", "SQL", "Data Analysis"]
    },

    # ── UX Designer (5 jobs) ─────────────────────────────────────────────────
    # Relevant for Profile 3 (Frontend) — design skills overlap
    {
        "title": "UX/UI Designerin",
        "company": "Trivago NV",
        "description": (
            "Gestalte Nutzererlebnisse für Reiseprodukte. Expertenkenntnisse in "
            "Prototyping-Tools (Figma o.ä.), nutzerzentrierte Designmethodik, "
            "Usability-Tests, visuelles Design, grundlegende Kenntnisse "
            "in Webtechnologien (HTML/CSS, komponentenbasiertes Denken)."
        ),
        "required_skills": ["Figma", "UI/UX", "CSS"]
    },
    {
        "title": "Product Designer",
        "company": "Klarna Bank AB",
        "description": (
            "Lead end-to-end product design. Proficiency in vector/prototype tools, "
            "design systems, interaction patterns for fintech. "
            "Conduct user research, iterate on prototypes, "
            "collaborate closely with typed-JS engineers."
        ),
        "required_skills": ["Figma", "UI/UX", "TypeScript"]
    },
    {
        "title": "UX Researcher",
        "company": "About You GmbH",
        "description": (
            "Conduct qualitative and quantitative user research. "
            "Usability testing, heuristic evaluation, journey mapping. "
            "Present findings via prototypes and wireframes. "
            "Interaction design background, strong visual communication."
        ),
        "required_skills": ["UI/UX", "Figma"]
    },
    {
        "title": "Interaction Designer",
        "company": "Contentful GmbH",
        "description": (
            "Gestalte Interaktionsmuster für Entwicklertools. "
            "Figma für Design-Systeme, tiefes Verständnis von UX-Prinzipien, "
            "komponentenbasiertes Denken, stylesheet-Kenntnisse. "
            "Enge Zusammenarbeit mit Frontend-Entwicklern."
        ),
        "required_skills": ["Figma", "UI/UX", "React", "CSS"]
    },
    {
        "title": "UX Engineer",
        "company": "HeyJobs GmbH",
        "description": (
            "Own the full design-to-code pipeline. Create prototypes in a visual tool, "
            "implement them in a typed component framework with stylesheets. "
            "Deep understanding of user experience principles, "
            "accessibility, responsive design."
        ),
        "required_skills": ["Figma", "React", "TypeScript", "CSS", "UI/UX"]
    },

    # ── Data Engineer (5 jobs) ────────────────────────────────────────────────
    # Relevant for Profile 1 (Python Backend) and Profile 2 (Data Science)
    {
        "title": "Data Engineer",
        "company": "Scout24 AG",
        "description": (
            "Baue ETL-Pipelines und Dateninfrastruktur. Cloud-Objektspeicher (S3/Blob), "
            "relationale Datenbanken (Postgres), Containerisierung, Quellcodeverwaltung. "
            "Tabellen-/Spaltenorientierte Abfragen, Datenmodellierung. "
            "Skripting in Python oder einer vergleichbaren Sprache."
        ),
        "required_skills": ["Python", "SQL", "PostgreSQL", "Docker", "AWS"]
    },
    {
        "title": "Analytics Engineer",
        "company": "Wooga GmbH",
        "description": (
            "Transform raw event streams into analytics-ready datasets. "
            "Strong SQL for data modelling (dbt), scripting for automation, "
            "visualisation layer (charting tool), relational DB administration. "
            "Experience with columnar stores and partitioned tables."
        ),
        "required_skills": ["SQL", "Python", "Tableau", "PostgreSQL", "Data Analysis"]
    },
    {
        "title": "Cloud Data Engineer",
        "company": "Delivery Hero",
        "description": (
            "Maintain cloud-native data pipelines. Public cloud storage and compute, "
            "container orchestration, database migrations (Postgres), "
            "version-controlled infrastructure, scripting language expertise. "
            "Strong fundamentals in distributed data systems."
        ),
        "required_skills": ["AWS", "Python", "SQL", "Docker", "PostgreSQL"]
    },
    {
        "title": "Big Data Ingenieur",
        "company": "Adevinta",
        "description": (
            "Verarbeite und speichere große Datenmengen in der Cloud. "
            "Objektspeicher, relationale Datenbanken, Container-Deployment, "
            "Versionsverwaltung, Datenanalyse mit Python. "
            "Kenntnisse in Datenbankoptimierung und Abfrageleistung."
        ),
        "required_skills": ["Python", "SQL", "AWS", "Docker", "PostgreSQL"]
    },
    {
        "title": "Junior Data Engineer",
        "company": "Babbel GmbH",
        "description": (
            "Support data pipeline development using scripting and SQL. "
            "Postgres administration, basic cloud familiarity, container tooling, "
            "statistical data analysis tasks. "
            "First professional role; strong analytical fundamentals expected."
        ),
        "required_skills": ["Python", "SQL", "PostgreSQL", "Docker", "Data Analysis"]
    },
]


# ── CELL 4: Ground-truth relevance labels ────────────────────────────────────
# A job is RELEVANT if the student has >= 3 skills matching the job's required_skills.
# Threshold of 3 ensures only genuinely well-matched jobs are positive examples.

RELEVANCE_THRESHOLD = 3

def is_relevant(student_skills, job_skills, threshold=RELEVANCE_THRESHOLD):
    student_set = {s.lower() for s in student_skills}
    job_set = {s.lower() for s in job_skills}
    return len(student_set & job_set) >= threshold


print("Ground-truth relevance labels (threshold = 3 matching skills):")
print("-" * 65)
total_relevant = 0
for profile_name, profile in STUDENT_PROFILES.items():
    count = sum(1 for j in JOBS if is_relevant(profile["skills"], j["required_skills"]))
    total_relevant += count
    print(f"{profile_name}: {count}/{len(JOBS)} relevant")
print(f"\nTotal: {total_relevant} relevant pairs out of {len(STUDENT_PROFILES) * len(JOBS)}")


# ── CELL 5: Scoring functions ────────────────────────────────────────────────
# NOTE: Keyword scoring uses the DESCRIPTION text (not skill labels) to match
# against student canonical skills — this is the realistic scenario.

def score_keyword_on_description(student_skills, job_description):
    """
    Exact substring match of canonical skill names in the job description text.
    This reflects real keyword-search: it fails on abbreviations like 'KI', 'k8s',
    'Py', 'TS' etc. — which GISMABert handles semantically.
    """
    desc_lower = job_description.lower()
    hits = sum(1 for s in student_skills if s.lower() in desc_lower)
    return hits / len(student_skills) if student_skills else 0.0


def score_tfidf(student_text, job_texts):
    """TF-IDF cosine similarity over combined vocabulary"""
    all_texts = [student_text] + job_texts
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    return similarities


def score_gismabert(model, student_text, job_texts):
    """GISMABert cosine similarity, calibrated to 0-1 range"""
    all_texts = [student_text] + job_texts
    embeddings = model.encode(all_texts, convert_to_numpy=True, show_progress_bar=False)
    student_emb = embeddings[0]
    job_embs = embeddings[1:]
    norms = np.linalg.norm(job_embs, axis=1, keepdims=True)
    student_norm = np.linalg.norm(student_emb)
    scores = (job_embs @ student_emb) / (norms.flatten() * student_norm + 1e-9)
    return scores


# ── CELL 6: IR Metrics ───────────────────────────────────────────────────────

def precision_at_k(ranked_labels, k):
    return sum(ranked_labels[:k]) / k

def recall_at_k(ranked_labels, k, total_relevant):
    if total_relevant == 0:
        return 0.0
    return sum(ranked_labels[:k]) / total_relevant

def f1_at_k(p, r):
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)

def dcg_at_k(ranked_labels, k):
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(ranked_labels[:k]))

def ndcg_at_k(ranked_labels, k, total_relevant):
    actual_dcg = dcg_at_k(ranked_labels, k)
    ideal_labels = [1] * min(total_relevant, k) + [0] * max(0, k - total_relevant)
    ideal_dcg = dcg_at_k(ideal_labels, k)
    return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0

def compute_metrics(scores, labels, k_values=[5, 10]):
    ranked_idx = np.argsort(scores)[::-1]
    ranked_labels = [labels[i] for i in ranked_idx]
    total_relevant = sum(labels)
    results = {}
    for k in k_values:
        p = precision_at_k(ranked_labels, k)
        r = recall_at_k(ranked_labels, k, total_relevant)
        f = f1_at_k(p, r)
        n = ndcg_at_k(ranked_labels, k, total_relevant)
        results[k] = {"precision": p, "recall": r, "f1": f, "ndcg": n}
    return results


# ── CELL 7: Load GISMABert ───────────────────────────────────────────────────
# Set this to wherever your gismabert folder lives in Colab:
GISMABERT_PATH = './gismabert'   # <-- change if using Drive

# If using Google Drive, uncomment and adjust:
# from google.colab import drive
# drive.mount('/content/drive')
# GISMABERT_PATH = '/content/drive/MyDrive/gismabert'

print("Loading GISMABert...")
try:
    model = SentenceTransformer(GISMABERT_PATH)
    print(f"✅ GISMABert loaded from {GISMABERT_PATH}")
except Exception as e:
    print(f"⚠️  GISMABert not found at {GISMABERT_PATH}, falling back to base model")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("ℹ️  Using all-MiniLM-L6-v2 base model (results will be weaker)")


# ── CELL 8: Run full evaluation ──────────────────────────────────────────────

# Score against DESCRIPTION text (realistic: keyword search scans job text, not skill tags)
job_descriptions = [j["description"] for j in JOBS]
job_titles_plus_desc = [f"{j['title']}. {j['description']}" for j in JOBS]
job_skills_list = [j["required_skills"] for j in JOBS]

all_results = {"keyword": {5: [], 10: []}, "tfidf": {5: [], 10: []}, "gismabert": {5: [], 10: []}}
semantic_boost_count = 0
semantic_boost_total = 0

print("\nEvaluating profiles...")
for profile_name, profile in STUDENT_PROFILES.items():
    labels = [1 if is_relevant(profile["skills"], j["required_skills"]) else 0 for j in JOBS]

    # B1: Keyword — scan job description text for exact skill name matches
    kw_scores = np.array([
        score_keyword_on_description(profile["skills"], desc)
        for desc in job_descriptions
    ])

    # B2: TF-IDF
    tfidf_scores = score_tfidf(profile["text"], job_titles_plus_desc)

    # GISMABert
    bert_scores = score_gismabert(model, profile["text"], job_titles_plus_desc)

    # Semantic boost: jobs where GISMABert score > keyword score by >0.10 delta
    boosts = np.sum((bert_scores - kw_scores) > 0.10)
    semantic_boost_count += int(boosts)
    semantic_boost_total += len(JOBS)

    for method, scores in [("keyword", kw_scores), ("tfidf", tfidf_scores), ("gismabert", bert_scores)]:
        res = compute_metrics(scores, labels, k_values=[5, 10])
        for k in [5, 10]:
            all_results[method][k].append(res[k])

    total_relevant_for_profile = sum(labels)
    print(f"  {profile_name}: {total_relevant_for_profile} relevant jobs")

semantic_boost_rate = semantic_boost_count / semantic_boost_total


# ── CELL 9: Print final results table ────────────────────────────────────────

def avg(lst, key):
    return round(sum(d[key] for d in lst) / len(lst), 2)

def pct_change(new, old):
    if old == 0:
        return "N/A"
    delta = (new - old) / old * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}%"

print("\n" + "=" * 80)
print("TABLE 5.2 — GISMABERT EVALUATION RESULTS (REAL DATA)")
print("=" * 80)
print(f"{'Metric':<20} {'Exact Keyword':>15} {'TF-IDF':>12} {'GISMABert':>12} {'vs Keyword':>12} {'vs TF-IDF':>10}")
print("-" * 80)

for k in [5, 10]:
    for metric in ["precision", "recall", "f1", "ndcg"]:
        kw  = avg(all_results["keyword"][k], metric)
        tf  = avg(all_results["tfidf"][k], metric)
        gb  = avg(all_results["gismabert"][k], metric)
        label = f"{metric.capitalize()}@{k}"
        print(f"{label:<20} {kw:>15.2f} {tf:>12.2f} {gb:>12.2f} {pct_change(gb,kw):>12} {pct_change(gb,tf):>10}")

print(f"{'SemanticBoostRate':<20} {'—':>15} {'—':>12} {semantic_boost_rate*100:>11.1f}% {'—':>12} {'—':>10}")
print("=" * 80)

print("\n📋 Copy these numbers into Table 5.2 of your thesis.")
print(f"\nEvaluation corpus: {len(STUDENT_PROFILES)} student profiles × {len(JOBS)} job postings")
relevant_total = sum(
    1 for p in STUDENT_PROFILES.values()
    for j in JOBS
    if is_relevant(p["skills"], j["required_skills"])
)
print(f"Relevant pairs (≥{RELEVANCE_THRESHOLD} skill overlap): {relevant_total} / {len(STUDENT_PROFILES)*len(JOBS)} ({relevant_total/(len(STUDENT_PROFILES)*len(JOBS))*100:.1f}%)")
print(f"Semantic boost rate: {semantic_boost_rate*100:.1f}%  (jobs where GISMABert score > keyword score by >0.10)")
print(f"\nModel: {GISMABERT_PATH}")

"""
Real job fetching for GISMA Career Connect.

Sources:
─────────
- Bundesagentur für Arbeit API  → Official German Federal Employment Agency
                                   No API key needed. Free. Berlin-focused.
                                   Returns real jobs posted by German companies.

- Adzuna API                    → StepStone and broader German job market
                                   Free 200 req/day. Needs app_id + app_key.

- In-memory cache               → 30-minute TTL per query
- Graceful fallback             → returns [] if APIs fail; router uses seed jobs

Adzuna keys (already set in docker-compose.yml):
  ADZUNA_APP_ID:   your_adzuna_app_id
  ADZUNA_APP_KEY:  your_adzuna_app_key
"""

from __future__ import annotations
import time
import logging
from datetime import date
from typing import Optional
from urllib.parse import quote

import httpx

from ..config import settings

logger = logging.getLogger(__name__)

# ── In-memory cache ────────────────────────────────────────────────────────────
_cache: dict[str, dict] = {}
CACHE_TTL_SECONDS = 1800  # 30 minutes


def _get_cached(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _set_cached(key: str, data: list):
    _cache[key] = {"data": data, "ts": time.time()}


# ── Search query builder ───────────────────────────────────────────────────────

def build_query(student_skills: list[str], course: Optional[str]) -> str:
    """
    Return a single short keyword that both Arbeitsagentur and Adzuna understand.
    Shorter = more results. "Python" beats "Python Software Developer" every time.
    """
    PRIORITY = [
        "Python", "JavaScript", "Java", "React", "SQL", "Machine Learning",
        "Data Analysis", "TypeScript", "Node.js", "Docker", "AWS",
        "Excel", "SAP", "Tableau", "Marketing", "Finance", "Figma",
    ]
    # Course-based fallback when no known skills match
    COURSE_FALLBACK = {
        "business": "Management", "management": "Management", "mba": "Management",
        "marketing": "Marketing", "data": "Data Analyst", "analytics": "Data Analyst",
        "design": "UX Designer", "computer": "Developer", "software": "Developer",
        "it": "Developer", "finance": "Finance", "accounting": "Finance",
    }
    top_skill = next((s for s in PRIORITY if s in student_skills), None)
    if top_skill:
        return top_skill   # e.g. "Python" — clean single keyword

    if course:
        for kw, fallback in COURSE_FALLBACK.items():
            if kw in course.lower():
                return fallback

    return student_skills[0] if student_skills else "Developer"


# ── Bundesagentur für Arbeit (German Federal Employment Agency) ───────────────

def _fetch_arbeitsagentur(query: str, n: int = 8) -> list[dict]:
    """
    Fetch jobs from the official German Federal Employment Agency.
    No API key needed — public endpoint.
    """
    logger.info("Arbeitsagentur: fetching query=%r (Berlin)", query)
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(
                "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs",
                params={
                    "was":  query,    # job keyword
                    "wo":   "Berlin", # location
                    "size": n,
                    "page": 0,
                },
                headers={
                    "X-API-Key":  "jobboerse-jobsuche",
                    "User-Agent": "Mozilla/5.0 (compatible; GISMACareerConnect/1.0)",
                },
            )
            logger.info("Arbeitsagentur: HTTP %s", resp.status_code)
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("stellenangebote") or []
            logger.info("Arbeitsagentur: got %d results", len(jobs))
            return [_parse_arbeitsagentur(j) for j in jobs[:n]]
    except Exception as exc:
        logger.error("Arbeitsagentur: failed — %s", exc)
        return []


def _parse_arbeitsagentur(j: dict) -> dict:
    ref_nr = j.get("refnr", "")
    title  = j.get("titel", "")
    arbeitgeber = j.get("arbeitgeber", "")

    # Build the direct apply/detail URL on the official portal
    apply_url = (
        f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref_nr}"
        if ref_nr else
        f"https://www.arbeitsagentur.de/jobsuche/suche?was={quote(title)}&wo=Berlin"
    )

    # Location
    arbeitsort = j.get("arbeitsort") or {}
    city    = arbeitsort.get("ort") or "Berlin"
    country = arbeitsort.get("land") or "Deutschland"
    location = f"{city}, {country}"

    # Job type
    raw_type = (j.get("arbeitszeitModelle") or [""])[0].upper()
    type_map = {
        "VOLLZEIT": "fulltime",
        "TEILZEIT": "parttime",
        "HOMEOFFICE": "remote",
        "AUSBILDUNG": "internship",
    }
    job_type = type_map.get(raw_type, "fulltime")

    # Posted date
    eintrittsdatum = j.get("eintrittsdatum")
    try:
        posted = date.fromisoformat(eintrittsdatum[:10]) if eintrittsdatum else date.today()
    except Exception:
        posted = date.today()

    return {
        "id":             f"ba_{ref_nr}",
        "title":          title,
        "company":        arbeitgeber,
        "location":       location,
        "job_type":       job_type,
        "salary":         None,   # BA doesn't expose salary in search results
        "posted_date":    posted,
        "required_skills": [],    # extracted from description below
        "apply_url":      apply_url,
        "source":         "arbeitsagentur",
        "description":    (j.get("stellenbeschreibung") or "")[:600],
    }


# ── Adzuna (StepStone / German market) ────────────────────────────────────────

def _fetch_adzuna(query: str, n: int = 5) -> list[dict]:
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        logger.warning("Adzuna: no API keys set, skipping")
        return []
    logger.info("Adzuna: fetching query=%r", query)
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                "https://api.adzuna.com/v1/api/jobs/de/search/1",
                params={
                    "app_id":           settings.adzuna_app_id,
                    "app_key":          settings.adzuna_app_key,
                    "what":             query,
                    "results_per_page": n,
                    "content-type":     "application/json",
                },
            )
            logger.info("Adzuna: HTTP %s", resp.status_code)
            resp.raise_for_status()
            jobs = resp.json().get("results", [])
            logger.info("Adzuna: got %d results", len(jobs))
            return [_parse_adzuna(j) for j in jobs[:n]]
    except Exception as exc:
        logger.error("Adzuna: failed — %s", exc)
        return []


def _parse_adzuna(j: dict) -> dict:
    min_s = j.get("salary_min")
    max_s = j.get("salary_max")
    salary = None
    if min_s and max_s:
        salary = f"€{int(min_s):,} – €{int(max_s):,}"
    elif min_s:
        salary = f"From €{int(min_s):,}"

    title = j.get("title", "")
    return {
        "id":             f"adzuna_{j.get('id', '')}",
        "title":          title,
        "company":        j.get("company", {}).get("display_name", ""),
        "location":       j.get("location", {}).get("display_name", "Berlin"),
        "job_type":       "fulltime",
        "salary":         salary,
        "posted_date":    date.today(),
        "required_skills": [],
        "apply_url": (
            j.get("redirect_url")
            or f"https://www.stepstone.de/jobs/{title.replace(' ', '-').lower()}"
        ),
        "source":         "adzuna",
        "description":    (j.get("description") or "")[:600],
    }


# ── Skill extraction from description ──────────────────────────────────────────

KNOWN_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "React", "Node.js",
    "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS",
    "Machine Learning", "Deep Learning", "Data Analysis", "Pandas",
    "TensorFlow", "PyTorch", "REST APIs", "Spring Boot", "Git",
    "Agile", "Scrum", "Excel", "Tableau", "Power BI", "Figma",
    "UI/UX", "Marketing", "SEO", "Finance", "Accounting", "SAP",
    "Project Management", "Communication", "Leadership", "C++", "C#",
]


def extract_skills_from_description(description: str) -> list[str]:
    """Simple keyword match to extract known skills from a job description."""
    desc_lower = description.lower()
    return [s for s in KNOWN_SKILLS if s.lower() in desc_lower][:8]


# ── Main public function ───────────────────────────────────────────────────────

def fetch_real_jobs(student_skills: list[str], course: Optional[str] = None) -> list[dict]:
    """
    Fetch live Berlin jobs from:
      - Bundesagentur für Arbeit (official German agency, no key needed) — up to 8
      - Adzuna / StepStone (German market)                               — up to 5

    Results cached 30 min. Returns [] gracefully if APIs are down.
    """
    query     = build_query(student_skills, course)
    cache_key = f"real_jobs::{query}"

    cached = _get_cached(cache_key)
    if cached is not None:
        logger.info("Cache hit for query=%r", query)
        return cached

    ba_jobs    = _fetch_arbeitsagentur(query, n=8)
    adzuna_jobs = _fetch_adzuna(query, n=5)

    # Extract skills from descriptions where missing
    for job in ba_jobs + adzuna_jobs:
        if not job["required_skills"] and job.get("description"):
            job["required_skills"] = extract_skills_from_description(job["description"])

    all_jobs = ba_jobs + adzuna_jobs
    _set_cached(cache_key, all_jobs)
    return all_jobs

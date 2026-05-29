from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job, Student
from ..schemas import JobResponse, SkillGapResponse
from ..auth import get_current_student
from ..services import recommendation, skill_gap
from ..services.job_fetcher import fetch_real_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/recommended", response_model=list[JobResponse])
def recommended_jobs(
    filter: str = Query(default="all"),
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Returns jobs ranked by BERT semantic similarity to the student's skill set.

    Sources:
      1. Real jobs from JSearch (LinkedIn) + Adzuna (StepStone) — up to 10 live listings.
      2. Seed jobs from the database — always present as fallback.

    Each job includes match_percent, missing_skills, semantic_boost, apply_url, and source.
    """
    # 1. Seed jobs from DB (always available)
    db_jobs = db.query(Job).all()

    # 2. Real jobs from APIs (returns [] gracefully if keys missing or quota exceeded)
    student_skills = [s.name for s in student.skills]
    real_jobs = fetch_real_jobs(student_skills, course=student.course)

    # 3. Merge — real API jobs first (fresher), then DB seeds
    #    Deduplicate by normalised title+company to avoid showing the same job twice.
    seen: set[str] = set()
    merged = []

    for job in real_jobs:
        key = f"{job['title'].lower()}::{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            merged.append(job)

    for job in db_jobs:
        key = f"{job.title.lower()}::{job.company.lower()}"
        if key not in seen:
            seen.add(key)
            merged.append(job)

    return recommendation.recommend(student, merged, filter)


@router.get("/skill-gap", response_model=SkillGapResponse)
def skill_gap_analysis(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Returns the student's personalised skill gap:
    - top_missing: skills ranked by how many jobs they unlock
    - learning_path: greedy-optimal order to learn them
    """
    jobs = db.query(Job).all()
    return skill_gap.analyse(student, jobs)

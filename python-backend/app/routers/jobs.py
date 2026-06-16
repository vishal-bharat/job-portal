from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job, Student
from ..schemas import JobResponse, SkillGapResponse
from ..auth import get_current_student
from ..services import recommendation, skill_gap
from ..services import job_fetcher as jf

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/recommended", response_model=list[JobResponse])
def recommended_jobs(
    filter: str = Query(default="all"),
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Returns REAL jobs from Arbeitsagentur + Adzuna ranked by BERT similarity.
    No dummy seed data. If APIs return nothing, returns empty list.
    """
    student_skills = [s.name for s in student.skills]
    real_jobs = jf.fetch_real_jobs(student_skills, course=student.course)

    return recommendation.recommend(student, real_jobs, filter)


@router.get("/search", response_model=list[JobResponse])
def search_jobs(
    q: str = Query(default="Developer"),
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Keyword search — fetches live jobs from Arbeitsagentur + Adzuna,
    scored by BERT against the student's profile. No dummy data.
    """
    cache_key = f"search::{q}"
    cached = jf._get_cached(cache_key)

    if cached is None:
        ba_jobs     = jf._fetch_arbeitsagentur(q, n=10)
        adzuna_jobs = jf._fetch_adzuna(q, n=8)
        for job in ba_jobs + adzuna_jobs:
            if not job["required_skills"] and job.get("description"):
                job["required_skills"] = jf.extract_skills_from_description(job["description"])
        all_jobs = ba_jobs + adzuna_jobs
        jf._set_cached(cache_key, all_jobs)
    else:
        all_jobs = cached

    return recommendation.recommend(student, all_jobs, "all")


@router.get("/skill-gap", response_model=SkillGapResponse)
def skill_gap_analysis(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Skill gap analysis uses seed jobs (structured skill data)
    to compute which skills unlock the most opportunities.
    """
    jobs = db.query(Job).all()
    return skill_gap.analyse(student, jobs)

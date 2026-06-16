from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Student, SavedApplication
from ..schemas import SaveApplicationRequest, UpdateApplicationStatusRequest, SavedApplicationResponse
from ..auth import get_current_student

router = APIRouter(prefix="/api/applications", tags=["applications"])

VALID_STATUSES = {"saved", "applied", "interviewing", "offered", "rejected"}


@router.get("", response_model=list[SavedApplicationResponse])
def list_applications(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Return all saved/tracked jobs for the current student, newest first."""
    return (
        db.query(SavedApplication)
        .filter(SavedApplication.student_id == student.id)
        .order_by(SavedApplication.saved_at.desc())
        .all()
    )


@router.post("", response_model=SavedApplicationResponse)
def save_application(
    req: SaveApplicationRequest,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Save a job to the student's applications tracker."""
    # Don't allow duplicates
    existing = (
        db.query(SavedApplication)
        .filter(
            SavedApplication.student_id == student.id,
            SavedApplication.external_job_id == req.external_job_id,
        )
        .first()
    )
    if existing:
        return existing

    app = SavedApplication(
        student_id=student.id,
        external_job_id=req.external_job_id,
        title=req.title,
        company=req.company,
        location=req.location,
        job_type=req.job_type,
        salary=req.salary,
        apply_url=req.apply_url,
        source=req.source,
        status="saved",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.patch("/{app_id}", response_model=SavedApplicationResponse)
def update_status(
    app_id: int,
    req: UpdateApplicationStatusRequest,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Update the status (and optional notes) of a saved application."""
    if req.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {VALID_STATUSES}")

    app = db.query(SavedApplication).filter(
        SavedApplication.id == app_id,
        SavedApplication.student_id == student.id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = req.status
    if req.notes is not None:
        app.notes = req.notes
    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=204)
def delete_application(
    app_id: int,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Remove a saved application."""
    app = db.query(SavedApplication).filter(
        SavedApplication.id == app_id,
        SavedApplication.student_id == student.id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()

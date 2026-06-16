from sqlalchemy import Column, Integer, String, Date, DateTime, Table, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

# Many-to-many: students <-> skills
student_skills = Table(
    "student_skills", Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("skill_id",   Integer, ForeignKey("skills.id"),   primary_key=True),
)

# Many-to-many: jobs <-> skills
job_skills = Table(
    "job_skills", Base.metadata,
    Column("job_id",   Integer, ForeignKey("jobs.id"),   primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)


class Skill(Base):
    __tablename__ = "skills"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Student(Base):
    __tablename__ = "students"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String, unique=True, nullable=False, index=True)
    password   = Column(String, nullable=False)
    name       = Column(String, nullable=False)
    university = Column(String)
    course     = Column(String)
    year       = Column(Integer)

    skills = relationship("Skill", secondary=student_skills, lazy="joined")


class Job(Base):
    __tablename__ = "jobs"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    company     = Column(String, nullable=False)
    location    = Column(String)
    job_type    = Column(String)   # internship | fulltime | parttime | remote
    salary      = Column(String)
    posted_date = Column(Date)

    required_skills = relationship("Skill", secondary=job_skills, lazy="joined")


class SavedApplication(Base):
    """Tracks jobs a student has saved or applied to."""
    __tablename__ = "saved_applications"

    id             = Column(Integer, primary_key=True, index=True)
    student_id     = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    external_job_id = Column(String, nullable=False)   # e.g. "ba_abc123" or "adzuna_xyz"
    title          = Column(String, nullable=False)
    company        = Column(String, nullable=False)
    location       = Column(String)
    job_type       = Column(String)
    salary         = Column(String)
    apply_url      = Column(String)
    source         = Column(String)                    # arbeitsagentur | stepstone | seed
    # Student workflow status
    status         = Column(String, default="saved")   # saved | applied | interviewing | offered | rejected
    notes          = Column(String, default="")
    saved_at       = Column(DateTime, server_default=func.now())

    student = relationship("Student", backref="saved_applications")

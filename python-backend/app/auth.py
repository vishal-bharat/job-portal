from datetime import datetime, timedelta
from typing import Optional

import bcrypt as _bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Student

bearer_scheme = HTTPBearer()


def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(student_id: int) -> str:
    payload = {
        "sub": str(student_id),
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiry_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Student:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        student_id: Optional[str] = payload.get("sub")
        if student_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    student = db.query(Student).filter(Student.id == int(student_id)).first()
    if student is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Student not found")
    return student

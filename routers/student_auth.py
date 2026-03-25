from fastapi import APIRouter, Request, Depends, Form, HTTPException, responses
from sqlmodel import Session, select
from datetime import timedelta
from database import get_session
from models import Student
from security import verify_password, create_access_token
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/student-auth", tags=["student_auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def student_login_page(request: Request):
    return templates.TemplateResponse("student/login.html", {"request": request})

@router.post("/login")
def student_login(
    request: Request,
    umis_id: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    student = session.exec(select(Student).where(Student.umis_id == umis_id)).first()
    if not student or not verify_password(password, student.password_hash):
        return templates.TemplateResponse("student/login.html", {
            "request": request,
            "error": "Invalid UMIS ID or password"
        })
    token = create_access_token({"sub": str(student.id), "role": "student"}, timedelta(hours=12))
    response = responses.RedirectResponse("/student/dashboard", status_code=302)
    response.set_cookie(key="student_access_token", value=token, httponly=True)
    return response

@router.get("/logout")
def student_logout():
    response = responses.RedirectResponse("/student-auth/login", status_code=302)
    response.delete_cookie("student_access_token")
    return response

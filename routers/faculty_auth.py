from fastapi import APIRouter, Request, Depends, Form, HTTPException, responses
from sqlmodel import Session, select
from datetime import timedelta
from database import get_session
from models import Faculty
from security import verify_password, create_access_token
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/faculty-auth", tags=["faculty_auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def faculty_login_page(request: Request):
    return templates.TemplateResponse("faculty/login.html", {"request": request})

@router.post("/login")
def faculty_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    faculty = session.exec(select(Faculty).where(Faculty.username == username)).first()
    if not faculty or not verify_password(password, faculty.password_hash):
        return templates.TemplateResponse("faculty/login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
    
    token = create_access_token(
        {"sub": str(faculty.id), "username": faculty.username, "role": "faculty"}, 
        timedelta(hours=12)
    )
    
    response = responses.RedirectResponse("/faculty/dashboard", status_code=302)
    response.set_cookie(key="faculty_access_token", value=token, httponly=True)
    return response

@router.get("/logout")
def faculty_logout():
    response = responses.RedirectResponse("/faculty-auth/login", status_code=302)
    response.delete_cookie("faculty_access_token")
    return response

# Dependency to get current faculty
from security import decode_access_token

def get_current_faculty(request: Request, db: Session = Depends(get_session)):
    token = request.cookies.get("faculty_access_token")
    if not token:
        raise HTTPException(status_code=302, headers={"Location": "/faculty-auth/login"})
    
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "faculty":
        raise HTTPException(status_code=302, headers={"Location": "/faculty-auth/login"})
    
    faculty_id = payload.get("sub")
    faculty = db.get(Faculty, int(faculty_id))
    if not faculty:
        raise HTTPException(status_code=302, headers={"Location": "/faculty-auth/login"})
    return faculty

from fastapi import APIRouter, Request, Depends, Form, HTTPException, responses
from sqlmodel import Session, select
from datetime import timedelta
from database import get_session
from models import User
from security import verify_password, create_access_token
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin-auth", tags=["admin_auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash) or user.role != "admin":
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
    token = create_access_token({"sub": username, "role": "admin"}, timedelta(hours=12))
    response = responses.RedirectResponse("/admin", status_code=302)
    response.set_cookie(key="admin_access_token", value=token, httponly=True)
    return response

@router.get("/logout")
def logout():
    response = responses.RedirectResponse("/admin-auth/login", status_code=302)
    response.delete_cookie("admin_access_token")
    return response

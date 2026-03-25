from fastapi import APIRouter, Request, Depends, Form, responses
from sqlmodel import Session, select
from database import get_session
from models import Faculty, Notice
from fastapi.templating import Jinja2Templates
from routers.faculty_auth import get_current_faculty

router = APIRouter(prefix="/faculty/notices", tags=["faculty_notices"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_notices(
    request: Request, 
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    notices = db.exec(select(Notice).where(Notice.posted_by == str(faculty.id))).all()
    return templates.TemplateResponse("faculty/notices.html", {
        "request": request,
        "faculty": faculty,
        "notices": notices,
        "active_page": "notices"
    })

@router.post("/post")
def post_notice(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    type: str = Form("General"),
    db: Session = Depends(get_session),
    faculty: Faculty = Depends(get_current_faculty)
):
    notice = Notice(
        title=title,
        content=content,
        type=type,
        posted_by=str(faculty.id)
    )
    db.add(notice)
    db.commit()
    return responses.RedirectResponse("/faculty/notices", status_code=302)

@router.get("/delete/{notice_id}")
def delete_notice(
    notice_id: int, 
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    notice = db.get(Notice, notice_id)
    if notice and notice.posted_by == str(faculty.id):
        db.delete(notice)
        db.commit()
    return responses.RedirectResponse("/faculty/notices", status_code=302)

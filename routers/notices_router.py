from fastapi import APIRouter, Request, Depends, Form, responses, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Notice
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin

router = APIRouter(prefix="/admin/notices", tags=["admin_notices"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_notices(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    notices = db.exec(select(Notice).order_by(Notice.date_posted.desc())).all()
    return templates.TemplateResponse("admin/notices_list.html", {"request": request, "notices": notices})

@router.post("/add")
def add_notice(
    title: str = Form(...), content: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    notice = Notice(title=title, content=content)
    db.add(notice)
    db.commit()
    return responses.RedirectResponse("/admin/notices", status_code=302)

@router.get("/edit/{notice_id}")
def edit_notice_page(notice_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    notice = db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return templates.TemplateResponse("admin/notices_edit.html", {"request": request, "notice": notice})

@router.post("/edit/{notice_id}")
def edit_notice(
    notice_id: int, request: Request,
    title: str = Form(...), content: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    notice = db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    notice.title = title
    notice.content = content
    
    db.add(notice)
    db.commit()
    return responses.RedirectResponse("/admin/notices", status_code=302)

@router.get("/delete/{notice_id}")
def delete_notice(notice_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    notice = db.get(Notice, notice_id)
    if notice:
        db.delete(notice)
        db.commit()
    return responses.RedirectResponse("/admin/notices", status_code=302)

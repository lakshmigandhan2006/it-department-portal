from fastapi import APIRouter, Request, Depends, Form, responses, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Exam
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin

router = APIRouter(prefix="/admin/exams", tags=["admin_exams"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_exams(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    exams = db.exec(select(Exam)).all()
    return templates.TemplateResponse("admin/exams_list.html", {"request": request, "exams": exams})

@router.post("/add")
def add_exam(
    title: str = Form(...), date: str = Form(...),
    course_code: str = Form(...), status: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    exam = Exam(title=title, date=date, course_code=course_code, status=status)
    db.add(exam)
    db.commit()
    return responses.RedirectResponse("/admin/exams", status_code=302)

@router.get("/edit/{exam_id}")
def edit_exam_page(exam_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return templates.TemplateResponse("admin/exams_edit.html", {"request": request, "exam": exam})

@router.post("/edit/{exam_id}")
def edit_exam(
    exam_id: int, request: Request,
    title: str = Form(...), date: str = Form(...),
    course_code: str = Form(...), status: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam.title = title
    exam.date = date
    exam.course_code = course_code
    exam.status = status
    
    db.add(exam)
    db.commit()
    return responses.RedirectResponse("/admin/exams", status_code=302)

@router.get("/delete/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    exam = db.get(Exam, exam_id)
    if exam:
        db.delete(exam)
        db.commit()
    return responses.RedirectResponse("/admin/exams", status_code=302)

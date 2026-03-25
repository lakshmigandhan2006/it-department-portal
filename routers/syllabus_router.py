from fastapi import APIRouter, Request, Depends, Form, responses, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Syllabus
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin

router = APIRouter(prefix="/admin/syllabus", tags=["admin_syllabus"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_syllabus(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    syllabi = db.exec(select(Syllabus)).all()
    return templates.TemplateResponse("admin/syllabus_list.html", {"request": request, "syllabi": syllabi})

@router.post("/add")
def add_syllabus(
    course_name: str = Form(...), course_code: str = Form(...),
    semester: int = Form(...), description: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    syllabus = Syllabus(course_name=course_name, course_code=course_code, semester=semester, description=description)
    db.add(syllabus)
    db.commit()
    return responses.RedirectResponse("/admin/syllabus", status_code=302)

@router.get("/edit/{syllabus_id}")
def edit_syllabus_page(syllabus_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    syllabus = db.get(Syllabus, syllabus_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return templates.TemplateResponse("admin/syllabus_edit.html", {"request": request, "syllabus": syllabus})

@router.post("/edit/{syllabus_id}")
def edit_syllabus(
    syllabus_id: int, request: Request,
    course_name: str = Form(...), course_code: str = Form(...),
    semester: int = Form(...), description: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    syllabus = db.get(Syllabus, syllabus_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    syllabus.course_name = course_name
    syllabus.course_code = course_code
    syllabus.semester = semester
    syllabus.description = description
    
    db.add(syllabus)
    db.commit()
    return responses.RedirectResponse("/admin/syllabus", status_code=302)

@router.get("/delete/{syllabus_id}")
def delete_syllabus(syllabus_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    syllabus = db.get(Syllabus, syllabus_id)
    if syllabus:
        db.delete(syllabus)
        db.commit()
    return responses.RedirectResponse("/admin/syllabus", status_code=302)

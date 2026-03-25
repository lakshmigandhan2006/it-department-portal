from fastapi import APIRouter, Request, Depends, Form, responses, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import TimeTable
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin

router = APIRouter(prefix="/admin/timetable", tags=["admin_timetable"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_timetable(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    entries = db.exec(select(TimeTable)).all()
    return templates.TemplateResponse("admin/timetable_list.html", {"request": request, "entries": entries})

@router.post("/add")
def add_timetable(
    day_of_week: str = Form(...), time_slot: str = Form(...),
    course_code: str = Form(...), faculty_name: str = Form(...),
    room_no: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    entry = TimeTable(
        day_of_week=day_of_week, time_slot=time_slot,
        course_code=course_code, faculty_name=faculty_name, room_no=room_no
    )
    db.add(entry)
    db.commit()
    return responses.RedirectResponse("/admin/timetable", status_code=302)

@router.get("/edit/{entry_id}")
def edit_timetable_page(entry_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    entry = db.get(TimeTable, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return templates.TemplateResponse("admin/timetable_edit.html", {"request": request, "entry": entry})

@router.post("/edit/{entry_id}")
def edit_timetable(
    entry_id: int, request: Request,
    day_of_week: str = Form(...), time_slot: str = Form(...),
    course_code: str = Form(...), faculty_name: str = Form(...),
    room_no: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    entry = db.get(TimeTable, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    entry.day_of_week = day_of_week
    entry.time_slot = time_slot
    entry.course_code = course_code
    entry.faculty_name = faculty_name
    entry.room_no = room_no
    
    db.add(entry)
    db.commit()
    return responses.RedirectResponse("/admin/timetable", status_code=302)

@router.get("/delete/{entry_id}")
def delete_timetable(entry_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    entry = db.get(TimeTable, entry_id)
    if entry:
        db.delete(entry)
        db.commit()
    return responses.RedirectResponse("/admin/timetable", status_code=302)

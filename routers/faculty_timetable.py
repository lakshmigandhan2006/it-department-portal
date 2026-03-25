from fastapi import APIRouter, Request, Depends
from sqlmodel import Session, select
from database import get_session
from models import Faculty, TimeTable
from fastapi.templating import Jinja2Templates
from routers.faculty_auth import get_current_faculty

router = APIRouter(prefix="/faculty/timetable", tags=["faculty_timetable"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_timetable(
    request: Request, 
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    # Try to match by faculty name (simple string match for now)
    entries = db.exec(select(TimeTable).where(TimeTable.faculty_name == faculty.name)).all()
    # If no specific entries, show all (or could show just relevant department ones)
    if not entries:
        entries = db.exec(select(TimeTable)).all()
        
    return templates.TemplateResponse("faculty/timetable.html", {
        "request": request,
        "faculty": faculty,
        "entries": entries,
        "active_page": "timetable"
    })

from fastapi import APIRouter, Request, Depends, Form, HTTPException, responses, UploadFile, File
from sqlmodel import Session, select
from database import get_session
from models import Student
from security import get_password_hash
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin
import os
import shutil
import uuid

router = APIRouter(prefix="/admin/students", tags=["admin_students"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_students(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    students = db.exec(select(Student)).all()
    return templates.TemplateResponse("admin/students_list.html", {"request": request, "students": students})

@router.get("/add")
def add_student_page(request: Request, admin=Depends(check_admin)):
    return templates.TemplateResponse("admin/students_add.html", {"request": request})

@router.post("/add")
async def add_student(
    request: Request,
    name: str = Form(...), roll_no: str = Form(...), year: str = Form(...),
    umis_id: str = Form(...), dob: str = Form(...), gender: str = Form(...),
    blood_group: str = Form(...), hostel_status: str = Form(...), community: str = Form(...),
    scholarship_status: str = Form(...), aadhaar: str = Form(...), student_phone: str = Form(...),
    parent_phone: str = Form(...), address: str = Form(...), password: str = Form(...),
    attendance_percentage: float = Form(0.0), last_sem_percentage: float = Form(0.0),
    photo: UploadFile = File(None),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    student = Student(
        name=name, roll_no=roll_no, year=year, umis_id=umis_id, dob=dob, gender=gender,
        blood_group=blood_group, hostel_status=hostel_status, community=community,
        scholarship_status=scholarship_status, password_hash=get_password_hash(password),
        attendance_percentage=attendance_percentage, last_sem_percentage=last_sem_percentage
    )
    student.aadhaar = aadhaar
    student.student_phone = student_phone
    student.parent_phone = parent_phone
    student.address = address
    
    if photo and photo.filename:
        ext = photo.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = f"static/uploads/students/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        student.photo = filepath
        
    db.add(student)
    db.commit()
    return responses.RedirectResponse("/admin/students", status_code=302)

@router.get("/edit/{student_id}")
def edit_student_page(student_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse("admin/students_edit.html", {"request": request, "student": student})

@router.post("/edit/{student_id}")
async def edit_student(
    student_id: int, request: Request,
    name: str = Form(...), roll_no: str = Form(...), year: str = Form(...),
    umis_id: str = Form(...), dob: str = Form(...), gender: str = Form(...),
    blood_group: str = Form(...), hostel_status: str = Form(...), community: str = Form(...),
    scholarship_status: str = Form(...), aadhaar: str = Form(""), student_phone: str = Form(...),
    parent_phone: str = Form(...), address: str = Form(...), password: str = Form(""),
    attendance_percentage: float = Form(0.0), last_sem_percentage: float = Form(0.0),
    photo: UploadFile = File(None),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.name = name
    student.roll_no = roll_no
    student.year = year
    student.umis_id = umis_id
    student.dob = dob
    student.gender = gender
    student.blood_group = blood_group
    student.hostel_status = hostel_status
    student.community = community
    student.scholarship_status = scholarship_status
    student.attendance_percentage = attendance_percentage
    student.last_sem_percentage = last_sem_percentage
    if aadhaar:
        student.aadhaar = aadhaar
    student.student_phone = student_phone
    student.parent_phone = parent_phone
    student.address = address
    if password:
        student.password_hash = get_password_hash(password)

    if photo and photo.filename:
        ext = photo.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = f"static/uploads/students/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        try:
            if student.photo:
                os.remove(student.photo)
        except Exception:
            pass
        student.photo = filepath

    db.add(student)
    db.commit()
    return responses.RedirectResponse("/admin/students", status_code=302)

@router.get("/delete/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    student = db.get(Student, student_id)
    if student:
        db.delete(student)
        db.commit()
    return responses.RedirectResponse("/admin/students", status_code=302)

@router.get("/id_card/{student_id}")
def admin_generate_student_id_card(student_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse("student/id_card.html", {"request": request, "student": student})

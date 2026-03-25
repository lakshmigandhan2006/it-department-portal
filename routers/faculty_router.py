from fastapi import APIRouter, Request, Depends, Form, responses, HTTPException, UploadFile, File
from typing import Optional
from sqlmodel import Session, select
from database import get_session
from models import Faculty
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin
from security import get_password_hash
import os
import shutil
import uuid

router = APIRouter(prefix="/admin/faculty", tags=["admin_faculty"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_faculty(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    faculties = db.exec(select(Faculty)).all()
    return templates.TemplateResponse("admin/faculty_list.html", {"request": request, "faculties": faculties})

@router.post("/add")
def add_faculty(
    name: str = Form(...), designation: str = Form(...),
    email: str = Form(...), phone: str = Form(...),
    subject: str = Form("General"), department: str = Form("IT"),
    username: str = Form(...), password: str = Form(...),
    photo: UploadFile = File(None),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    photo_path = None
    if photo and photo.filename:
        # Save photo
        upload_dir = "static/uploads/faculty"
        os.makedirs(upload_dir, exist_ok=True)
        ext = photo.filename.split(".")[-1]
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(upload_dir, new_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_path = file_path

    faculty = Faculty(
        name=name, designation=designation, email=email, phone=phone,
        subject=subject, department=department,
        username=username, password_hash=get_password_hash(password),
        photo=photo_path
    )
    db.add(faculty)
    db.commit()
    return responses.RedirectResponse("/admin/faculty", status_code=302)

@router.get("/edit/{faculty_id}")
def edit_faculty_page(faculty_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return templates.TemplateResponse("admin/faculty_edit.html", {"request": request, "faculty": faculty})

@router.post("/edit/{faculty_id}")
def edit_faculty(
    faculty_id: int, request: Request,
    name: str = Form(...), designation: str = Form(...),
    email: str = Form(...), phone: str = Form(...),
    subject: str = Form(...), department: str = Form(...),
    username: str = Form(...), password: Optional[str] = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    faculty.name = name
    faculty.designation = designation
    faculty.email = email
    faculty.phone = phone
    faculty.subject = subject
    faculty.department = department
    faculty.username = username
    
    if password:
        faculty.password_hash = get_password_hash(password)
    
    if photo and photo.filename:
        # Save new photo
        upload_dir = "static/uploads/faculty"
        os.makedirs(upload_dir, exist_ok=True)
        ext = photo.filename.split(".")[-1]
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        new_file_path = os.path.join(upload_dir, new_filename)
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
            
        # Optional: delete old photo if exists
        try:
            if faculty.photo and os.path.exists(faculty.photo):
                os.remove(faculty.photo)
        except Exception:
            pass

        faculty.photo = new_file_path
    
    db.add(faculty)
    db.commit()
    return responses.RedirectResponse("/admin/faculty", status_code=302)

@router.get("/delete/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    faculty = db.get(Faculty, faculty_id)
    if faculty:
        db.delete(faculty)
        db.commit()
    return responses.RedirectResponse("/admin/faculty", status_code=302)

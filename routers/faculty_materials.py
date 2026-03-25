from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, responses
from sqlmodel import Session, select
from database import get_session
from models import Faculty, StudyMaterial
from fastapi.templating import Jinja2Templates
from routers.faculty_auth import get_current_faculty
import os
import shutil
import uuid

router = APIRouter(prefix="/faculty/materials", tags=["faculty_materials"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_materials(
    request: Request, 
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    materials = db.exec(select(StudyMaterial).where(StudyMaterial.uploaded_by == faculty.id)).all()
    return templates.TemplateResponse("faculty/materials.html", {
        "request": request,
        "faculty": faculty,
        "materials": materials,
        "active_page": "materials"
    })

@router.post("/upload")
def upload_material(
    request: Request,
    title: str = Form(...),
    course_code: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    faculty: Faculty = Depends(get_current_faculty)
):
    upload_dir = "static/uploads/materials"
    os.makedirs(upload_dir, exist_ok=True)
    
    ext = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(upload_dir, new_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    material = StudyMaterial(
        title=title,
        course_code=course_code,
        description=description,
        file_path=file_path,
        uploaded_by=faculty.id
    )
    db.add(material)
    db.commit()
    return responses.RedirectResponse("/faculty/materials", status_code=302)

@router.get("/delete/{material_id}")
def delete_material(
    material_id: int, 
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    material = db.get(StudyMaterial, material_id)
    if material and material.uploaded_by == faculty.id:
        if os.path.exists(material.file_path):
            os.remove(material.file_path)
        db.delete(material)
        db.commit()
    return responses.RedirectResponse("/faculty/materials", status_code=302)

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, responses, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import StudyMaterial
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin
import os
import shutil
import uuid

router = APIRouter(prefix="/admin/materials", tags=["admin_materials"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_materials(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    materials = db.exec(select(StudyMaterial)).all()
    return templates.TemplateResponse("admin/materials_list.html", {"request": request, "materials": materials})

@router.post("/add")
async def add_material(
    title: str = Form(...), course_code: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = f"static/uploads/materials/{filename}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    material = StudyMaterial(title=title, course_code=course_code, file_path=filepath)
    db.add(material)
    db.commit()
    return responses.RedirectResponse("/admin/materials", status_code=302)

@router.get("/edit/{material_id}")
def edit_material_page(material_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    material = db.get(StudyMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return templates.TemplateResponse("admin/materials_edit.html", {"request": request, "material": material})

@router.post("/edit/{material_id}")
async def edit_material(
    material_id: int, request: Request,
    title: str = Form(...), course_code: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    material = db.get(StudyMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material.title = title
    material.course_code = course_code
    
    if file and file.filename:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = f"static/uploads/materials/{filename}"
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        try:
            os.remove(material.file_path)
        except:
            pass
        material.file_path = filepath
        
    db.add(material)
    db.commit()
    return responses.RedirectResponse("/admin/materials", status_code=302)

@router.get("/delete/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    material = db.get(StudyMaterial, material_id)
    if material:
        try:
            os.remove(material.file_path)
        except Exception:
            pass
        db.delete(material)
        db.commit()
    return responses.RedirectResponse("/admin/materials", status_code=302)

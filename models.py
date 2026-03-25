from typing import Optional, List
from sqlmodel import Field, SQLModel
from datetime import datetime
from security import encrypt_data, decrypt_data, get_password_hash

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="admin")  # 'admin'

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    roll_no: str = Field(unique=True, index=True)
    year: str
    umis_id: str = Field(unique=True, index=True)
    dob: str
    gender: str
    blood_group: str
    hostel_status: str
    community: str
    scholarship_status: str
    attendance_percentage: float = 0.0
    last_sem_percentage: float = 0.0
    photo: Optional[str] = None
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Encrypted fields
    encrypted_aadhaar: Optional[str] = None
    encrypted_student_phone: Optional[str] = None
    encrypted_parent_phone: Optional[str] = None
    encrypted_address: Optional[str] = None
    
    @property
    def aadhaar(self) -> str:
        return decrypt_data(self.encrypted_aadhaar)
    @aadhaar.setter
    def aadhaar(self, value: str):
        self.encrypted_aadhaar = encrypt_data(value)

    @property
    def student_phone(self) -> str:
        return decrypt_data(self.encrypted_student_phone)
    @student_phone.setter
    def student_phone(self, value: str):
        self.encrypted_student_phone = encrypt_data(value)
        
    @property
    def parent_phone(self) -> str:
        return decrypt_data(self.encrypted_parent_phone)
    @parent_phone.setter
    def parent_phone(self, value: str):
        self.encrypted_parent_phone = encrypt_data(value)
        
    @property
    def address(self) -> str:
        return decrypt_data(self.encrypted_address)
    @address.setter
    def address(self, value: str):
        self.encrypted_address = encrypt_data(value)

class Faculty(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    designation: str
    email: str = Field(unique=True, index=True)
    phone: str
    subject: str = Field(default="General")
    department: str = Field(default="IT")
    username: str = Field(unique=True, index=True, default=None)
    password_hash: str = Field(default="")
    role: str = Field(default="faculty")
    photo: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    faculty_id: int = Field(foreign_key="faculty.id")
    date: str
    status: str  # 'Present', 'Absent'
    subject: str
    year: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Syllabus(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_name: str
    course_code: str
    semester: int
    description: str

class Exam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    date: str
    course_code: str
    status: str

class StudyMaterial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    course_code: str
    description: Optional[str] = None
    file_path: str
    uploaded_by: Optional[int] = Field(default=None, foreign_key="faculty.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class Notice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    posted_by: str = Field(default="Admin") # 'Admin' or Faculty ID/Name
    type: str = Field(default="General") # 'General', 'Academic', 'Exam'
    date_posted: datetime = Field(default_factory=datetime.utcnow)

class Achievement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    student_name: str
    description: str
    date: str

class TimeTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day_of_week: str
    time_slot: str
    course_code: str
    faculty_name: str
    room_no: str

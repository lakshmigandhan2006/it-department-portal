import os
import base64
from passlib.context import CryptContext
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from jose import jwt, JWTError
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate or use a static key for AES (32 bytes for AES-256)
SECRET_KEY = os.environ.get("AES_SECRET_KEY", "itdept_secret_key_12345678901234").encode("utf-8")
if len(SECRET_KEY) < 32:
    SECRET_KEY = SECRET_KEY.ljust(32, b'0')
elif len(SECRET_KEY) > 32:
    SECRET_KEY = SECRET_KEY[:32]

JWT_SECRET = "jwt_secret_itdept_ultra_version"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def encrypt_data(raw: str) -> str:
    if not raw:
        return raw
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(raw.encode("utf-8"), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode("utf-8")
    ct = base64.b64encode(ct_bytes).decode("utf-8")
    return f"{iv}:{ct}"

def decrypt_data(enc: str) -> str:
    if not enc or ":" not in enc:
        return enc
    try:
        iv_b64, ct_b64 = enc.split(":", 1)
        iv = base64.b64decode(iv_b64)
        ct = base64.b64decode(ct_b64)
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size).decode("utf-8")
        return pt
    except Exception:
        return enc

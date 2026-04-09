from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from database import db
from utils.auth import hash_password, verify_password, create_token, decode_token
from bson import ObjectId

router = APIRouter()
security = HTTPBearer()

class SignupBody(BaseModel):
    name: str
    email: EmailStr
    password: str
    skills: list[str] = []

class LoginBody(BaseModel):
    email: EmailStr
    password: str

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = decode_token(credentials.credentials)
        user = await db.users.find_one({"_id": ObjectId(payload["id"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["id"] = str(user["_id"])
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/signup")
async def signup(body: SignupBody):
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "name": body.name,
        "email": body.email,
        "password": hash_password(body.password),
        "skills": body.skills,
        "role": "admin",
        "score": 0,
        "bio": "",
        "github": "",
        "linkedin": "",
        "avatar": ""
    }
    result = await db.users.insert_one(user)
    token = create_token({"id": str(result.inserted_id)})
    return {
        "success": True,
        "data": {"id": str(result.inserted_id), "name": body.name, "email": body.email, "role": "admin"},
        "token": token
    }

@router.post("/login")
async def login(body: LoginBody):
    user = await db.users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token({"id": str(user["_id"])})
    return {
        "success": True,
        "data": {"id": str(user["_id"]), "name": user["name"], "role": user["role"]},
        "token": token
    }

@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "skills": current_user.get("skills", []),
            "score": current_user.get("score", 0),
            "role": current_user.get("role", "admin")
        }
    }
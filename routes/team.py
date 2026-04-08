from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import db
from routes.auth import get_current_user
from bson import ObjectId

router = APIRouter()

class MemberBody(BaseModel):
    name: str
    role: str
    domain: str = "Web"
    skills: list[str] = []
    photo: str = ""
    batch: str = ""
    github: str = ""
    linkedin: str = ""
    isAlumni: bool = False

def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@router.get("")
async def get_team(domain: str = None, isAlumni: bool = False):
    query = {"isAlumni": isAlumni}
    if domain:
        query["domain"] = domain
    members = await db.team.find(query).to_list(200)
    return {"success": True, "data": [serialize(m) for m in members]}

@router.post("")
async def add_member(body: MemberBody, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    result = await db.team.insert_one(body.dict())
    return {"success": True, "data": {"id": str(result.inserted_id)}}

@router.patch("/{member_id}")
async def update_member(member_id: str, body: dict, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    await db.team.update_one({"_id": ObjectId(member_id)}, {"$set": body})
    return {"success": True, "message": "Updated"}
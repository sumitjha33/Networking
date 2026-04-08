from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import db
from routes.auth import get_current_user
from bson import ObjectId

router = APIRouter()

class ProjectBody(BaseModel):
    title: str
    description: str
    techStack: list[str] = []
    github: str = ""
    live: str = ""
    thumbnail: str = ""
    featured: bool = False

def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@router.get("")
async def get_projects(techStack: str = None, featured: bool = None):
    query = {}
    if techStack:
        query["techStack"] = {"$in": [techStack]}
    if featured is not None:
        query["featured"] = featured
    projects = await db.projects.find(query).to_list(100)
    return {"success": True, "data": [serialize(p) for p in projects]}

@router.get("/{project_id}")
async def get_project(project_id: str):
    p = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True, "data": serialize(p)}

@router.post("")
async def create_project(body: ProjectBody, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    result = await db.projects.insert_one(body.dict())
    return {"success": True, "data": {"id": str(result.inserted_id)}}

@router.patch("/{project_id}")
async def update_project(project_id: str, body: dict, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    await db.projects.update_one({"_id": ObjectId(project_id)}, {"$set": body})
    return {"success": True, "message": "Updated"}
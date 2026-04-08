from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import db
from routes.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()

class EventBody(BaseModel):
    title: str
    description: str = ""
    date: str
    venue: str = ""
    category: str = "Workshop"
    bannerImage: str = ""

def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@router.get("")
async def get_events(type: str = "all"):
    now = datetime.utcnow().isoformat()
    query = {}
    if type == "upcoming":
        query = {"date": {"$gte": now}}
    elif type == "past":
        query = {"date": {"$lt": now}}
    
    events = await db.events.find(query).sort("date", 1).to_list(100)
    return {"success": True, "data": [serialize(e) for e in events]}

@router.get("/{event_id}")
async def get_event(event_id: str):
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True, "data": serialize(event)}

@router.post("")
async def create_event(body: EventBody, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    event = body.dict()
    event["registeredCount"] = 0
    event["registeredUsers"] = []
    result = await db.events.insert_one(event)
    return {"success": True, "data": {"id": str(result.inserted_id)}}

@router.patch("/{event_id}")
async def update_event(event_id: str, body: dict, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    await db.events.update_one({"_id": ObjectId(event_id)}, {"$set": body})
    return {"success": True, "message": "Updated"}

@router.post("/{event_id}/register")
async def register_event(event_id: str, current_user=Depends(get_current_user)):
    uid = current_user["id"]
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if uid in event.get("registeredUsers", []):
        raise HTTPException(status_code=400, detail="Already registered")
    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$push": {"registeredUsers": uid}, "$inc": {"registeredCount": 1}}
    )
    return {"success": True, "message": "Registered successfully"}
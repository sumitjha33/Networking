from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import db
from routes.auth import get_current_user
from bson import ObjectId
from datetime import datetime
import re

router = APIRouter()

class ChallengeBody(BaseModel):
    title: str
    description: str
    difficulty: str = "easy"
    deadline: str
    category: str = "Full-Stack"

class SubmissionBody(BaseModel):
    githubLink: str
    liveLink: str = ""

def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

def is_valid_url(url: str):
    return re.match(r'https?://', url) is not None

@router.get("")
async def get_challenges(difficulty: str = None, category: str = None):
    query = {}
    if difficulty:
        query["difficulty"] = difficulty
    if category:
        query["category"] = category
    challenges = await db.challenges.find(query).to_list(100)
    return {"success": True, "data": [serialize(c) for c in challenges]}

@router.get("/{challenge_id}")
async def get_challenge(challenge_id: str):
    c = await db.challenges.find_one({"_id": ObjectId(challenge_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True, "data": serialize(c)}

@router.post("")
async def create_challenge(body: ChallengeBody, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    result = await db.challenges.insert_one(body.dict())
    return {"success": True, "data": {"id": str(result.inserted_id)}}

@router.patch("/{challenge_id}")
async def update_challenge(challenge_id: str, body: dict, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    await db.challenges.update_one({"_id": ObjectId(challenge_id)}, {"$set": body})
    return {"success": True, "message": "Updated"}

@router.post("/{challenge_id}/submissions")
async def submit(challenge_id: str, body: SubmissionBody, current_user=Depends(get_current_user)):
    uid = current_user["id"]
    if not is_valid_url(body.githubLink):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    existing = await db.submissions.find_one({"challengeId": challenge_id, "userId": uid})
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted")
    
    submission = {
        "challengeId": challenge_id,
        "userId": uid,
        "userName": current_user["name"],
        "githubLink": body.githubLink,
        "liveLink": body.liveLink,
        "status": "pending",
        "score": 0,
        "submittedAt": datetime.utcnow().isoformat()
    }
    await db.submissions.insert_one(submission)
    return {"success": True, "message": "Submitted successfully"}

@router.get("/{challenge_id}/submissions")
async def get_submissions(challenge_id: str, current_user=Depends(get_current_user)):
    subs = await db.submissions.find({"challengeId": challenge_id}).to_list(200)
    for s in subs:
        s["id"] = str(s["_id"])
        del s["_id"]
    return {"success": True, "data": subs}
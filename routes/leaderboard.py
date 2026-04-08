from fastapi import APIRouter
from database import db
from bson import ObjectId

router = APIRouter()

@router.get("")
async def global_leaderboard():
    users = await db.users.find({}, {"name": 1, "score": 1, "role": 1}).sort("score", -1).to_list(50)
    data = [{"userId": str(u["_id"]), "name": u["name"], "score": u.get("score", 0)} for u in users]
    return {"success": True, "data": data}

@router.get("/{challenge_id}")
async def challenge_leaderboard(challenge_id: str):
    subs = await db.submissions.find(
        {"challengeId": challenge_id},
        {"userName": 1, "score": 1, "submittedAt": 1}
    ).sort("score", -1).to_list(100)
    for s in subs:
        s["id"] = str(s["_id"])
        del s["_id"]
    return {"success": True, "data": subs}
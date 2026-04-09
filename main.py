from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, events, challenges, leaderboard, projects, team
from database import db   
from fastapi import Response


app = FastAPI(title="Club Hub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/v1/auth",        tags=["Auth"])
app.include_router(events.router,      prefix="/api/v1/events",      tags=["Events"])
app.include_router(challenges.router,  prefix="/api/v1/challenges",  tags=["Challenges"])
app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["Leaderboard"])
app.include_router(projects.router,    prefix="/api/v1/projects",    tags=["Projects"])
app.include_router(team.router,        prefix="/api/v1/team",        tags=["Team"])



@app.get("/debug-users")
async def debug_users():
    users = await db.users.find().to_list(10)
    for u in users:
        u["id"] = str(u["_id"])
        del u["_id"]
    return users

@app.get("/")
def root():
    return {"message": "Club Hub API is running"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return Response(status_code=200)
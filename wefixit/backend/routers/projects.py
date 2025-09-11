#projects.py
from fastapi import APIRouter, Depends
from backend.database import get_db
from bson import ObjectId

router = APIRouter(tags=["projects"])

@router.get("/")
async def list_projects(db=Depends(get_db)):
    projects = []
    cursor = db.projects.find({})
    async for doc in cursor:
        projects.append({
            "_id": str(doc["_id"]),
            "name": doc["name"],
            "description": doc.get("description")
        })
    return projects


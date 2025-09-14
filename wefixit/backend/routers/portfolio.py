from fastapi import (
    APIRouter, HTTPException, Query,
    Depends, Form, File, UploadFile, Request
)
from bson import ObjectId
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import os, uuid

from backend.database import get_db
from backend.schemas import PortfolioOut
from backend.deps import get_current_admin

router = APIRouter(tags=["portfolio"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ----------------------------
# Helpers
# ----------------------------
def _doc_to_portfolio_out(doc: Dict[str, Any]) -> PortfolioOut:
    return PortfolioOut(
        _id=str(doc["_id"]),
        title=doc["title"],
        description=doc.get("description"),
        image=doc.get("image_url"),
        link=doc.get("link"),
        tags=doc.get("tags", []),
        is_featured=bool(doc.get("is_featured", False)),
        is_active=bool(doc.get("is_active", True)),
        created_at=doc.get("created_at", datetime.now(timezone.utc)),
    )


def _save_image(image: UploadFile, base_url: str) -> str:
    """Save uploaded file and return its public URL"""
    ext = os.path.splitext(image.filename)[1]  # keep extension
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    return f"{base_url.rstrip('/')}/uploads/{unique_name}"


# ----------------------------
# Routes
# ----------------------------
@router.get("/", response_model=dict)
async def list_portfolio(
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    q: Dict[str, Any] = {}
    if is_active is not None:
        q["is_active"] = is_active
    if is_featured is not None:
        q["is_featured"] = is_featured

    total = await db.portfolio.count_documents(q)
    cursor = db.portfolio.find(q).sort("created_at", -1).skip(offset).limit(limit)

    items: List[PortfolioOut] = []
    async for doc in cursor:
        items.append(_doc_to_portfolio_out(doc))

    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/{item_id}", response_model=PortfolioOut)
async def get_portfolio_item(item_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Item not found")

    doc = await db.portfolio.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")

    return _doc_to_portfolio_out(doc)


@router.post("/", response_model=PortfolioOut)
async def create_portfolio_item(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    is_featured: bool = Form(False),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    _admin=Depends(get_current_admin),
    db=Depends(get_db)
):
    data = {
        "title": title,
        "description": description,
        "category": category,
        "link": link,
        "is_featured": is_featured,
        "is_active": is_active,
        "created_at": datetime.now(timezone.utc),
    }

    if image:
        try:
            base_url = str(request.base_url)
            data["image_url"] = _save_image(image, base_url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    result = await db.portfolio.insert_one(data)
    new_doc = await db.portfolio.find_one({"_id": result.inserted_id})
    return _doc_to_portfolio_out(new_doc)


@router.put("/{item_id}", response_model=PortfolioOut)
async def update_portfolio_item(
    request: Request,
    item_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    is_featured: Optional[bool] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    _admin=Depends(get_current_admin),
    db=Depends(get_db)
):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Item not found")

    updates: Dict[str, Any] = {}
    if title is not None:
        updates["title"] = title
    if description is not None:
        updates["description"] = description
    if category is not None:
        updates["category"] = category
    if link is not None:
        updates["link"] = link
    if is_featured is not None:
        updates["is_featured"] = is_featured
    if is_active is not None:
        updates["is_active"] = is_active

    if image:
        base_url = str(request.base_url)
        updates["image_url"] = _save_image(image, base_url)

    if updates:
        result = await db.portfolio.update_one({"_id": ObjectId(item_id)}, {"$set": updates})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")

    doc = await db.portfolio.find_one({"_id": ObjectId(item_id)})
    return _doc_to_portfolio_out(doc)


@router.delete("/{item_id}", response_model=dict)
async def delete_portfolio_item(item_id: str, _admin=Depends(get_current_admin), db=Depends(get_db)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Item not found")

    result = await db.portfolio.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Portfolio item deleted successfully"}

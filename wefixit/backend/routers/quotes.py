from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import List
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

from backend.database import get_db
from .auth import get_current_admin

load_dotenv()
router = APIRouter()

# --- Email Settings ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "WeFixIt Quotes")

# --- Models ---
class Quote(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    company: str = ""
    serviceType: str
    projectTitle: str
    description: str
    features: List[str] = []
    timeline: str
    budget: str = ""
    hasExistingWebsite: str = ""
    preferredStyle: str = ""
    targetAudience: str = ""
    additionalNotes: str = ""


class Reply(BaseModel):
    content: str


# --- Email helper ---
def send_quote_email(quote: dict):
    try:
        subject = f"📩 New Quote Request from {quote['name']}"
        body = f"""
        You received a new quote request:

        Name: {quote['name']}
        Email: {quote['email']}
        Phone: {quote.get('phone', '')}
        Company: {quote.get('company', '')}

        Service: {quote['serviceType']}
        Project Title: {quote['projectTitle']}
        Description: {quote['description']}

        Features: {", ".join(quote.get('features', []))}
        Timeline: {quote['timeline']}
        Budget: {quote.get('budget', '')}

        Has Existing Website: {quote.get('hasExistingWebsite', '')}
        Preferred Style: {quote.get('preferredStyle', '')}
        Target Audience: {quote.get('targetAudience', '')}
        Additional Notes: {quote.get('additionalNotes', '')}

        Submitted at: {quote['created_at']}
        """

        msg = MIMEMultipart()
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_USER}>"
        msg["To"] = EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())

        print("[✅] Quote email sent successfully")

    except Exception as e:
        print(f"[❌] Failed to send quote email: {e}")


# --- Routes ---
@router.post("/", response_model=dict)
async def create_quote(quote: Quote, db=Depends(get_db)):
    quote_dict = quote.dict()
    quote_dict["created_at"] = datetime.utcnow()
    quote_dict["replies"] = []  # store replies here

    result = await db["quotes"].insert_one(quote_dict)
    quote_dict["_id"] = str(result.inserted_id)

    # Send notification email
    send_quote_email(quote_dict)

    return {"message": "Quote created successfully", "quote": quote_dict}


@router.get("/", response_model=List[dict])
async def get_quotes(db=Depends(get_db), user=Depends(get_current_admin)):
    quotes = await db["quotes"].find().to_list(100)
    for q in quotes:
        q["_id"] = str(q["_id"])
    return quotes


@router.delete("/{quote_id}")
async def delete_quote(quote_id: str, db=Depends(get_db), user=Depends(get_current_admin)):
    result = await db["quotes"].delete_one({"_id": ObjectId(quote_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {"message": "Quote deleted successfully"}


@router.post("/{quote_id}/reply")
async def reply_to_quote(quote_id: str, message: Reply, db=Depends(get_db), user=Depends(get_current_admin)):
    quote = await db["quotes"].find_one({"_id": ObjectId(quote_id)})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    reply = {
        "content": message.content,
        "sent_at": datetime.utcnow().isoformat(),
        "admin": user["username"] if "username" in user else "admin",
    }

    # Save reply in DB
    await db["quotes"].update_one(
        {"_id": ObjectId(quote_id)},
        {"$push": {"replies": reply}}
    )

    # Send reply via email
    try:
        subject = f"💬 Reply to your Quote Request - {quote['projectTitle']}"
        body = f"""
        Hi {quote['name']},

        {message.content}

        ---
        WeFixIt Team
        """

        msg = MIMEMultipart()
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_USER}>"
        msg["To"] = quote["email"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, quote["email"], msg.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

    return {"message": "Reply sent successfully", "reply": reply}


@router.delete("/{quote_id}/reply/{reply_index}")
async def delete_reply(quote_id: str, reply_index: int, db=Depends(get_db), user=Depends(get_current_admin)):
    quote = await db["quotes"].find_one({"_id": ObjectId(quote_id)})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    replies = quote.get("replies", [])
    if reply_index < 0 or reply_index >= len(replies):
        raise HTTPException(status_code=404, detail="Reply not found")

    # Remove reply
    replies.pop(reply_index)
    await db["quotes"].update_one(
        {"_id": ObjectId(quote_id)},
        {"$set": {"replies": replies}}
    )

    return {"message": "Reply deleted successfully"}


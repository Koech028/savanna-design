# backend/routers/contacts.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

from backend.database import get_db
from .auth import get_current_admin

load_dotenv()
router = APIRouter(tags=["contacts"])

# --- Email Settings ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Savanna Designs Contact")

# --- Models ---
class ContactCreate(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    company: str = ""
    subject: str
    message: str

# --- Email helper ---
def send_contact_email(contact: dict):
    try:
        subject = f"📧 New Contact Form Submission from {contact['firstName']} {contact['lastName']}"
        body = f"""
        You received a new contact form submission:

        Name: {contact['firstName']} {contact['lastName']}
        Email: {contact['email']}
        Company: {contact.get('company', '')}
        Subject: {contact['subject']}

        Message:
        {contact['message']}

        Submitted at: {contact['created_at']}
        """

        msg = MIMEMultipart()
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_USER}>"
        msg["To"] = EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())

        print("[✅] Contact email sent successfully")

    except Exception as e:
        print(f"[❌] Failed to send contact email: {e}")

# --- Routes ---
@router.post("/", response_model=dict)
async def create_contact(contact: ContactCreate, db=Depends(get_db)):
    contact_dict = contact.dict()
    contact_dict["created_at"] = datetime.utcnow()
    contact_dict["read"] = False  # Track if admin has read this

    result = await db["contacts"].insert_one(contact_dict)
    contact_dict["_id"] = str(result.inserted_id)

    # Send notification email
    send_contact_email(contact_dict)

    return {"message": "Contact form submitted successfully", "contact": contact_dict}

@router.get("/", response_model=list)
async def get_contacts(db=Depends(get_db), user=Depends(get_current_admin)):
    contacts = await db["contacts"].find().sort("created_at", -1).to_list(100)
    for contact in contacts:
        contact["_id"] = str(contact["_id"])
    return contacts

@router.delete("/{contact_id}")
async def delete_contact(contact_id: str, db=Depends(get_db), user=Depends(get_current_admin)):
    result = await db["contacts"].delete_one({"_id": ObjectId(contact_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}

@router.put("/{contact_id}/read")
async def mark_as_read(contact_id: str, db=Depends(get_db), user=Depends(get_current_admin)):
    result = await db["contacts"].update_one(
        {"_id": ObjectId(contact_id)},
        {"$set": {"read": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact marked as read"}
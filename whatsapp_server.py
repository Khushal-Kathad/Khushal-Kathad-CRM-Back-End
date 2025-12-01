# import os
# from fastapi import FastAPI, Request, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime
# from twilio.rest import Client
# from models import Contact, Lead
# from database import SessionLocal

# # ----------------------
# # 1️⃣ Twilio Credentials
# # ----------------------
# # Store these in environment variables for security
# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# # Initialize Twilio client
# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# # ----------------------
# # 2️⃣ FastAPI Setup
# # ----------------------
# app = FastAPI(title="WhatsApp Lead Webhook")

# # ----------------------
# # 3️⃣ Database Dependency
# # ----------------------
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ----------------------
# # 4️⃣ WhatsApp Webhook
# # ----------------------
# @app.post("/webhook/whatsapp")
# async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
#     """
#     Receives WhatsApp messages from Twilio, creates Contact + Lead, and sends auto-reply.
#     """
#     form = await request.form()
#     from_number = form.get("From")         # e.g., whatsapp:+919876543210
#     message_text = form.get("Body")        # message content
#     profile_name = form.get("ProfileName", "WhatsApp User")

#     if not from_number or not message_text:
#         raise HTTPException(status_code=400, detail="Invalid WhatsApp message payload")

#     # 1️⃣ Find or create Contact
#     contact = db.query(Contact).filter(Contact.ContactNo == from_number).first()
#     if not contact:
#         contact = Contact(
#             ContactFName=profile_name,
#             ContactLName="",
#             ContactNo=from_number,
#             ContactType="Prospect",
#             CreatedAt=datetime.utcnow()
#         )
#         db.add(contact)
#         db.commit()
#         db.refresh(contact)

#     # 2️⃣ Create Lead linked to Contact
#     lead = Lead(
#         LeadName=contact.ContactFName,
#         ContactId=contact.ContactId,
#         LeadSource="WhatsApp",
#         LeadNotes=message_text,
#         LeadStatus="New",
#         CreatedAt=datetime.utcnow()
#     )
#     db.add(lead)
#     db.commit()
#     db.refresh(lead)

#     # 3️⃣ Send auto-reply via Twilio
#     client.messages.create(
#         from_=TWILIO_WHATSAPP_NUMBER,
#         to=from_number,
#         body=f"Hi {contact.ContactFName}, we received your message and created a lead. Our team will contact you soon."
#     )

#     return {
#         "status": "lead created",
#         "LeadId": lead.LeadId,
#         "ContactId": contact.ContactId
#     }

# # ----------------------
# # 5️⃣ Root Test Endpoint
# # ----------------------
# @app.get("/")
# def root():
#     return {"message": "WhatsApp Lead Webhook is running."}

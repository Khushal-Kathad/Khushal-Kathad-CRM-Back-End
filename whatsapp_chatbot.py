# # whatsapp_chatbot.py

# import os
# from dotenv import load_dotenv
# from fastapi import FastAPI, Request, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime
# from twilio.rest import Client
# from models import Contact, Lead
# from database import SessionLocal
# from services.groq_client import GroqClient
# from services.context_manager import ConversationContext
# from services.intent_handlers import IntentHandler
# from schemas.schemas import WhatsAppConversationStats, WhatsAppConversationResponse
# from typing import Dict, List
# import logging

# # Load environment variables from .env file
# load_dotenv()

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ----------------------
# # Twilio & Groq Setup
# # ----------------------
# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# groq_client = GroqClient()

# # ----------------------
# # FastAPI Setup
# # ----------------------
# from fastapi import APIRouter

# # Create router for integration with main app
# router = APIRouter(
#     prefix="",
#     tags=["WhatsApp Chatbot"]
# )

# # Keep app instance for standalone mode (optional)
# app = FastAPI(title="WhatsApp AI Chatbot with Groq (SQL-Based)")

# # ----------------------
# # Database Dependency
# # ----------------------
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ----------------------
# # Message Processor
# # ----------------------
# class MessageProcessor:
#     """
#     Main orchestrator for processing WhatsApp messages.
#     Uses SQL Server for context management (no Redis required).
#     """

#     def __init__(self, db: Session):
#         self.db = db
#         self.intent_handler = IntentHandler(db)
#         self.context_manager = ConversationContext(db)

#     def process_message(
#         self,
#         phone_number: str,
#         message_text: str,
#         profile_name: str
#     ) -> str:
#         """
#         Main processing pipeline:
#         1. Get conversation context from SQL database
#         2. Detect intent using Groq
#         3. Handle intent and perform CRM operations
#         4. Generate response using Groq
#         5. Update context in SQL database
#         """

#         try:
#             # Step 1: Get conversation context from SQL
#             context = self.context_manager.get_context(phone_number)
#             logger.info(f"Processing message from {phone_number}: {message_text}")

#             # Step 2: Detect intent
#             intent_result = groq_client.detect_intent(
#                 message=message_text,
#                 context=context.get("messages", [])
#             )

#             intent = intent_result.get("intent", "general")
#             entities = intent_result.get("entities", {})
#             confidence = intent_result.get("confidence", 0.0)

#             logger.info(f"Detected intent: {intent} (confidence: {confidence})")
#             logger.info(f"Extracted entities: {entities}")

#             # Merge with accumulated entities
#             accumulated_entities = context.get("entities", {})
#             accumulated_entities.update(entities)

#             # Step 3: Handle intent and perform CRM operations
#             crm_data = {}
#             lead_id = context.get("lead_id")
#             contact_id = context.get("contact_id")
#             visit_id = context.get("visit_id")

#             # NEW: Handle brochure queries (answers from PDF content, NO file sending)
#             if intent == "brochure_query":
#                 response_text = self.intent_handler.handle_brochure_query(
#                     question=message_text,
#                     context=context.get("messages", [])
#                 )
#                 crm_data["answered_from_brochure"] = True

#             # NEW: Handle visit requests (creates Visit + Visitor, NOT Lead)
#             elif intent == "visit_request":
#                 visit_id, contact_id, response_text = self.intent_handler.handle_visit_request(
#                     phone_number=phone_number,
#                     profile_name=profile_name,
#                     entities=accumulated_entities,
#                     message=message_text
#                 )
#                 crm_data["visit_created"] = visit_id is not None
#                 logger.info(f"🏠 Visit created: VisitId={visit_id}, ContactId={contact_id}")

#             # Existing: Lead creation
#             elif intent == "lead_creation":
#                 lead_id, contact_id, info = self.intent_handler.handle_lead_creation(
#                     entities=accumulated_entities,
#                     phone_number=phone_number,
#                     message=message_text,
#                     profile_name=profile_name
#                 )
#                 crm_data["lead_info"] = info
#                 # Generate response for lead creation
#                 response_text = groq_client.generate_response(
#                     intent=intent,
#                     entities=accumulated_entities,
#                     context=context.get("messages", []),
#                     crm_data=crm_data
#                 )

#             elif intent == "information_query":
#                 crm_data = self.intent_handler.handle_information_query(
#                     entities=accumulated_entities
#                 )
#                 response_text = groq_client.generate_response(
#                     intent=intent,
#                     entities=accumulated_entities,
#                     context=context.get("messages", []),
#                     crm_data=crm_data
#                 )

#             elif intent == "followup_schedule":
#                 followup_id, info = self.intent_handler.handle_followup_schedule(
#                     lead_id=lead_id,
#                     entities=accumulated_entities,
#                     phone_number=phone_number
#                 )
#                 crm_data["followup_info"] = info
#                 response_text = groq_client.generate_response(
#                     intent=intent,
#                     entities=accumulated_entities,
#                     context=context.get("messages", []),
#                     crm_data=crm_data
#                 )

#             elif intent == "site_visit":
#                 # Keep old site_visit handler for backward compatibility
#                 visit_id, info = self.intent_handler.handle_site_visit(
#                     entities=accumulated_entities,
#                     phone_number=phone_number,
#                     lead_id=lead_id,
#                     contact_id=contact_id,
#                     profile_name=profile_name
#                 )
#                 crm_data["visit_info"] = info
#                 logger.info(f"Site visit created: Visit ID {visit_id}")
#                 response_text = groq_client.generate_response(
#                     intent=intent,
#                     entities=accumulated_entities,
#                     context=context.get("messages", []),
#                     crm_data=crm_data
#                 )

#             elif intent == "site_info":
#                 crm_data = self.intent_handler.handle_site_info(
#                     entities=accumulated_entities
#                 )
#                 response_text = groq_client.generate_response(
#                     intent=intent,
#                     entities=accumulated_entities,
#                     context=context.get("messages", []),
#                     crm_data=crm_data
#                 )

#             else:  # general or unknown intent
#                 response_text = groq_client.generate_response(
#                     intent=intent,
#                     entities=accumulated_entities,
#                     context=context.get("messages", []),
#                     crm_data=crm_data
#                 )

#             # Step 5: Update context in SQL database
#             self.context_manager.update_context(
#                 phone_number=phone_number,
#                 user_message=message_text,
#                 bot_response=response_text,
#                 intent=intent,
#                 entities=accumulated_entities,
#                 lead_id=lead_id,
#                 contact_id=contact_id,
#                 visit_id=visit_id  # NEW: Store visit ID in context
#             )

#             return response_text

#         except Exception as e:
#             logger.error(f"Error processing message: {e}", exc_info=True)
#             return "I apologize, but I'm having trouble processing your request. Let me connect you with our team."

# # ----------------------
# # WhatsApp Webhook
# # ----------------------
# @router.post("/webhook/whatsapp")
# async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
#     """
#     Enhanced WhatsApp webhook with Groq AI integration.
#     Uses SQL Server for conversation history (no Redis required).
#     """

#     try:
#         form = await request.form()
#         from_number = form.get("From")
#         message_text = form.get("Body")
#         profile_name = form.get("ProfileName", "WhatsApp User")

#         if not from_number or not message_text:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Invalid WhatsApp message payload"
#             )

#         # Process message through AI pipeline
#         processor = MessageProcessor(db)
#         response_text = processor.process_message(
#             phone_number=from_number,
#             message_text=message_text,
#             profile_name=profile_name
#         )

#         # Send response via Twilio
#         twilio_client.messages.create(
#             from_=TWILIO_WHATSAPP_NUMBER,
#             to=from_number,
#             body=response_text
#         )

#         return {
#             "status": "success",
#             "message": "Response sent",
#             "intent_detected": True
#         }

#     except HTTPException:
#         # Re-raise HTTPException without modification to preserve status code
#         raise
#     except Exception as e:
#         logger.error(f"Webhook error: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

# # ----------------------
# # Health Check & Status
# # ----------------------
# @router.get("/whatsapp")
# def root():
#     return {
#         "service": "WhatsApp AI Chatbot with Groq",
#         "version": "1.0",
#         "status": "running",
#         "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
#         "context_storage": "SQL Server (no Redis)"
#     }

# @router.get("/whatsapp/health")
# def health_check(db: Session = Depends(get_db)):
#     """Check system health including database connection."""
#     from sqlalchemy import text

#     try:
#         # Test database connection
#         db.execute(text("SELECT 1"))
#         db_status = "connected"
#     except Exception as e:
#         db_status = f"error: {str(e)}"

#     return {
#         "status": "healthy" if db_status == "connected" else "unhealthy",
#         "database": db_status,
#         "groq_model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
#         "twilio_configured": bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)
#     }

# @router.get("/conversations/stats", response_model=WhatsAppConversationStats)
# def conversation_stats(db: Session = Depends(get_db)):
#     """Get conversation statistics."""
#     from models import WhatsAppConversation
#     from sqlalchemy import func

#     try:
#         total_conversations = db.query(func.count(WhatsAppConversation.Id)).scalar()
#         unique_users = db.query(func.count(func.distinct(WhatsAppConversation.PhoneNumber))).scalar()
#         unique_sessions = db.query(func.count(func.distinct(WhatsAppConversation.SessionId))).scalar()

#         intent_counts = db.query(
#             WhatsAppConversation.Intent,
#             func.count(WhatsAppConversation.Id)
#         ).group_by(WhatsAppConversation.Intent).all()

#         return WhatsAppConversationStats(
#             total_messages=total_conversations or 0,
#             unique_users=unique_users or 0,
#             total_sessions=unique_sessions or 0,
#             intents={intent: count for intent, count in intent_counts if intent}
#         )

#     except Exception as e:
#         logger.error(f"Stats error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/conversations/{phone_number}", response_model=List[WhatsAppConversationResponse])
# def get_conversations(
#     phone_number: str,
#     skip: int = 0,
#     limit: int = 50,
#     db: Session = Depends(get_db)
# ):
#     """
#     Get conversation history for a specific phone number.

#     Args:
#         phone_number: Phone number to query (with or without 'whatsapp:' prefix)
#         skip: Number of records to skip (pagination)
#         limit: Maximum number of records to return
#     """
#     from models import WhatsAppConversation

#     try:
#         # Clean phone number
#         clean_phone = phone_number.replace("whatsapp:", "")

#         conversations = db.query(WhatsAppConversation).filter(
#             WhatsAppConversation.PhoneNumber.like(f"%{clean_phone}%")
#         ).order_by(
#             WhatsAppConversation.Timestamp.desc()
#         ).offset(skip).limit(limit).all()

#         return conversations

#     except Exception as e:
#         logger.error(f"Error fetching conversations: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# # ----------------------
# # Test Endpoints
# # ----------------------
# @router.post("/test/intent")
# async def test_intent(message: str, db: Session = Depends(get_db)):
#     """Test intent detection without sending WhatsApp message."""
#     try:
#         result = groq_client.detect_intent(message=message, context=[])
#         return {
#             "message": message,
#             "intent": result.get("intent"),
#             "confidence": result.get("confidence"),
#             "entities": result.get("entities")
#         }
#     except Exception as e:
#         return {"error": str(e)}


# @router.post("/test/chat")
# async def test_chat(
#     message: str,
#     phone_number: str = "whatsapp:+919999999999",
#     profile_name: str = "Test User",
#     db: Session = Depends(get_db)
# ):
#     """
#     Test complete chatbot conversation flow without sending actual WhatsApp message.

#     This endpoint simulates the full message processing pipeline:
#     1. Detects intent
#     2. Extracts entities
#     3. Performs CRM operations (creates leads, visits, etc.)
#     4. Generates bot response

#     Parameters:
#     - message: The user's message to test
#     - phone_number: Optional phone number (default: test number)
#     - profile_name: Optional user name (default: "Test User")

#     Returns:
#     - user_message: The message you sent
#     - bot_response: What the bot would reply
#     - intent: Detected intent
#     - confidence: Confidence score
#     - entities: Extracted entities
#     - crm_actions: Any CRM actions performed (lead created, visit scheduled, etc.)
#     """
#     try:
#         logger.info(f"TEST CHAT: Processing message from {phone_number}: {message}")

#         # Process message through the same pipeline as real WhatsApp messages
#         processor = MessageProcessor(db)

#         # Get the bot's response
#         bot_response = processor.process_message(
#             phone_number=phone_number,
#             message_text=message,
#             profile_name=profile_name
#         )

#         # Get the context to show what was detected
#         context_manager = ConversationContext(db)
#         context = context_manager.get_context(phone_number)

#         # Get the latest message from context
#         latest_message = context.get("messages", [])[-1] if context.get("messages") else {}

#         return {
#             "status": "success",
#             "user_message": message,
#             "bot_response": bot_response,
#             "intent": latest_message.get("intent", "unknown"),
#             "confidence": "N/A",  # Not stored in context
#             "entities": context.get("entities", {}),
#             "crm_actions": {
#                 "lead_id": context.get("lead_id"),
#                 "contact_id": context.get("contact_id"),
#                 "visit_id": context.get("visit_id")
#             },
#             "conversation_context": {
#                 "total_messages": len(context.get("messages", [])),
#                 "last_updated": context.get("last_updated")
#             }
#         }

#     except Exception as e:
#         logger.error(f"TEST CHAT ERROR: {e}", exc_info=True)
#         return {
#             "status": "error",
#             "error": str(e),
#             "user_message": message
#         }

# # Include router in app for standalone mode
# app.include_router(router)

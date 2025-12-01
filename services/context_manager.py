# services/context_manager.py

from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models import WhatsAppConversation
import json
import uuid

class ConversationContext:
    """
    Manages conversation context using SQL Server instead of Redis.
    Stores user conversation history, state, and extracted entities.
    """

    def __init__(self, db: Session):
        self.db = db
        self.timeout_minutes = 30  # Session timeout
        self.max_messages = 10     # Max messages to keep in context

    def _get_or_create_session_id(self, phone_number: str) -> str:
        """Get active session or create new one."""

        # Find recent active session (within timeout)
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.timeout_minutes)

        recent_conv = self.db.query(WhatsAppConversation).filter(
            WhatsAppConversation.PhoneNumber == phone_number,
            WhatsAppConversation.Timestamp > cutoff_time
        ).order_by(WhatsAppConversation.Timestamp.desc()).first()

        if recent_conv:
            return recent_conv.SessionId
        else:
            # Create new session
            return str(uuid.uuid4())

    def get_context(self, phone_number: str) -> Dict:
        """
        Retrieve conversation context for a user.

        Returns:
        {
            "session_id": "uuid",
            "messages": [],
            "entities": {},
            "current_intent": "",
            "last_updated": "",
            "lead_id": None,
            "contact_id": None
        }
        """

        session_id = self._get_or_create_session_id(phone_number)
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.timeout_minutes)

        # Get recent messages from this session
        conversations = self.db.query(WhatsAppConversation).filter(
            WhatsAppConversation.PhoneNumber == phone_number,
            WhatsAppConversation.SessionId == session_id,
            WhatsAppConversation.Timestamp > cutoff_time
        ).order_by(WhatsAppConversation.Timestamp.asc()).all()

        if not conversations:
            # Return empty context for new conversation
            return {
                "session_id": session_id,
                "messages": [],
                "entities": {},
                "current_intent": None,
                "last_updated": datetime.utcnow().isoformat(),
                "lead_id": None,
                "contact_id": None,
                "visit_id": None  # NEW
            }

        # Build context from database records
        messages = []
        accumulated_entities = {}
        current_intent = None
        lead_id = None
        contact_id = None
        visit_id = None  # NEW

        for conv in conversations:
            messages.append({
                "timestamp": conv.Timestamp.isoformat(),
                "user_message": conv.UserMessage,
                "bot_response": conv.BotResponse,
                "intent": conv.Intent
            })

            # Merge entities
            if conv.Entities:
                try:
                    entities = json.loads(conv.Entities)
                    accumulated_entities.update(entities)
                except:
                    pass

            current_intent = conv.Intent
            lead_id = conv.LeadId if conv.LeadId else lead_id
            contact_id = conv.ContactId if conv.ContactId else contact_id
            visit_id = conv.VisitId if conv.VisitId else visit_id  # NEW

        return {
            "session_id": session_id,
            "messages": messages[-self.max_messages:],  # Keep only recent messages
            "entities": accumulated_entities,
            "current_intent": current_intent,
            "last_updated": conversations[-1].Timestamp.isoformat() if conversations else datetime.utcnow().isoformat(),
            "lead_id": lead_id,
            "contact_id": contact_id,
            "visit_id": visit_id  # NEW
        }

    def update_context(
        self,
        phone_number: str,
        user_message: str,
        bot_response: str,
        intent: str,
        entities: Dict,
        lead_id: Optional[int] = None,
        contact_id: Optional[int] = None,
        visit_id: Optional[int] = None  # NEW
    ):
        """Save new message to database."""

        context = self.get_context(phone_number)
        session_id = context["session_id"]

        conversation = WhatsAppConversation(
            PhoneNumber=phone_number,
            UserMessage=user_message,
            BotResponse=bot_response,
            Intent=intent,
            Entities=json.dumps(entities),
            SessionId=session_id,
            LeadId=lead_id,
            ContactId=contact_id,
            VisitId=visit_id,  # NEW
            Timestamp=datetime.utcnow(),
            CreatedDate=datetime.utcnow(),
            UpdatedDate=datetime.utcnow()
        )

        self.db.add(conversation)
        self.db.commit()

        # Clean up old messages (optional - keep only recent ones)
        self._cleanup_old_messages(phone_number, session_id)

    def _cleanup_old_messages(self, phone_number: str, session_id: str):
        """Keep only recent messages to avoid database bloat."""

        conversations = self.db.query(WhatsAppConversation).filter(
            WhatsAppConversation.PhoneNumber == phone_number,
            WhatsAppConversation.SessionId == session_id
        ).order_by(WhatsAppConversation.Timestamp.desc()).all()

        # Keep only max_messages, delete older ones
        if len(conversations) > self.max_messages:
            old_convs = conversations[self.max_messages:]
            for conv in old_convs:
                self.db.delete(conv)
            self.db.commit()

    def clear_context(self, phone_number: str):
        """Clear conversation context for a user."""

        self.db.query(WhatsAppConversation).filter(
            WhatsAppConversation.PhoneNumber == phone_number
        ).delete()
        self.db.commit()

    def get_accumulated_entities(self, phone_number: str) -> Dict:
        """Get all entities accumulated in the conversation."""
        context = self.get_context(phone_number)
        return context.get("entities", {})

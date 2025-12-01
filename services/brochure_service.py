# services/brochure_service.py

import os
import logging
from typing import Dict, List, Optional
from groq import Groq
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Brochure

logger = logging.getLogger(__name__)

class BrochureService:
    """
    Reads brochure data from database and provides intelligent answers
    based on complete property information.

    Data Source: Database (Brochure table)
    The brochure file is NEVER sent to users - only answers from its content.
    """

    def __init__(self, project_name: str = None, site_id: int = None, db: Session = None):
        self.project_name = project_name
        self.site_id = site_id
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self._db = db
        self._should_close_db = False

        # Storage for brochure content
        self.brochure_text = ""
        self.brochure_data = {}
        self.brochure_id = None

        # Load brochure on initialization
        self.load_brochure()

    def _get_db(self) -> Session:
        """Get database session, creating one if not provided."""
        if self._db is None:
            self._db = SessionLocal()
            self._should_close_db = True
        return self._db

    def _close_db(self):
        """Close database session if we created it."""
        if self._should_close_db and self._db:
            self._db.close()
            self._db = None
            self._should_close_db = False

    def load_brochure(self):
        """
        Load brochure data from database.
        Supports multiple loading strategies:
        1. By project_name (if specified)
        2. By site_id (if specified)
        3. First active brochure (if nothing specified)
        """
        try:
            db = self._get_db()

            # Build query based on available filters
            query = db.query(Brochure).filter(
                Brochure.IsActive == True,
                Brochure.IsDeleted == False
            )

            # Add filters based on what's provided
            if self.project_name:
                query = query.filter(Brochure.ProjectName == self.project_name)
                logger.info(f"📝 Loading brochure for project: {self.project_name}")
            elif self.site_id:
                query = query.filter(Brochure.SiteId == self.site_id)
                logger.info(f"📝 Loading brochure for site ID: {self.site_id}")
            else:
                logger.info(f"📝 Loading first available active brochure")

            # Get the brochure
            brochure = query.order_by(Brochure.CreatedDate.desc()).first()

            if not brochure:
                filter_info = f"project: {self.project_name}" if self.project_name else \
                             f"site_id: {self.site_id}" if self.site_id else "any active brochure"
                logger.warning(f"✗ No active brochure found in database for {filter_info}")
                logger.warning(f"💡 Please upload a brochure using POST /brochure/upload API")
                self.brochure_text = ""
                self.brochure_data = {}
                self.brochure_id = None
                self.project_name = None
                return

            # Load text and structured data
            self.brochure_text = brochure.RawText or ""
            self.brochure_data = brochure.StructuredData or {}
            self.brochure_id = brochure.BrochureId
            self.project_name = brochure.ProjectName  # Update with actual project name

            logger.info(f"✓ Brochure loaded successfully: {len(self.brochure_text)} characters")
            logger.info(f"✓ Brochure ID: {self.brochure_id}")
            logger.info(f"✓ Project: {self.project_name}")
            logger.info(f"✓ Configurations: {len(self.brochure_data.get('configurations', []))} types")
            logger.info(f"✓ Amenities: {len(self.brochure_data.get('amenities', []))} listed")

        except Exception as e:
            logger.error(f"✗ Failed to load brochure from database: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.brochure_text = ""
            self.brochure_data = {}
            self.brochure_id = None
        finally:
            # Close DB if we created it
            if self._should_close_db:
                self._close_db()

    def reload_brochure(self):
        """
        Reload brochure data from database.
        Useful for refreshing data after updates.
        """
        logger.info(f"🔄 Reloading brochure for project: {self.project_name}")
        self.load_brochure()

    def answer_from_brochure(
        self,
        question: str,
        conversation_context: List[Dict] = None
    ) -> str:
        """
        Answer user questions using brochure knowledge.
        This is the main function called when user asks about property.

        Args:
            question: User's question about the property
            conversation_context: Previous conversation for context

        Returns:
            Intelligent answer based on brochure content
        """
        if not self.brochure_text:
            return "I'm currently unable to access property information. Please try again in a moment."

        # Build context with brochure knowledge
        system_prompt = f"""You are a helpful and friendly real estate assistant for Swagat Cilantra properties.

COMPLETE BROCHURE KNOWLEDGE (Structured Data):
{json.dumps(self.brochure_data, indent=2)}

FULL BROCHURE CONTENT (Reference for additional details):
{self.brochure_text[:15000]}

KEY PROPERTY INFORMATION:
- Project: Swagat Cilantra - "Realty Beyond Luxury"
- Developer: Swagat Builders (Est. 2006, 18+ years experience, 5000+ happy families)
- Location: Opposite Punya Bhoomi, Near Second VIP Road, Vesu, Surat
- Total Units: 144 (Exclusive residential tower with 4 towers A, B, C, D)
- Open Space: 70% with 40,000 Sq.Ft Central Open Space
- Amenities: 40+ premium amenities including Banquet Hall, Swimming Pool, Gym, etc.
- Configurations: 3 BHK (1138-1643 Sq.Ft) and 4 BHK Penthouses (1747-2496 Sq.Ft)

INSTRUCTIONS:
- Answer questions ONLY from the brochure content above
- Be friendly, warm, and conversational (use a professional yet approachable tone)
- Keep answers concise (2-4 sentences) but informative
- When asked about configurations, provide specific carpet areas and details
- When asked about amenities, highlight 2-3 relevant ones based on the question
- When asked about location, mention connectivity (Airport 15 min, VR Mall 10 min, etc.)
- If information is NOT in the brochure, say: "I don't have that specific information, but I can connect you with our team who can help."
- Provide specific details like sizes, features, amenities when asked
- Use numbers and facts from the brochure for credibility
- End with an engaging follow-up question when appropriate (e.g., "Would you like to know more about the amenities?" or "Interested in scheduling a site visit?")

IMPORTANT: You are answering FROM brochure knowledge, NOT sending the PDF file to the user."""

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation context for better follow-up answers
        if conversation_context:
            for ctx in conversation_context[-3:]:  # Last 3 exchanges
                messages.append({
                    "role": "user",
                    "content": ctx.get("user_message", "")
                })
                messages.append({
                    "role": "assistant",
                    "content": ctx.get("bot_response", "")
                })

        # Add current question
        messages.append({"role": "user", "content": question})

        try:
            logger.info(f"💬 Answering question: {question[:50]}...")

            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=250
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"✓ Generated answer ({len(answer)} chars)")

            return answer

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I'm having trouble processing that question right now. Let me connect you with our team who can provide all the details."

    def get_site_context(self) -> Dict:
        """
        Get site information for visit creation.
        Returns structured data that can be used when scheduling visits.
        """
        return {
            "project_name": self.brochure_data.get("project_name", "Cilantra"),
            "location": self.brochure_data.get("location", {}),
            "configurations": self.brochure_data.get("configurations", []),
            "amenities": self.brochure_data.get("amenities", [])
        }

    def get_quick_summary(self) -> str:
        """Get a brief summary of the property for introductions."""
        if not self.brochure_data:
            return "Swagat Cilantra - a premium residential property in Vesu, Surat"

        project = self.brochure_data.get("project_name", "Swagat Cilantra")
        tagline = self.brochure_data.get("tagline", "")
        location = self.brochure_data.get("location", {}).get("area", "Vesu")
        city = self.brochure_data.get("location", {}).get("city", "Surat")
        total_units = self.brochure_data.get("total_units", 144)
        amenities = self.brochure_data.get("total_amenities", "40+")

        summary = f"{project} - '{tagline}' by Swagat Builders. Located in {location}, {city} with {total_units} exclusive units and {amenities} premium amenities featuring 3 BHK and 4 BHK Penthouses."

        return summary

    def is_loaded(self) -> bool:
        """Check if brochure is successfully loaded."""
        return bool(self.brochure_text and self.brochure_data)

    def get_project_info(self) -> Dict:
        """Get comprehensive project information."""
        return {
            "name": self.brochure_data.get("project_name", "Swagat Cilantra"),
            "tagline": self.brochure_data.get("tagline", "Realty Beyond Luxury"),
            "developer": self.brochure_data.get("developer", {}).get("name", "Swagat Builders"),
            "location": self.brochure_data.get("location", {}).get("area", "Vesu"),
            "city": self.brochure_data.get("location", {}).get("city", "Surat"),
            "total_units": self.brochure_data.get("total_units", 144),
            "amenities_count": self.brochure_data.get("total_amenities", "40+"),
            "summary": self.get_quick_summary(),
            "loaded": self.is_loaded()
        }

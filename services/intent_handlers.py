# services/intent_handlers.py

from sqlalchemy.orm import Session
from typing import Dict, Optional, Tuple, List
from models import Lead, Contact, FollowUps, Site, Visit, Visitors
from datetime import datetime, timedelta
import re
import os
import logging
from services.brochure_service import BrochureService

logger = logging.getLogger(__name__)

class IntentHandler:
    """
    Handles different intents and performs CRM operations.
    Enhanced with brochure query and visit creation.
    """

    def __init__(self, db: Session):
        self.db = db

        # Initialize brochure service with database session
        # No hardcoded project name - will load first active brochure automatically
        self.brochure_service = BrochureService(db=db)

        if self.brochure_service.is_loaded():
            logger.info(f"✓ Brochure service ready - loaded project: {self.brochure_service.project_name}")
        else:
            logger.warning("✗ Brochure service not loaded - please upload brochure via API")

    def handle_lead_creation(
        self,
        entities: Dict,
        phone_number: str,
        message: str,
        profile_name: str = ""
    ) -> Tuple[Optional[int], Optional[int], str]:
        """
        Create or update lead in CRM.

        Returns:
            (lead_id, contact_id, additional_info)
        """

        # Clean phone number
        clean_phone = self._clean_phone_number(phone_number)

        # Find or create contact
        contact = self.db.query(Contact).filter(
            Contact.ContactNo == clean_phone
        ).first()

        if not contact:
            # Extract first and last name from profile_name
            name_parts = profile_name.split() if profile_name else ["WhatsApp", "User"]
            fname = entities.get("name", name_parts[0])
            lname = " ".join(name_parts[1:]) if len(name_parts) > 1 else entities.get("last_name", "")

            contact = Contact(
                ContactFName=fname,
                ContactLName=lname,
                ContactNo=clean_phone,
                ContactType="Customer",
                CreatedDate=datetime.utcnow(),
                UpdatedDate=datetime.utcnow()
            )
            self.db.add(contact)
            self.db.commit()
            self.db.refresh(contact)

        # Create lead with full name
        full_name = f"{contact.ContactFName} {contact.ContactLName}".strip()
        lead = Lead(
            LeadName=full_name,
            ContactId=contact.ContactId,
            LeadSource="WhatsApp",
            LeadType="Online",
            # LeadNotes=self._build_lead_notes(message, entities),
            LeadStatus="New",
            # Bedrooms=entities.get("bedrooms"),
            # SizeSqFt=entities.get("size"),
            # RequestedAmount=self._parse_budget(entities.get("budget")),  # Store budget in RequestedAmount
            CreatedDate=datetime.utcnow(),
            UpdatedDate=datetime.utcnow()
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)

        additional_info = f"Lead created: {lead.LeadName}"
        if entities.get("property_type"):
            additional_info += f", Looking for: {entities['property_type']}"

        return lead.LeadId, contact.ContactId, additional_info

    def handle_brochure_query(
        self,
        question: str,
        context: List[Dict]
    ) -> str:
        """
        Answer questions from brochure content.
        PDF is NOT sent - only intelligent answers from content.

        Args:
            question: User's question about the property
            context: Conversation history for context

        Returns:
            Intelligent answer from brochure knowledge
        """
        try:
            if not self.brochure_service.is_loaded():
                return "I'm currently unable to access property information. Let me connect you with our team who can help you immediately."

            answer = self.brochure_service.answer_from_brochure(
                question=question,
                conversation_context=context
            )

            logger.info(f"✓ Answered brochure query: {question[:50]}")
            return answer

        except Exception as e:
            logger.error(f"Brochure query error: {e}")
            return "I apologize for the inconvenience. Let me connect you with our team who can provide all the details you need."

    def handle_visit_request(
        self,
        phone_number: str,
        profile_name: str,
        entities: Dict,
        message: str
    ) -> Tuple[Optional[int], Optional[int], str]:
        """
        Create Visit and Visitor records when user wants to visit.
        Creates Contact → Visit → Visitors flow (NOT Lead initially).

        Args:
            phone_number: User's WhatsApp number
            profile_name: User's WhatsApp profile name
            entities: Extracted entities from message
            message: Original message text

        Returns:
            (visit_id, contact_id, response_message)
        """
        try:
            clean_phone = self._clean_phone_number(phone_number)

            # Step 1: Find or create Contact
            contact = self.db.query(Contact).filter(
                Contact.ContactNo == clean_phone
            ).first()

            if not contact:
                # Create new contact
                name_parts = profile_name.split() if profile_name else ["WhatsApp", "User"]
                fname = entities.get("name", name_parts[0])
                lname = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                contact = Contact(
                    ContactFName=fname,
                    ContactLName=lname,
                    ContactNo=clean_phone,
                    ContactType="Customer",  # Default to Customer
                    CreatedDate=datetime.utcnow(),
                    UpdatedDate=datetime.utcnow()
                )
                self.db.add(contact)
                self.db.commit()
                self.db.refresh(contact)
                logger.info(f"✓ Created contact: {contact.ContactId} - {contact.ContactFName}")

            # Step 2: Get Site information
            site_id = int(os.getenv("DEFAULT_SITE_ID", "1"))
            site = self.db.query(Site).filter(Site.SiteId == site_id).first()

            if not site:
                logger.error(f"Site not found: {site_id}")
                return None, contact.ContactId, "I'd love to schedule your visit! Our team will contact you shortly to arrange a convenient time."

            # Step 3: Parse visit date
            visit_date = self._parse_visit_date(entities.get("preferred_date"))

            # Step 4: Create Visit record
            visit = Visit(
                SiteId=site.SiteId,
                InfraId=None,  # Can be set if specific building mentioned
                VisitDate=visit_date,
                VisitStatus="Scheduled",
                # Purpose="Property Tour",
                VisitOutlook="Positive",
                # SalesPersonId=int(os.getenv("DEFAULT_SALESPERSON_ID", "1")),
                CreatedDate=datetime.utcnow(),
                UpdatedDate=datetime.utcnow()
            )
            self.db.add(visit)
            self.db.commit()
            self.db.refresh(visit)
            logger.info(f"✓ Created visit: {visit.VisitId} for site {site.SiteName}")

            # Step 5: Create Visitor record
            visitor = Visitors(
                VisitId=visit.VisitId,
                ContactId=contact.ContactId,
                LeadId=None,  # Will be created later if needed
                # PropertyType=entities.get("property_type"),
                Bedrooms=entities.get("bedrooms"),
                BuyingIntent=entities.get("buying_intent"),
                Notes=f"Visit requested via WhatsApp. Message: {message[:200]}",
                VisitType="Site Visit",
                CreatedDate=datetime.utcnow(),
                UpdatedDate=datetime.utcnow(),
                IsDeleted="No"
            )
            self.db.add(visitor)
            self.db.commit()
            self.db.refresh(visitor)
            logger.info(f"✓ Created visitor: {visitor.VisitorsId}")

            # Step 6: Prepare response message
            visit_date_str = visit.VisitDate.strftime("%B %d, %Y at %I:%M %p")
            response = f"Great! I've scheduled your visit to {site.SiteName} for {visit_date_str}. "
            response += f"Our team will contact you shortly to confirm the details. "
            response += f"Looking forward to seeing you! Visit ID: {visit.VisitId}"

            return visit.VisitId, contact.ContactId, response

        except Exception as e:
            logger.error(f"Visit creation error: {e}", exc_info=True)
            return None, None, "I've noted your interest in visiting! Our team will reach out shortly to schedule your visit at a convenient time."

    def handle_information_query(
        self,
        entities: Dict
    ) -> Dict:
        """
        Retrieve information from CRM based on query.
        """

        result = {}

        # Query sites if location mentioned
        if entities.get("location"):
            sites = self.db.query(Site).filter(
                Site.SiteCity.ilike(f"%{entities['location']}%")
            ).limit(3).all()

            result["sites"] = [
                {
                    "name": site.SiteName,
                    "location": site.SiteCity,
                    "address": site.SiteAddress,
                    "site_id": site.SiteId
                }
                for site in sites
            ]

        # Add property type filtering if needed
        if entities.get("property_type"):
            result["property_type"] = entities["property_type"]

        return result

    def handle_followup_schedule(
        self,
        lead_id: Optional[int],
        entities: Dict,
        phone_number: str
    ) -> Tuple[Optional[int], str]:
        """
        Schedule a follow-up for the lead.
        """

        clean_phone = self._clean_phone_number(phone_number)

        if not lead_id:
            # Try to find existing lead by phone
            contact = self.db.query(Contact).filter(
                Contact.ContactNo == clean_phone
            ).first()

            if contact:
                lead = self.db.query(Lead).filter(
                    Lead.ContactId == contact.ContactId
                ).order_by(Lead.CreatedDate.desc()).first()

                if lead:
                    lead_id = lead.LeadId

        if lead_id:
            followup = FollowUps(
                LeadId=lead_id,
                FollowUpType="WhatsApp Request",
                Status="Pending",
                Notes=f"Callback requested. Preferred time: {entities.get('preferred_time', 'ASAP')}",
                FollowUpDate=datetime.utcnow(),
                CreatedDate=datetime.utcnow(),
                UpdatedDate=datetime.utcnow()
            )
            self.db.add(followup)
            self.db.commit()
            self.db.refresh(followup)

            return followup.FollowUpsId, f"Follow-up scheduled for lead {lead_id}"

        return None, "Could not find associated lead"

    def handle_site_visit(
        self,
        entities: Dict,
        phone_number: str,
        lead_id: Optional[int] = None,
        contact_id: Optional[int] = None,
        profile_name: str = ""
    ) -> Tuple[Optional[int], str]:
        """
        Schedule a site visit for the customer.

        Returns:
            (visit_id, additional_info)
        """

        clean_phone = self._clean_phone_number(phone_number)

        # Find or create contact if not provided
        if not contact_id:
            contact = self.db.query(Contact).filter(
                Contact.ContactNo == clean_phone
            ).first()

            if not contact:
                # Extract first and last name from profile_name
                name_parts = profile_name.split() if profile_name else ["WhatsApp", "User"]
                fname = entities.get("name", name_parts[0])
                lname = " ".join(name_parts[1:]) if len(name_parts) > 1 else entities.get("last_name", "")

                # Create new contact
                contact = Contact(
                    ContactFName=fname,
                    ContactLName=lname,
                    ContactNo=clean_phone,
                    ContactType="Customer",
                    CreatedDate=datetime.utcnow(),
                    UpdatedDate=datetime.utcnow()
                )
                self.db.add(contact)
                self.db.commit()
                self.db.refresh(contact)

            contact_id = contact.ContactId

        # Find or create lead if not provided
        if not lead_id:
            lead = self.db.query(Lead).filter(
                Lead.ContactId == contact_id
            ).order_by(Lead.CreatedDate.desc()).first()

            if not lead:
                # Get contact to build full name
                contact = self.db.query(Contact).filter(Contact.ContactId == contact_id).first()
                full_name = f"{contact.ContactFName} {contact.ContactLName}".strip() if contact else "WhatsApp User"

                # Create new lead
                lead = Lead(
                    LeadName=full_name,
                    ContactId=contact_id,
                    LeadSource="WhatsApp",
                    LeadType="Online",
                    LeadNotes=f"Site visit requested via WhatsApp",
                    LeadStatus="New",
                    RequestedAmount=self._parse_budget(entities.get("budget")),
                    CreatedDate=datetime.utcnow(),
                    UpdatedDate=datetime.utcnow()
                )
                self.db.add(lead)
                self.db.commit()
                self.db.refresh(lead)

            lead_id = lead.LeadId

        # Find site if location/site name mentioned
        site_id = None
        if entities.get("location") or entities.get("site_name"):
            site_query = self.db.query(Site)

            if entities.get("site_name"):
                site_query = site_query.filter(Site.SiteName.ilike(f"%{entities['site_name']}%"))
            elif entities.get("location"):
                site_query = site_query.filter(Site.SiteCity.ilike(f"%{entities['location']}%"))

            site = site_query.first()
            if site:
                site_id = site.SiteId

        # Parse visit date
        visit_date = self._parse_visit_date(entities.get("preferred_date", entities.get("preferred_time")))

        # Create visit record
        visit = Visit(
            SiteId=site_id,
            VisitDate=visit_date,
            VisitStatus="Scheduled",
            Purpose=f"Site visit requested via WhatsApp. {entities.get('property_type', '')}".strip(),
            VisitOutlook="Positive",
            CreatedDate=datetime.utcnow(),
            UpdatedDate=datetime.utcnow()
        )
        self.db.add(visit)
        self.db.commit()
        self.db.refresh(visit)

        # Create follow-up for the visit
        followup = FollowUps(
            LeadId=lead_id,
            FollowUpType="Site Visit",
            Status="Scheduled",
            Notes=f"Site visit scheduled for {visit_date.strftime('%Y-%m-%d %H:%M')}",
            FollowUpDate=visit_date,
            CreatedDate=datetime.utcnow(),
            UpdatedDate=datetime.utcnow()
        )
        self.db.add(followup)
        self.db.commit()

        additional_info = f"Site visit scheduled for {visit_date.strftime('%Y-%m-%d')}"
        if site_id:
            site = self.db.query(Site).filter(Site.SiteId == site_id).first()
            if site:
                additional_info += f" at {site.SiteName}"

        return visit.VisitId, additional_info

    def handle_site_info(self, entities: Dict) -> Dict:
        """
        Get detailed site information.
        """

        sites_data = []

        if entities.get("location"):
            sites = self.db.query(Site).filter(
                Site.SiteCity.ilike(f"%{entities['location']}%")
            ).limit(5).all()

            for site in sites:
                sites_data.append({
                    "name": site.SiteName,
                    "city": site.SiteCity,
                    "address": site.SiteAddress,
                    "status": site.SiteStatus,
                    "site_id": site.SiteId
                })

        return {"sites": sites_data}

    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean phone number by removing whatsapp: prefix and special characters."""
        clean = phone_number.replace("whatsapp:", "").replace("+", "").replace("-", "").replace(" ", "")
        # Keep only digits
        clean = re.sub(r'\D', '', clean)
        return clean

    def _parse_visit_date(self, date_str: Optional[str]) -> datetime:
        """
        Parse visit date from natural language.
        Default to tomorrow at 10 AM if not specified.
        """

        if not date_str:
            # Default to tomorrow at 10 AM
            return datetime.utcnow() + timedelta(days=1, hours=10)

        date_str_lower = date_str.lower()

        # Check for common phrases
        if "today" in date_str_lower:
            base_date = datetime.utcnow()
        elif "tomorrow" in date_str_lower:
            base_date = datetime.utcnow() + timedelta(days=1)
        elif "day after tomorrow" in date_str_lower or "day after" in date_str_lower:
            base_date = datetime.utcnow() + timedelta(days=2)
        elif "next week" in date_str_lower:
            base_date = datetime.utcnow() + timedelta(days=7)
        elif "this weekend" in date_str_lower or "weekend" in date_str_lower:
            # Next Saturday
            days_until_saturday = (5 - datetime.utcnow().weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            base_date = datetime.utcnow() + timedelta(days=days_until_saturday)
        else:
            # Default to tomorrow
            base_date = datetime.utcnow() + timedelta(days=1)

        # Set time to 10 AM by default
        visit_datetime = base_date.replace(hour=10, minute=0, second=0, microsecond=0)

        # Try to extract time if mentioned
        if "morning" in date_str_lower:
            visit_datetime = visit_datetime.replace(hour=10)
        elif "afternoon" in date_str_lower:
            visit_datetime = visit_datetime.replace(hour=14)
        elif "evening" in date_str_lower:
            visit_datetime = visit_datetime.replace(hour=17)

        return visit_datetime

    def _build_lead_notes(self, message: str, entities: Dict) -> str:
        """Build comprehensive lead notes from message and entities."""

        notes = [f"Initial Message: {message}"]

        if entities.get("budget"):
            notes.append(f"Budget: {entities['budget']}")
        if entities.get("property_type"):
            notes.append(f"Property Type: {entities['property_type']}")
        if entities.get("location"):
            notes.append(f"Preferred Location: {entities['location']}")
        if entities.get("bedrooms"):
            notes.append(f"Bedrooms: {entities['bedrooms']}")
        if entities.get("size"):
            notes.append(f"Size: {entities['size']} sq ft")

        return " | ".join(notes)

    def _parse_budget(self, budget_str: Optional[str]) -> Optional[float]:
        """
        Parse budget string to numeric value.
        Examples: "50 lakhs" -> 5000000, "1 crore" -> 10000000, "5000000" -> 5000000
        """
        if not budget_str:
            return None

        try:
            budget_str = budget_str.lower().strip()

            # Handle crore
            if "crore" in budget_str or "cr" in budget_str:
                number = float(''.join(filter(str.isdigit, budget_str.split("crore")[0].split("cr")[0])))
                return number * 10000000

            # Handle lakhs
            if "lakh" in budget_str or "lac" in budget_str or "l" == budget_str[-1]:
                number = float(''.join(filter(str.isdigit, budget_str.split("lakh")[0].split("lac")[0].replace("l", ""))))
                return number * 100000

            # Handle thousand
            if "thousand" in budget_str or "k" in budget_str:
                number = float(''.join(filter(str.isdigit, budget_str.split("thousand")[0].split("k")[0])))
                return number * 1000

            # Handle plain number
            number = float(''.join(filter(str.isdigit, budget_str)))
            return number if number > 0 else None

        except (ValueError, IndexError, AttributeError):
            logger.warning(f"Could not parse budget: {budget_str}")
            return None

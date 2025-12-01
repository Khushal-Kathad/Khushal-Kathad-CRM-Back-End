# services/groq_client.py

import os
from groq import Groq
from typing import List, Dict, Optional
import json

class GroqClient:
    """
    Handles all interactions with Groq API for intent detection and response generation.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.client = Groq(api_key=self.api_key)

    def detect_intent(self, message: str, context: List[Dict] = None) -> Dict:
        """
        Detect user intent from message using Groq SLM.

        Returns:
        {
            "intent": "lead_creation" | "information_query" | "followup_schedule" | "site_info" | "general",
            "confidence": 0.95,
            "entities": {
                "name": "John Doe",
                "phone": "+919876543210",
                "budget": "50 lakhs",
                "property_type": "2BHK",
                "location": "Bangalore"
            }
        }
        """

        system_prompt = """You are an intent classifier for a real estate CRM chatbot.

Classify the user's message into ONE of these intents:

1. **brochure_query** - User asks questions about property details, pricing, amenities, size, location, features
   Examples: "What's the price?", "Tell me about amenities", "How big is 2BHK?", "Where is it located?", "What is Cilantra?", "Tell me about the property"

2. **visit_request** - User wants to schedule a site visit, property tour, or wants to see the property
   Examples: "I want to visit", "Can I see the property?", "Schedule a visit", "Book a tour", "I want to come see it"

3. **lead_creation** - User explicitly shows buying interest or investment intent (NOT just visiting)
   Examples: "I want to buy", "I'm interested in purchasing", "I want to invest", "Book an apartment"

4. **followup_schedule** - User wants a callback or phone meeting
   Examples: "Call me back", "Contact me later", "Have someone call me"

5. **site_info** - User asks about specific location details or area information
   Examples: "What's near the property?", "How is the location?", "Transportation nearby?"

6. **general** - Greetings, thanks, unclear messages
   Examples: "Hi", "Hello", "Thank you", "Bye", "Ok"

IMPORTANT DISTINCTIONS:
- Questions about property → brochure_query
- "I want to visit" → visit_request (NOT lead_creation)
- "I want to buy" → lead_creation
- Most property information questions → brochure_query

Extract relevant entities:
- name (person's name)
- phone (phone number)
- budget (budget amount)
- property_type (2BHK, 3BHK, villa, etc.)
- location (area, city)
- site_name (specific project/site name)
- preferred_time (for callbacks)
- preferred_date (for site visits - today, tomorrow, weekend, etc.)
- bedrooms (number of bedrooms)
- size (property size in sq ft)
- buying_intent (1-10 scale if mentioned)

Return ONLY a JSON object with this structure:
{
    "intent": "intent_name",
    "confidence": 0.0-1.0,
    "entities": {}
}"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation context if available
        if context:
            for ctx in context[-5:]:  # Last 5 messages
                messages.append({"role": "user", "content": ctx.get("user_message", "")})
                messages.append({"role": "assistant", "content": ctx.get("bot_response", "")})

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error in intent detection: {e}")
            return {
                "intent": "general",
                "confidence": 0.0,
                "entities": {}
            }

    def generate_response(
        self,
        intent: str,
        entities: Dict,
        context: List[Dict],
        crm_data: Optional[Dict] = None
    ) -> str:
        """
        Generate contextual response using Groq SLM.

        Args:
            intent: Detected intent
            entities: Extracted entities
            context: Conversation history
            crm_data: Data from CRM (leads, sites, etc.)
        """

        system_prompt = f"""You are a friendly real estate assistant helping customers.

Current Intent: {intent}
Extracted Information: {json.dumps(entities, indent=2)}

Guidelines:
- Be conversational and helpful
- Keep responses under 160 characters when possible (WhatsApp best practice)
- If user is a new lead, ask for their name and contact details politely
- For property inquiries, provide brief details and offer to connect with sales team
- For scheduling, confirm the details and mention someone will reach out
- Always be professional but warm

CRM Data Available: {json.dumps(crm_data, indent=2) if crm_data else "None"}

Generate a helpful response."""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add recent context
        if context:
            for ctx in context[-3:]:
                messages.append({"role": "user", "content": ctx.get("user_message", "")})
                messages.append({"role": "assistant", "content": ctx.get("bot_response", "")})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Moderate temperature for natural responses
                max_tokens=200
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error in response generation: {e}")
            return "I'm having trouble processing your request. Let me connect you with our team."

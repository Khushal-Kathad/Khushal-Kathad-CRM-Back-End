"""
Helper Functions for Lead Intelligence System
==============================================

Utility functions for:
- Follow-up status calculations
- JSON parsing
- Date handling
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import FollowUps
import json


def get_follow_up_status(lead_id: int, db: Session) -> dict:
    """
    Get next follow-up status for a lead

    Used by the scheduler to calculate follow-up status when updating lead scores.

    Returns:
        dict with next_date, status, overdue_days

    Example:
        {
            "next_date": "2025-10-15T10:00:00",
            "status": "today",
            "overdue_days": 0
        }
    """
    next_followup = db.query(FollowUps).filter(
        FollowUps.LeadId == lead_id,
        FollowUps.Status != 'Completed'
    ).order_by(FollowUps.NextFollowUpDate.asc()).first()

    if not next_followup or not next_followup.NextFollowUpDate:
        return {
            "next_date": None,
            "status": "none",
            "overdue_days": 0
        }

    next_date = next_followup.NextFollowUpDate
    now = datetime.now()

    if next_date < now:
        status = "overdue"
        overdue_days = (now - next_date).days
    elif next_date.date() == now.date():
        status = "today"
        overdue_days = 0
    elif next_date.date() <= (now + timedelta(days=7)).date():
        status = "this_week"
        overdue_days = 0
    else:
        status = "scheduled"
        overdue_days = 0

    return {
        "next_date": next_date.isoformat() if next_date else None,
        "status": status,
        "overdue_days": overdue_days
    }


def parse_recommendation_json(recommendation_json: str) -> dict:
    """
    Parse RecommendationJson from lead table

    Helper function to safely parse the JSON recommendation stored in the lead table.
    Used by API endpoints when returning lead data.

    Args:
        recommendation_json: JSON string from Lead.RecommendationJson column

    Returns:
        dict with recommendation structure, or default if parsing fails

    Example:
        {
            "priority": "urgent",
            "action": "call_now",
            "message": "Call immediately! Lead health critical",
            "reasoning": "High churn risk - immediate action required"
        }
    """
    if not recommendation_json:
        return {
            "priority": "low",
            "message": "No specific recommendation",
            "action": "monitor",
            "reasoning": "Standard follow-up process"
        }

    try:
        return json.loads(recommendation_json)
    except (json.JSONDecodeError, TypeError):
        # Return default if parsing fails
        return {
            "priority": "low",
            "message": "No specific recommendation",
            "action": "monitor",
            "reasoning": "Standard follow-up process"
        }


def generate_recommendation(lead_id: int, health_score: int, velocity_score: int,
                          buying_intent: int, overdue_days: int,
                          days_since_contact: int) -> dict:
    """
    Generate AI recommendation based on lead metrics

    This function analyzes all scores and returns the most urgent recommendation.

    Priority order:
    1. URGENT: Critical health + overdue
    2. HIGH: High intent + going cold
    3. MEDIUM: Improving lead
    4. LOW: Stable lead

    Args:
        lead_id: Lead ID
        health_score: 0-100
        velocity_score: 0-100
        buying_intent: 1-10
        overdue_days: integer
        days_since_contact: integer

    Returns:
        dict with priority, action, message, reasoning
    """
    # URGENT: Critical health + overdue
    if health_score < 40 and overdue_days > 3:
        return {
            "priority": "urgent",
            "action": "call_now",
            "message": f"🔴 URGENT: Call immediately! Lead health critical ({health_score}) and {overdue_days} days overdue.",
            "reasoning": "High churn risk - immediate action required"
        }

    # HIGH: High intent going cold
    if buying_intent >= 8 and days_since_contact > 5:
        return {
            "priority": "high",
            "action": "follow_up",
            "message": f"🟠 HIGH PRIORITY: Hot lead (intent {buying_intent}/10) going cold. Contact within 24 hours.",
            "reasoning": "High buying intent with declining engagement"
        }

    # MEDIUM: Good momentum
    if velocity_score > 70:
        return {
            "priority": "medium",
            "action": "nurture",
            "message": "🟢 Good momentum! Lead improving. Continue current approach.",
            "reasoning": "Positive trend - maintain engagement"
        }

    # LOW: Standard process
    return {
        "priority": "low",
        "action": "monitor",
        "message": "Monitor and follow standard process.",
        "reasoning": "No urgent action needed"
    }


# NOTE: No caching logic needed!
# Scores are already in the lead table, updated by the scheduler every 30 minutes.
# API endpoints simply read the pre-calculated values from the lead table columns:
#   - Lead.HealthScore
#   - Lead.VelocityScore
#   - Lead.AIPriority
#   - Lead.ConversionProbability
#   - Lead.ChurnRisk
#   - Lead.FollowUpStatus
#   - Lead.OverdueDays
#   - Lead.RecommendationJson
#   - Lead.ScoresLastUpdated

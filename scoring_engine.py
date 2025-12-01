"""
Lead Scoring Engine
===================

This module contains all scoring calculation functions for lead intelligence.

Functions are used by:
1. Scheduler (scheduler/score_updater.py) for bulk calculations
2. Manual recalculation endpoint for single leads
3. Testing and debugging

All calculations use simple, rule-based logic (no ML).
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import Lead, FollowUps, Visit, Visitors, LeadVelocitySnapshots


# ============================================================
# FUNCTION 1: Health Score (0-100)
# ============================================================

def calculate_lead_health_score(lead_id: int, db: Session) -> int:
    """
    Calculate health score (0-100)

    Formula:
    - Start with 100 points
    - Deduct for inactive (40 points max)
    - Deduct for overdue (30 points max)
    - Add/subtract for buying intent (±20 points)
    - Add for response rate (10 points max)

    Example:
    - Lead contacted 2 days ago: -0 points
    - No overdue follow-ups: -0 points
    - Buying intent 8/10: +12 points
    - Response rate 80%: +8 points
    → Final: 100 - 0 - 0 + 12 + 8 = 120, clamped to 100
    """
    lead = db.query(Lead).filter(Lead.LeadId == lead_id).first()
    if not lead:
        return 0

    score = 100

    # Factor 1: Last contact (40 points)
    last_contact = get_last_contact_date(lead_id, db)
    if last_contact:
        days_inactive = (datetime.now() - last_contact).days
        if days_inactive <= 3:
            score -= 0
        elif days_inactive <= 7:
            score -= 10
        elif days_inactive <= 14:
            score -= 20
        elif days_inactive <= 30:
            score -= 30
        else:
            score -= 40
    else:
        score -= 40  # Never contacted

    # Factor 2: Overdue follow-ups (30 points)
    overdue_count = db.query(FollowUps).filter(
        FollowUps.LeadId == lead_id,
        FollowUps.Status != 'Completed',
        FollowUps.NextFollowUpDate < datetime.now()
    ).count()
    score -= min(overdue_count * 10, 30)

    # Factor 3: Buying intent (±20 points)
    if lead.BuyingIntent:
        score += (lead.BuyingIntent - 5) * 4

    # Factor 4: Response rate (10 points)
    response_rate = calculate_response_rate(lead_id, db)
    score += (response_rate / 10)

    return max(0, min(100, int(score)))


# ============================================================
# FUNCTION 2: AI Priority Score (0-100)
# ============================================================

def calculate_ai_priority(lead_id: int, db: Session) -> int:
    """
    Calculate AI priority for sorting (0-100, higher = more urgent)

    Formula:
    - Inverse health (30%)
    - Buying intent (40%)
    - Overdue days (30%)

    Example:
    - Health 30 → (100-30) × 0.30 = 21 points
    - Intent 9 → 90 × 0.40 = 36 points
    - 5 days overdue → min(25, 50) × 0.30 = 7.5 points
    → Total: 64.5 (HIGH PRIORITY)
    """
    lead = db.query(Lead).filter(Lead.LeadId == lead_id).first()
    if not lead:
        return 0

    health_score = calculate_lead_health_score(lead_id, db)
    buying_intent = lead.BuyingIntent or 5
    overdue_days = get_overdue_days(lead_id, db)

    priority = (
        (100 - health_score) * 0.30 +     # Lower health = higher priority
        (buying_intent * 10) * 0.40 +      # Scale 0-10 to 0-100, 40% weight
        min(overdue_days * 5, 50) * 0.30   # Overdue urgency, capped at 50
    )

    return int(max(0, min(100, priority)))


# ============================================================
# FUNCTION 3: Velocity Score (0-100)
# ============================================================

def calculate_velocity_score(lead_id: int, db: Session) -> int:
    """
    Calculate velocity score (0-100) based on health trend over time

    Formula:
    - Compare current health to 7-day and 14-day snapshots
    - Positive trend = higher velocity
    - Negative trend = lower velocity
    - Rapid improvement = bonus points

    Returns 50 (neutral) if not enough history available.
    """
    current_health = calculate_lead_health_score(lead_id, db)

    # Get snapshots from 7 and 14 days ago
    now = datetime.now()
    snapshot_7d = db.query(LeadVelocitySnapshots).filter(
        LeadVelocitySnapshots.LeadId == lead_id,
        LeadVelocitySnapshots.SnapshotDate >= now - timedelta(days=8),
        LeadVelocitySnapshots.SnapshotDate <= now - timedelta(days=6)
    ).first()

    snapshot_14d = db.query(LeadVelocitySnapshots).filter(
        LeadVelocitySnapshots.LeadId == lead_id,
        LeadVelocitySnapshots.SnapshotDate >= now - timedelta(days=15),
        LeadVelocitySnapshots.SnapshotDate <= now - timedelta(days=13)
    ).first()

    if not snapshot_7d or not snapshot_14d:
        # Not enough history, return neutral score
        return 50

    # Calculate 7-day trend
    trend_7d = current_health - snapshot_7d.HealthScore

    # Calculate 14-day trend
    trend_14d = current_health - snapshot_14d.HealthScore

    # Calculate acceleration (is trend improving?)
    acceleration = trend_7d - (snapshot_7d.HealthScore - snapshot_14d.HealthScore)

    # Base score on 7-day trend
    velocity = 50  # Neutral baseline

    # Add/subtract based on 7-day trend (±30 points)
    velocity += (trend_7d / 100) * 30

    # Add/subtract based on 14-day trend (±20 points)
    velocity += (trend_14d / 100) * 20

    # Bonus for acceleration (±20 points)
    velocity += (acceleration / 50) * 20

    # Consider interaction frequency (±10 points)
    if snapshot_7d.FollowUpCount and snapshot_14d.FollowUpCount:
        interaction_trend = snapshot_7d.FollowUpCount - snapshot_14d.FollowUpCount
        velocity += min(interaction_trend * 2, 10)

    return max(0, min(100, int(velocity)))


# ============================================================
# FUNCTION 4: Churn Risk (low/medium/high/critical)
# ============================================================

def calculate_churn_risk(lead_id: int, db: Session) -> str:
    """
    Calculate churn risk level: low, medium, high, critical

    Based on:
    - Health score decline (40 points)
    - Negative velocity (30 points)
    - Days without contact (20 points)
    - Overdue follow-ups (10 points)

    Example:
    - Health 25 → 40 points
    - Velocity 20 → 30 points
    - No contact 20 days → 20 points
    - 7 days overdue → 10 points
    → Total: 100 = CRITICAL
    """
    health_score = calculate_lead_health_score(lead_id, db)
    velocity = calculate_velocity_score(lead_id, db)
    overdue_days = get_overdue_days(lead_id, db)
    last_contact = get_last_contact_date(lead_id, db)

    risk_score = 0

    # Factor 1: Low health (40 points)
    if health_score < 30:
        risk_score += 40
    elif health_score < 50:
        risk_score += 25
    elif health_score < 70:
        risk_score += 10

    # Factor 2: Negative velocity (30 points)
    if velocity < 30:
        risk_score += 30
    elif velocity < 40:
        risk_score += 20
    elif velocity < 50:
        risk_score += 10

    # Factor 3: No contact (20 points)
    if last_contact:
        days_inactive = (datetime.now() - last_contact).days
        if days_inactive > 14:
            risk_score += 20
        elif days_inactive > 7:
            risk_score += 15
        elif days_inactive > 3:
            risk_score += 5
    else:
        risk_score += 20

    # Factor 4: Overdue follow-ups (10 points)
    if overdue_days > 5:
        risk_score += 10
    elif overdue_days > 2:
        risk_score += 5

    # Map risk score to category
    if risk_score >= 70:
        return "critical"
    elif risk_score >= 50:
        return "high"
    elif risk_score >= 30:
        return "medium"
    else:
        return "low"


# ============================================================
# FUNCTION 5: Conversion Probability (0-100%)
# ============================================================

def calculate_conversion_probability(lead_id: int, db: Session) -> float:
    """
    Calculate probability of conversion (0-100%)

    Uses weighted regression model based on key factors:
    - Health score (30%)
    - Buying intent (25%)
    - Velocity (20%)
    - Site visits (15%)
    - Response rate (10%)

    Example:
    - Health 85 → 85 × 0.30 = 25.5
    - Intent 9 → 90 × 0.25 = 22.5
    - Velocity 75 → 75 × 0.20 = 15.0
    - 5 visits → 100 × 0.15 = 15.0
    - Response 90% → 90 × 0.10 = 9.0
    → Total: 87% chance of conversion
    """
    lead = db.query(Lead).filter(Lead.LeadId == lead_id).first()
    if not lead:
        return 0.0

    health_score = calculate_lead_health_score(lead_id, db)
    velocity = calculate_velocity_score(lead_id, db)
    buying_intent = lead.BuyingIntent or 5
    response_rate = calculate_response_rate(lead_id, db)

    # Count site visits
    visits = db.query(Visit).join(
        Visitors, Visit.VisitId == Visitors.VisitId
    ).filter(
        Visitors.LeadId == lead_id
    ).count()

    # Weighted calculation
    probability = (
        (health_score * 0.30) +                    # Health (30%)
        (buying_intent * 10 * 0.25) +              # Intent (25%)
        (velocity * 0.20) +                        # Velocity (20%)
        (min(visits * 20, 100) * 0.15) +           # Visits (15%, max 5 visits)
        (response_rate * 0.10)                     # Response (10%)
    )

    return round(min(100, max(0, probability)), 2)


# ============================================================
# HELPER FUNCTION: Response Rate (0-100%)
# ============================================================

def calculate_response_rate(lead_id: int, db: Session) -> float:
    """
    Calculate % of follow-ups where customer responded

    Example:
    - 10 completed follow-ups
    - 7 have notes (customer responded)
    → Response rate = 70%
    """
    total = db.query(FollowUps).filter(
        FollowUps.LeadId == lead_id,
        FollowUps.Status == 'Completed'
    ).count()

    if total == 0:
        return 0.0

    responded = db.query(FollowUps).filter(
        FollowUps.LeadId == lead_id,
        FollowUps.Status == 'Completed',
        FollowUps.Notes.isnot(None)
    ).count()

    return (responded / total) * 100


# ============================================================
# HELPER FUNCTION: Get Overdue Days
# ============================================================

def get_overdue_days(lead_id: int, db: Session) -> int:
    """
    Get days overdue for most overdue follow-up

    Example:
    - Today is Jan 10
    - Most overdue follow-up was due Jan 5
    → Overdue days = 5
    """
    overdue = db.query(FollowUps).filter(
        FollowUps.LeadId == lead_id,
        FollowUps.Status != 'Completed',
        FollowUps.NextFollowUpDate < datetime.now()
    ).order_by(FollowUps.NextFollowUpDate.asc()).first()

    if overdue:
        days = (datetime.now() - overdue.NextFollowUpDate).days
        return max(0, days)

    return 0


# ============================================================
# HELPER FUNCTION: Get Last Contact Date
# ============================================================

def get_last_contact_date(lead_id: int, db: Session):
    """
    Get most recent contact date from follow-ups or visits

    Example:
    - Last follow-up: Jan 5
    - Last website visit: Jan 8
    → Returns Jan 8 (most recent)
    """
    # Get last follow-up
    last_followup = db.query(FollowUps).filter(
        FollowUps.LeadId == lead_id,
        FollowUps.Status == 'Completed'
    ).order_by(FollowUps.FollowUpDate.desc()).first()

    # Get last visit
    last_visit = db.query(Visit).join(
        Visitors, Visit.VisitId == Visitors.VisitId
    ).filter(
        Visitors.LeadId == lead_id
    ).order_by(Visit.VisitDate.desc()).first()

    dates = []
    if last_followup and last_followup.FollowUpDate:
        dates.append(last_followup.FollowUpDate)
    if last_visit and last_visit.VisitDate:
        dates.append(last_visit.VisitDate)

    return max(dates) if dates else None

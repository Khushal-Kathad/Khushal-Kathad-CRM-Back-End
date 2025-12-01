"""
Scheduler Status and Management API
====================================

Endpoints to monitor and manage the background scheduler
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from scheduler.score_updater import get_scheduler_status, update_all_lead_scores
from datetime import datetime

router = APIRouter(
    prefix="/api/scheduler",
    tags=["Scheduler Management"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/status")
def check_scheduler_status():
    """
    Check the status of the background scheduler

    Returns:
        - running: Whether scheduler is active
        - state: Current scheduler state
        - jobs: List of scheduled jobs with next run times
    """
    try:
        status = get_scheduler_status()
        return {
            "data": status,
            "message": "Scheduler status retrieved successfully",
            "statusCode": 200
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking scheduler status: {str(e)}")


@router.post("/trigger-scoring")
def manually_trigger_scoring():
    """
    Manually trigger the lead scoring calculation immediately

    This will run the scoring engine outside the regular 30-minute schedule.
    Use this for testing or when you need immediate score updates.
    """
    try:
        start_time = datetime.now()
        update_all_lead_scores()
        elapsed = (datetime.now() - start_time).total_seconds()

        return {
            "data": {
                "triggered_at": start_time.isoformat(),
                "completed_at": datetime.now().isoformat(),
                "elapsed_seconds": round(elapsed, 2)
            },
            "message": f"Lead scoring completed successfully in {elapsed:.2f} seconds",
            "statusCode": 200
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering scoring: {str(e)}")


@router.get("/last-update")
def get_last_update_info(db: Session = Depends(get_db)):
    """
    Get information about the last scoring update

    Returns:
        - oldest_update: Oldest score update timestamp
        - latest_update: Most recent score update timestamp
        - total_scored: Number of leads with scores
        - age_minutes: Minutes since last update
    """
    from models import Lead
    from sqlalchemy import func

    try:
        stats = db.query(
            func.min(Lead.ScoresLastUpdated).label('oldest'),
            func.max(Lead.ScoresLastUpdated).label('latest'),
            func.count(Lead.LeadId).label('total')
        ).filter(
            Lead.ScoresLastUpdated.isnot(None)
        ).first()

        if not stats or not stats.latest:
            return {
                "data": {
                    "oldest_update": None,
                    "latest_update": None,
                    "total_scored": 0,
                    "age_minutes": None,
                    "status": "No scores have been calculated yet"
                },
                "message": "No scoring data available",
                "statusCode": 200
            }

        age_minutes = (datetime.now() - stats.latest).total_seconds() / 60 if stats.latest else None

        return {
            "data": {
                "oldest_update": stats.oldest.isoformat() if stats.oldest else None,
                "latest_update": stats.latest.isoformat() if stats.latest else None,
                "total_scored": stats.total,
                "age_minutes": round(age_minutes, 2) if age_minutes else None,
                "status": "Scores are up to date" if age_minutes and age_minutes < 31 else "Scores may be stale"
            },
            "message": "Last update info retrieved successfully",
            "statusCode": 200
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting last update info: {str(e)}")

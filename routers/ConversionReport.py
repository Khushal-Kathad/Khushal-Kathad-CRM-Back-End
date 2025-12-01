from string import ascii_uppercase
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException,status, Query
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
# from models import Lead, Contact, ProspectType, Site
from typing import Annotated, Optional,List
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import select, func, text, distinct, String, literal, Float, extract, and_, case, Numeric, \
    literal_column
from database import SessionLocal
from models import Visitors, Contact, Visit, Lead, Site
from .auth import get_current_user
from datetime import datetime, timedelta
from schemas.schemas import TargetsRequest
from sqlalchemy import cast, Date
from datetime import datetime, timedelta, date

from .infra_unit import get_time

router = APIRouter(
    prefix="/ConversionReport",
    tags = ['ConversionReport']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_date():
    ind_date = datetime.now(timezone("Asia/Kolkata")).date()
    return ind_date

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/monthly-leads")
def get_monthly_leads(user: user_dependency,db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    lead_created_by_id: Optional[int] = Query(None),
    broker_id: Optional[int] = Query(None)):

        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

            # Default to current month if dates are not provided
        today = get_date()
        if not start_date:
            start_date = today.replace(day=1)
        if not end_date:
            end_date = today

        query = db.query(func.count()).select_from(Lead).filter(
            Lead.CreatedDate != None,
            Lead.CreatedDate >= start_date,
            Lead.CreatedDate <= end_date )

        if site_id:
            query = query.filter(Lead.SiteId.in_(site_id))
        if lead_source:
            query = query.filter(Lead.LeadSource.in_(lead_source))
        if lead_created_by_id:
            query = query.filter(Lead.CreatedById == lead_created_by_id)
        if broker_id:
            query = query.filter(Lead.BrokerId == broker_id)

        total_count = query.scalar()

        return {"TotalLeads": total_count}




@router.get("/monthly-Win-leads")
def get_monthly_Win_leads(user: user_dependency,db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    lead_created_by_id: Optional[int] = Query(None),
    broker_id: Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()
    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    # Query to count "Win" leads with all filters
    query = db.query(func.count()).select_from(Lead).filter(
        Lead.LeadStatus == "Win",
        Lead.CreatedDate != None,
        Lead.CreatedDate >= start_date,
        Lead.CreatedDate <= end_date
    )

    if site_id:
        query = query.filter(Lead.SiteId.in_(site_id))
    if lead_source:
        query = query.filter(Lead.LeadSource.in_(lead_source))
    if lead_created_by_id:
        query = query.filter(Lead.LeadCreatedById == lead_created_by_id)
    if broker_id:
        query = query.filter(Lead.BrokerId == broker_id)

    total_won_leads = query.scalar()

    return {"TotalWonLeads": total_won_leads}



@router.get("/Conversion-Rate-Social-Media")
def get_conversion_Rate_social_media(user: user_dependency,db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    lead_created_by_id: Optional[int] = Query(None),
    broker_id: Optional[int] = Query(None)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    query = db.query(Lead)

    # Apply filters
    if start_date:
        query = query.filter(Lead.CreatedDate >= start_date)
    if end_date:
        query = query.filter(Lead.CreatedDate <= end_date)
    if site_id:
        query = query.filter(Lead.SiteId.in_(site_id))
    if lead_source:
        query = query.filter(Lead.LeadSource.in_(lead_source))
    if lead_created_by_id:
        query = query.filter(Lead.CreatedById == lead_created_by_id)
    if broker_id:
        query = query.filter(Lead.BrokerId == broker_id)

    # Clone query for total and social media
    total_leads = query.count()
    social_media_leads = query.filter(Lead.LeadSource == "Social Media").count()

    # Conversion Rate Calculation
    conversion_rate = (social_media_leads / total_leads * 100) if total_leads > 0 else 0

    return {
        "TotalLeads": total_leads,
        "TotalSocialMediaLeads": social_media_leads,
        "ConversionRate": round(conversion_rate, 2)
    }


@router.get("/broker-conversion-rate")
def get_broker_conversion_rate(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    lead_created_by_id: Optional[int] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Base query: only leads with brokers
    base_query = db.query(Lead).filter(Lead.BrokerId.isnot(None))

    # Apply filters
    if start_date:
        base_query = base_query.filter(Lead.CreatedDate >= start_date)
    if end_date:
        base_query = base_query.filter(Lead.CreatedDate <= end_date)
    if site_id:
        base_query = base_query.filter(Lead.SiteId.in_(site_id))
    if lead_source:
        base_query = base_query.filter(Lead.LeadSource.in_(lead_source))
    if lead_created_by_id:
        base_query = base_query.filter(Lead.CreatedById == lead_created_by_id)
    if broker_id:
        base_query = base_query.filter(Lead.BrokerId == broker_id)

    # Total broker leads after filtering
    total_broker_leads = base_query.count()

    # Broker wins after filtering
    broker_win_leads = base_query.filter(Lead.LeadStatus == "Win").count()

    # Conversion rate calculation
    conversion_rate = (broker_win_leads / total_broker_leads * 100) if total_broker_leads > 0 else 0

    return {
        "TotalBrokerLeads": total_broker_leads,
        "BrokerWins": broker_win_leads,
        "BrokerConversionRate": round(conversion_rate, 2)
    }


@router.get('/conversion_rate')
async def conversion_rate(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    lead_created_by_id: Optional[int] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    filter_conditions = []

    # Optional CreatedBy filter (only if passed)
    if lead_created_by_id is not None:
        filter_conditions.append(Lead.CreatedById == lead_created_by_id)

    if site_id:
        filter_conditions.append(Lead.SiteId.in_(site_id))
    if lead_source:
        filter_conditions.append(Lead.LeadSource.in_(lead_source))
    if broker_id:
        filter_conditions.append(Lead.BrokerId == broker_id)
    if start_date:
        filter_conditions.append(Lead.CreatedDate >= start_date)
    if end_date:
        filter_conditions.append(Lead.CreatedDate <= end_date)

    total_leads = db.query(Lead).filter(*filter_conditions).count()
    win_leads = db.query(Lead).filter(*filter_conditions, Lead.LeadStatus == 'Win').count()

    win_percentage = (win_leads / total_leads) * 100 if total_leads > 0 else 0.0

    return {
        'conversion_rate': round(win_percentage, 2),
        'total_leads': total_leads,
        'win_leads': win_leads
    }


@router.get("/sales-funnel")
def get_sales_funnel(user: user_dependency, db: db_dependency,
                     start_date: Optional[date] = Query(None),
                     end_date: Optional[date] = Query(None),
                     site_id: Optional[List[int]] = Query(None),
                     lead_source: Optional[List[str]] = Query(None),
                     lead_created_by_id: Optional[int] = Query(None),
                     broker_id: Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    lead_query = db.query(Lead)

    if start_date:
        lead_query = lead_query.filter(Lead.CreatedDate >= start_date)
    if end_date:
        lead_query = lead_query.filter(Lead.CreatedDate <= end_date)
    if site_id:
        lead_query = lead_query.filter(Lead.SiteId.in_(site_id))
    if lead_source:
        lead_query = lead_query.filter(Lead.LeadSource.in_(lead_source))
    if lead_created_by_id:
        lead_query = lead_query.filter(Lead.CreatedById == lead_created_by_id)
    if broker_id:
        lead_query = lead_query.filter(Lead.BrokerId == broker_id)

    # Total Leads
    total_leads = lead_query.count()

    # Qualified Leads (BuyingIntent >= 3)
    qualified_leads = lead_query.filter(Lead.BuyingIntent >= 3).count()

    # Bookings (LeadStatus = 'Win')
    bookings = lead_query.filter(Lead.LeadStatus == 'Win').count()

    # Site Visits: Filter using Visitors table but apply lead filters on joined Lead
    visitors_query = db.query(Visitors).join(Lead, Visitors.LeadId == Lead.LeadId)

    if start_date:
        visitors_query = visitors_query.filter(Lead.CreatedDate >= start_date)
    if end_date:
        visitors_query = visitors_query.filter(Lead.CreatedDate <= end_date)
    if site_id:
        visitors_query = visitors_query.filter(Lead.SiteId.in_(site_id))
    if lead_source:
        visitors_query = visitors_query.filter(Lead.LeadSource.in_(lead_source))
    if lead_created_by_id:
        visitors_query = visitors_query.filter(Lead.CreatedById == lead_created_by_id)
    if broker_id:
        visitors_query = visitors_query.filter(Lead.BrokerId == broker_id)

    site_visits = visitors_query.with_entities(func.count(func.distinct(Visitors.LeadId))).scalar()

    return {
        "TotalLeads": total_leads,
        "QualifiedLeads": qualified_leads,
        "SiteVisits": site_visits,
        "Bookings": bookings
    }



@router.get("/weekly-lead-Overview")
def get_weekly_lead_Overview(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    broker_id: Optional[int] = Query(default=None),
    created_by_id: Optional[int] = Query(default=None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()
    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    filters = [
        Lead.CreatedDate.isnot(None),
        Lead.CreatedDate >= start_date,
        Lead.CreatedDate <= end_date
    ]

    if site_id:
        filters.append(Lead.SiteId.in_(site_id))
    if lead_source:
        filters.append(Lead.LeadSource.in_(lead_source))
    if broker_id:
        filters.append(Lead.BrokerId == broker_id)
    if created_by_id:
        filters.append(Lead.CreatedById == created_by_id)

    # Group only by LeadSource
    query = db.query(
        Lead.LeadSource,
        func.count().label("TotalLeads")
    ).filter(*filters).group_by(
        Lead.LeadSource
    ).order_by(
        Lead.LeadSource
    )

    results = query.all()

    return [
        {
            "LeadSource": row.LeadSource,
            "TotalLeads": row.TotalLeads
        }
        for row in results
    ]




@router.get("/direct-visit-conversion-rate")
def get_direct_visit_conversion_rate(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    broker_id: Optional[int] = Query(None),
    created_by_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Default date range
    today = get_date()
    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    # Base query for total direct visits
    total_query = db.query(func.count(Visitors.VisitorsId)) \
        .join(Contact, Visitors.ContactId == Contact.ContactId) \
        .join(Visit, Visitors.VisitId == Visit.VisitId) \
        .filter(
            Visitors.VisitId != None,
            Contact.ContactType == "Customer",
            Visit.VisitDate >= start_date,
            Visit.VisitDate <= end_date
        )

    # Base query for converted (win) direct visits
    converted_query = db.query(func.count(Visitors.VisitorsId)) \
        .join(Contact, Visitors.ContactId == Contact.ContactId) \
        .join(Lead, Visitors.LeadId == Lead.LeadId) \
        .join(Visit, Visitors.VisitId == Visit.VisitId) \
        .filter(
            Visitors.VisitId != None,
            Contact.ContactType == "Customer",
            Lead.LeadStatus == "Win",
            Visit.VisitDate >= start_date,
            Visit.VisitDate <= end_date
        )

    # Apply additional filters
    if site_id:
        total_query = total_query.filter(Visit.SiteId.in_(site_id))
        converted_query = converted_query.filter(Visit.SiteId.in_(site_id))
    if lead_source:
        converted_query = converted_query.filter(Lead.LeadSource.in_(lead_source))
    if broker_id:
        converted_query = converted_query.filter(Lead.BrokerId == broker_id)
    if created_by_id:
        converted_query = converted_query.filter(Lead.CreatedById == created_by_id)

    total = total_query.scalar() or 0
    converted = converted_query.scalar() or 0

    conversion_rate = (converted / total * 100) if total > 0 else 0.0

    return {
        "TotalDirectVisits": total,
        "ConvertedDirectVisits": converted,
        "ConversionRate": round(conversion_rate, 2)
    }



@router.get("/site-Wise-conversion-rate")
def get_site_Wise_conversion_rate(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    broker_id: Optional[int] = Query(None),
    created_by_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()
    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    # Base filters
    visit_filters = [
        Visit.VisitDate >= start_date,
        Visit.VisitDate <= end_date
    ]
    lead_filters = [
        Lead.CreatedDate >= start_date,
        Lead.CreatedDate <= end_date,
        Lead.LeadStatus == "Win"
    ]

    # Optional filters
    if site_id:
        visit_filters.append(Visit.SiteId.in_(site_id))
        lead_filters.append(Lead.SiteId.in_(site_id))
    if broker_id:
        lead_filters.append(Lead.BrokerId == broker_id)
    if lead_source:
        lead_filters.append(Lead.LeadSource.in_(lead_source))
    if created_by_id:
        lead_filters.append(Lead.CreatedById == created_by_id)

    # 1. Visit counts grouped by site
    visit_data = db.query(
        Site.SiteId,
        Site.SiteName,
        func.count(Visit.VisitId).label("visits")
    ).join(Visit, Visit.SiteId == Site.SiteId)\
     .filter(and_(*visit_filters))\
     .group_by(Site.SiteId, Site.SiteName)\
     .all()

    # 2. Booking (lead) counts grouped by site
    booking_data = db.query(
        Site.SiteId,
        func.count(Lead.LeadId).label("bookings")
    ).join(Lead, Lead.SiteId == Site.SiteId)\
     .filter(and_(*lead_filters))\
     .group_by(Site.SiteId)\
     .all()

    booking_dict = {b.SiteId: b.bookings for b in booking_data}

    # 3. Final response
    result = []
    for item in visit_data:
        bookings = booking_dict.get(item.SiteId, 0)
        conversion = round((bookings / item.visits) * 100) if item.visits > 0 else 0
        result.append({
            "Site Name": item.SiteName,
            "Visits": item.visits,
            "Bookings": bookings,
            "Conversion": f"{conversion}%"
        })

    return result



@router.get("/Conversion-Trends-Quarterly")
def get_conversion_trends_quarterly(
    user: user_dependency,
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    lead_source: Optional[List[str]] = Query(None),
    broker_id: Optional[int] = Query(None),
    created_by_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = date.today()

    # Default: Last 4 quarters (1 year)
    if not start_date or not end_date:
        end_date = today
        start_date = end_date - timedelta(days=365) + timedelta(days=1)

    # Year and quarter expressions (SQL Server compatible)
    year_expr = literal_column("DATEPART(year, lead.CreatedDate)").label("year")
    quarter_expr = literal_column("(DATEPART(month, lead.CreatedDate) - 1) / 3 + 1").label("quarter")

    # Query with filters
    query = db.query(
        year_expr,
        quarter_expr,
        func.count().label("total_leads"),
        func.sum(case((Lead.LeadStatus == 'Win', 1), else_=0)).label("win_leads")
    ).filter(
        Lead.CreatedDate >= start_date,
        Lead.CreatedDate <= end_date
    )

    if site_id:
        query = query.filter(Lead.SiteId.in_(site_id))
    if lead_source:
        query = query.filter(Lead.LeadSource.in_(lead_source))
    if broker_id:
        query = query.filter(Lead.BrokerId == broker_id)
    if created_by_id:
        query = query.filter(Lead.CreatedById == created_by_id)

    query = query.group_by(year_expr, quarter_expr).order_by(year_expr, quarter_expr)

    results = query.all()

    # Format result
    response = []
    for row in results:
        year = int(row.year)
        quarter = int(row.quarter)
        total = row.total_leads or 0
        win = row.win_leads or 0
        conversion_rate = round((win / total) * 100, 2) if total > 0 else 0.0

        response.append({
            "quarter": f"Q{quarter}-{year}",
            "total_leads": total,
            "win_leads": win,
            "conversion_rate": conversion_rate
        })

    return {"data": response}




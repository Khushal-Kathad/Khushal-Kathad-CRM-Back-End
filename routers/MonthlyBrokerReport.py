from string import ascii_uppercase

from dateutil.relativedelta import relativedelta
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException,status, Query
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from typing import Annotated, Optional, List
from sqlalchemy.orm import Session, joinedload, load_only, aliased
from sqlalchemy import select, func, text, distinct, and_, case, tuple_, String, literal, Float, literal_column
from database import SessionLocal
from models import  Visitors, Contact, Visit, Users,Lead, Site
from .auth import get_current_user
from datetime import datetime, timedelta
from schemas.schemas import TargetsRequest
from sqlalchemy import cast, Date
from datetime import datetime, timedelta, date

from .infra_unit import get_time

router = APIRouter(
    prefix="/MonthlyBrokerReport",
    tags = ['MonthlyBrokerReport']
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


@router.get("/Total-Broker-Leads")
async def total_broker_leads(user: user_dependency,db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    Broker_id: Optional[int] = Query(None)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        today = get_date()

        # If no dates provided, default to current month
        if not start_date:
            start_date = today.replace(day=1)
        if not end_date:
            end_date = today

        query = db.query(
            func.count().label("TotalBrokerLeads")
        ).filter(
            Lead.BrokerId.isnot(None),
            Lead.CreatedDate >= start_date,
            Lead.CreatedDate <= end_date
        )

        if site_id:
            query = query.filter(Lead.SiteId.in_(site_id))
        if Broker_id:
            query = query.filter(Lead.BrokerId == Broker_id)

        total = query.scalar()

        return {
            "start_date": start_date,
            "end_date": end_date,
            "TotalBrokerLeads": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/Broker-Site-Visits", status_code=status.HTTP_200_OK)
async def broker_site_visits(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        today = get_date()

        # Default to current month start to today if no dates provided
        if not start_date:
            start_date = today.replace(day=1)
        if not end_date:
            end_date = today

        # Build the query directly with inline distinct count
        # query = db.query(
        #     func.count(
        #         func.distinct(
        #             func.concat(
        #                 cast(Contact.ContactId, String),
        #                 '-',
        #                 cast(Visit.SiteId, String)
        #             )
        #         )
        #     ).label("TotalBrokerSiteVisits")
        # ).select_from(Visit).join(
        #     Visitors, Visit.VisitId == Visitors.VisitId
        # ).join(
        #     Contact, Visitors.ContactId == Contact.ContactId
        # ).filter(
        #     Contact.ContactType == 'Broker',
        #     Visit.VisitDate >= start_date,
        #     Visit.VisitDate <= end_date
        # )
        query = db.query(
            func.count(func.distinct(Visit.VisitId)).label("TotalBrokerSiteVisits")
        ).select_from(Visit).join(
            Visitors, Visit.VisitId == Visitors.VisitId
        ).join(
            Contact, Visitors.ContactId == Contact.ContactId
        ).filter(
            Contact.ContactType == 'Broker',
            Visit.VisitDate >= start_date,
            Visit.VisitDate <= end_date
        )
        if site_id:
            query = query.filter(Visit.SiteId.in_(site_id))
        if broker_id:
            query = query.filter(Contact.ContactId == broker_id)

        result = query.scalar() or 0

        return {
            "start_date": start_date,
            "end_date": end_date,
            "TotalBrokerSiteVisits": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
@router.get("/New-Broker", status_code=status.HTTP_200_OK)
async def new_broker(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        today = get_date()

        # Default date range: start of current month to today
        if not start_date:
            start_date = today.replace(day=1)
        if not end_date:
            end_date = today

        query = db.query(
            func.count().label('TotalNewBrokers')
        ).filter(
            Contact.ContactType == 'Broker',
            Contact.CreatedDate >= start_date,
            Contact.CreatedDate <= end_date
        )

        if site_id:
            query = query.filter(Contact.SiteId.in_(site_id))
        if broker_id:
            query = query.filter(Contact.ContactId == broker_id)

        result = query.scalar() or 0

        return {
            "start_date": start_date,
            "end_date": end_date,
            "TotalNewBrokers": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/Top-Performig-Brokers")
async def Top_Performing_Brokers(user: user_dependency,db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    today = get_date()

    if not start_date:
        # start_date = today - timedelta(days=180)
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today
    try:
        # Broker Full Name
        broker_name = (Contact.ContactFName + ' ' + func.coalesce(Contact.ContactLName, '')).label('BrokerName')

        # Total Leads
        total_leads = func.count(distinct(Lead.LeadId)).label('TotalLeads')

        # Total Wins
        wins = func.count(distinct(
            case((Lead.LeadStatus == 'Win', Lead.LeadId))
        )).label('Wins')

        # Total Losts
        losts = func.count(distinct(
            case((Lead.LeadStatus == 'Lost', Lead.LeadId))
        )).label('Losts')

        # Total Site Visits
        site_visits = func.count(distinct(Visit.VisitId)).label('SiteVisits')

        # Conversion Rate Calculation
        conversion_rate = (
            cast(
                (100.0 * func.count(distinct(
                    case((Lead.LeadStatus == 'Win', Lead.LeadId))
                )) / func.nullif(func.count(distinct(Lead.LeadId)), 0)),
                Float
            )
        ).label('ConversionRate')

        # Build Query
        query = db.query(
            broker_name,
            total_leads,
            wins,
            losts,
            site_visits,
            conversion_rate
        ).select_from(Contact).outerjoin(
            Lead, Contact.ContactId == Lead.BrokerId
        ).outerjoin(
            Visitors, Lead.LeadId == Visitors.LeadId
        ).outerjoin(
            Visit, Visitors.VisitId == Visit.VisitId
        ).filter(
            Contact.ContactType == 'Broker'
        )

        # Apply Date Filters on Lead CreatedDate
        if start_date:
            query = query.filter(Lead.CreatedDate >= start_date)
        if end_date:
            query = query.filter(Lead.CreatedDate <= end_date)

        if site_id:
            query = query.filter(Visit.SiteId.in_(site_id))
        if broker_id:
            query = query.filter(Contact.ContactId == broker_id)

        query = query.group_by(Contact.ContactFName, Contact.ContactLName).order_by(conversion_rate.desc()).limit(5)

        results = query.all()

        response = []
        for broker in results:
            response.append({
                "BrokerName": broker.BrokerName,
                "TotalLeads": broker.TotalLeads,
                "Wins": broker.Wins,
                "Losts": broker.Losts,
                "SiteVisits": broker.SiteVisits,
                "ConversionRate": round(broker.ConversionRate or 0, 2)
            })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/Broker-Lead-Count", status_code=status.HTTP_200_OK)
async def broker_lead_count(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    try:
        today = get_date()

        # Default to last 6 months if no dates are provided
        if not start_date:
            start_date = today - timedelta(days=180)
        if not end_date:
            end_date = today

        query = db.query(func.count().label('TotalBrokerLeadCount')).filter(
            Lead.BrokerId.isnot(None),
            Lead.CreatedDate >= start_date,
            Lead.CreatedDate <= end_date
        )

        if site_id:
            query = query.filter(Lead.SiteId.in_(site_id))
        if broker_id:
            query = query.filter(Lead.BrokerId == broker_id)

        total_count = query.scalar() or 0

        return {
            "start_date": start_date,
            "end_date": end_date,
            "TotalBrokerLeadCount": total_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/Broker-Visitors-6mo", status_code=status.HTTP_200_OK)
async def broker_visitors(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    try:
        today = get_date()

        # Default to last 6 full months
        if not start_date:
                start_date = today - timedelta(days=180)
        if not end_date:
            end_date = today

        # DATEFROMPARTS equivalent
        month_start = func.datefromparts(
            func.year(Visitors.CreatedDate),
            func.month(Visitors.CreatedDate),
            literal_column("1")
        ).label("Month")

        query = db.query(
            Contact.ContactId,
            Contact.ContactType,
            month_start,
            func.count().label("BrokerVisitorCount")
        ).join(
            Contact, and_(
                Contact.ContactId == Visitors.ContactId,
                Contact.ContactType == 'Broker'
            )
        ).join(
            Visit, Visit.VisitId == Visitors.VisitId
        ).filter(
            Visitors.CreatedDate >= start_date,
            Visitors.CreatedDate <= end_date
        )

        if site_id:
            query = query.filter(Visit.SiteId.in_(site_id))
        if broker_id:
            query = query.filter(Contact.ContactId == broker_id)

        query = query.group_by(
            Contact.ContactId,
            Contact.ContactType,
            month_start
        ).order_by(
            month_start, Contact.ContactId
        )

        results = query.all()

        return [
            {
                "BrokerId": row.ContactId,
                "ContactType": row.ContactType,
                "Month": row.Month.strftime('%Y-%m-%d') if isinstance(row.Month, (date, datetime)) else str(row.Month),
                "BrokerVisitorCount": row.BrokerVisitorCount
            }
            for row in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/Broker-Visit-Distribution", status_code=status.HTTP_200_OK)
async def broker_visit_distribution(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    try:
        today = get_date()

        # Default to last 6 months if no dates provided
        if not start_date:
            # start_date = today - timedelta(days=180)
            start_date = today.replace(day=1)
        if not end_date:
            end_date = today

        # Broker Full Name (first + last)
        broker_name = (
            Contact.ContactFName + literal_column("' '") +
            func.coalesce(Contact.ContactLName, literal_column("''"))
        ).label('BrokerName')

        # Date parts
        visit_year = func.datepart(text('YEAR'), Visitors.CreatedDate).label('VisitYear')
        visit_month = func.datepart(text('MONTH'), Visitors.CreatedDate).label('VisitMonth')

        first_week_number = func.datepart(
            text('WEEK'),
            func.datefromparts(
                func.year(Visitors.CreatedDate),
                func.month(Visitors.CreatedDate),
                text('1')
            )
        )

        current_week_number = func.datepart(text('WEEK'), Visitors.CreatedDate)

        week_of_month = (
            current_week_number - first_week_number + literal_column('1')
        ).label('WeekOfMonth')

        # Main Query
        query = db.query(
            Contact.ContactId.label('BrokerId'),
            broker_name,
            visit_year,
            visit_month,
            week_of_month,
            func.count(distinct(Visit.VisitId)).label('TotalSiteVisits')
        ).select_from(Visitors).join(
            Visit, Visitors.VisitId == Visit.VisitId
        ).join(
            Contact, Visitors.ContactId == Contact.ContactId
        ).filter(
            Contact.ContactType == 'Broker',
            Visitors.CreatedDate >= start_date,
            Visitors.CreatedDate <= end_date
        )

        if site_id:
            query = query.filter(Visit.SiteId.in_(site_id))
        if broker_id:
            query = query.filter(Contact.ContactId == broker_id)

        query = query.group_by(
            Contact.ContactId,
            broker_name,
            visit_year,
            visit_month,
            week_of_month
        ).order_by(
            visit_year,
            visit_month,
            week_of_month,
            broker_name
        )

        results = query.all()

        response = [
            {
                # "BrokerId": row.BrokerId,
                # "BrokerName": row.BrokerName,
                "VisitYear": row.VisitYear,
                "VisitMonth": row.VisitMonth,
                "WeekOfMonth": row.WeekOfMonth,
                "TotalSiteVisits": row.TotalSiteVisits
            }
            for row in results
        ]

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/Broker-Wise-Customers")
async def broker_wise_customers(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    query = db.query(
        Lead.BrokerId,
        Lead.LeadStatus,
        Contact.ContactFName,
        func.count(distinct(Lead.ContactId)).label("CustomerCount")
    ).outerjoin(
        Contact,
        and_(
            Contact.ContactId == Lead.BrokerId,
            Contact.ContactType == 'broker'
        )
    ).filter(
        Lead.LeadStatus == 'Win',
        Lead.BrokerId.isnot(None),
        Lead.CreatedDate >= start_date,
        Lead.CreatedDate <= end_date
    )

    if site_id:
        query = query.filter(Lead.SiteId.in_(site_id))
    if broker_id:
        query = query.filter(Lead.BrokerId == broker_id)

    query = query.group_by(
        Lead.BrokerId,
        Lead.LeadStatus,
        Contact.ContactFName
    ).order_by(
        func.count(distinct(Lead.ContactId)).desc()
    ).limit(5)

    results = query.all()

    return [
        {
            "BrokerId": row.BrokerId,
            "LeadStatus": row.LeadStatus,
            "BrokerFName": row.ContactFName,
            "CustomerCount": row.CustomerCount
        }
        for row in results
    ]



@router.get("/Site-Broker-Performance")
async def site_broker_performance(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    if not start_date:
        # start_date = today - timedelta(days=180)
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

        # Base query with mandatory filters
    query = db.query(
        Lead.SiteId,
        Lead.LeadStatus,
        func.count(Lead.LeadId).label("LeadCount")
    ).filter(
        Lead.BrokerId.isnot(None),
        Lead.CreatedDate >= start_date,
        Lead.CreatedDate <= end_date
    )

    # Optional filters
    if site_id:
        query = query.filter(Lead.SiteId.in_(site_id))
    if broker_id:
        query = query.filter(Lead.BrokerId == broker_id)

    query = query.group_by(Lead.SiteId, Lead.LeadStatus)

    results = query.all()

    return [
        {
            "SiteId": row.SiteId,
            "LeadStatus": row.LeadStatus,
            "LeadCount": row.LeadCount
        }
        for row in results
    ]
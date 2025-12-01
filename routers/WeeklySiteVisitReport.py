from string import ascii_uppercase
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException,status, Query
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
# from models import Lead, Contact, ProspectType, Site
from typing import Annotated, Optional,List
from sqlalchemy.orm import Session, joinedload, load_only, aliased
from sqlalchemy import select, func, text, distinct, and_, case, literal_column, desc
from database import SessionLocal
from models import  Visitors, Contact, Visit, Users
from .auth import get_current_user
from datetime import datetime, timedelta
from schemas.schemas import TargetsRequest
from sqlalchemy import cast, Date
from datetime import datetime, timedelta, date

from .infra_unit import get_time

router = APIRouter(
    prefix="/WeeklySiteVisitReport",
    tags = ['WeeklySiteVisitReport']
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


@router.get("/Total-visits")
async def total_visits(user: user_dependency,db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    Broker_id : Optional[int] = Query(None),
    contact_id : Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    today = get_date()
    # If no dates provided, default to current month
    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today
    # 👉 Count directly from Visit table
    query = db.query(func.count(Visit.VisitId).label("TotalVisits"))
    # Apply date filters
    query = query.filter(Visit.VisitDate >= start_date)
    query = query.filter(Visit.VisitDate <= end_date)

    # if site_id:
    #     query = query.filter(Visit.SiteId == site_id)

    if site_id:
        query = query.filter(Visit.SiteId.in_(site_id))

    # 👉 Only join Visitors & Contact if Broker_id or contact_id is provided
    if Broker_id or contact_id:
        query = query.join(Visitors, Visitors.VisitId == Visit.VisitId)
        query = query.join(Contact, Visitors.ContactId == Contact.ContactId)

    if Broker_id:
        query = query.filter(Contact.ContactType == 'Broker', Contact.ContactId == Broker_id)

    if contact_id:
        query = query.filter(Contact.ContactType == 'Customer', Contact.ContactId == contact_id)

    total_visits = query.scalar()

    return {
        "StartDate": start_date,
        "EndDate": end_date,
        # "SiteIds": site_id,
        "TotalVisits": total_visits
    }



@router.get("/direct-visits")
def get_direct_visits(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # site_id: Optional[int] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    CustomerContact = aliased(Contact)
    # Base query using ORM with left outer join and filter
    query = db.query(
        func.count(distinct(Visitors.VisitId)).label("TotalDirectVisits")
    ).join(
        Visit, Visitors.VisitId == Visit.VisitId
    ).join(
        CustomerContact, Visitors.ContactId == CustomerContact.ContactId
    ).filter(
        Visitors.VisitId != None,
        CustomerContact.ContactType == "Customer"
    )
    # ✅ Apply correct date filters on VisitDate
    query = query.filter(Visit.VisitDate >= start_date)
    query = query.filter(Visit.VisitDate <= end_date)

    # if site_id:
    #     query = query.filter(Visit.SiteId == site_id)

    if site_id:
        query = query.filter(Visit.SiteId.in_(site_id))

    if broker_id:
        query = query.join(
            Contact, Visitors.ContactId == Contact.ContactId
        ).filter(
            Contact.ContactType == 'Broker',
            Contact.ContactId == broker_id
        )

    if customer_id:
        query = query.filter(CustomerContact.ContactId == customer_id)

    total_direct_visits = query.scalar()

    return {
        "StartDate": start_date,
        "EndDate": end_date,
        "TotalDirectVisits": total_direct_visits
    }



@router.get("/broker-visits")
def get_broker_visits(user: user_dependency,db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # site_id: Optional[int] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    CustomerContact = aliased(Contact)
    BrokerContact = aliased(Contact)

    # query = db.query(
    #     func.count(distinct(Visitors.VisitId)).label("TotalBrokerVisits")
    query = db.query(
        func.count(distinct(func.concat(Visitors.VisitId, '-', BrokerContact.ContactId))).label("TotalBrokerVisits")
    ).join(
        BrokerContact, Visitors.ContactId == BrokerContact.ContactId
    ).join(
        Visit, Visitors.VisitId == Visit.VisitId
    ).filter(
        Visitors.VisitId != None,
        BrokerContact.ContactType == 'Broker',
        Visit.VisitDate >= start_date,
        Visit.VisitDate <= end_date
    )

    # # ✅ Apply correct date filters on VisitDate
    # query = query.filter(Visit.VisitDate >= start_date)
    # query = query.filter(Visit.VisitDate <= end_date)

    # if site_id:
    #     query = query.filter(Visit.SiteId == site_id)

    if site_id:
        query = query.filter(Visit.SiteId.in_(site_id))

    if broker_id:
        query = query.filter(BrokerContact.ContactId == broker_id)

    if customer_id:
        query = query.join(
            CustomerContact, Visitors.ContactId == CustomerContact.ContactId
        ).filter(
            CustomerContact.ContactType == 'Customer',
            CustomerContact.ContactId == customer_id
        )

    total_broker_visits = query.scalar()

    return {
        "StartDate": start_date,
        "EndDate": end_date,
        "TotalBrokerVisits": total_broker_visits
    }



@router.get("/new-broker-visits")
def get_new_broker_visits(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # site_id: Optional[int] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    if not start_date:
        start_date = today - timedelta(days=30)
    if not end_date:
        end_date = today

    CustomerContact = aliased(Contact)
    BrokerContact = aliased(Contact)

    query = db.query(
        func.count(distinct(Visitors.VisitId)).label("TotalNewBrokerVisits")
    ).join(
        BrokerContact, Visitors.ContactId == BrokerContact.ContactId
    ).join(
        Visit, Visitors.VisitId == Visit.VisitId
    ).filter(
        BrokerContact.ContactType == 'Broker'
    )

    # ✅ Date filter based on when the broker was created
    query = query.filter(BrokerContact.CreatedDate >= start_date)
    query = query.filter(BrokerContact.CreatedDate <= end_date)

    # if site_id:
    #     query = query.filter(Visit.SiteId == site_id)

    if site_id:
        query = query.filter(Visit.SiteId.in_(site_id))

    if broker_id:
        query = query.filter(BrokerContact.ContactId == broker_id)

    if customer_id:
        # Join CustomerContact to filter by customer involved in the visit
        query = query.join(
            CustomerContact, Visitors.ContactId == CustomerContact.ContactId
        ).filter(
            CustomerContact.ContactType == 'Customer',
            CustomerContact.ContactId == customer_id
        )

    count = query.scalar()

    return {
        "StartDate": start_date,
        "EndDate": end_date,
        "TotalNewBrokerVisits": count
    }




@router.get("/Visit-Trends")
def get_Visit_Trends(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # site_id: Optional[int] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    # Default to current month if dates not provided
    if not start_date:
        start_date = today.replace(day=1)

    if not end_date:
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)

    CustomerContact = aliased(Contact)

    week_start_expr = func.DATEADD(
        text("WEEK"),
        func.DATEDIFF(text("WEEK"), text("0"), Visit.VisitDate),
        text("0")
    ).label("WeekStartDate")

    base_query = db.query(
        week_start_expr,
        func.count(func.distinct(Visit.VisitId)).label("TotalVisits")
    ).outerjoin(
        Visitors, Visit.VisitId == Visitors.VisitId
    ).outerjoin(
        Contact, Visitors.ContactId == Contact.ContactId
    ).filter(
        Visit.VisitDate >= start_date,
        Visit.VisitDate <= end_date
    )

    # if site_id:
    #     base_query = base_query.filter(Visit.SiteId == site_id)

    if site_id:
        base_query = base_query.filter(Visit.SiteId.in_(site_id))

    if broker_id:
        base_query = base_query.filter(Contact.ContactType == 'Broker', Contact.ContactId == broker_id)

    if customer_id:
        base_query = base_query.join(
            CustomerContact, Visitors.ContactId == CustomerContact.ContactId
        ).filter(
            CustomerContact.ContactType == 'Customer',
            CustomerContact.ContactId == customer_id
        )

    base_query = base_query.group_by(week_start_expr).order_by(week_start_expr)

    subquery = base_query.subquery()

    results = db.query(
        func.ROW_NUMBER().over(order_by=subquery.c.WeekStartDate).label("WeekNumber"),
        subquery.c.WeekStartDate,
        subquery.c.TotalVisits
    ).all()

    current_week_number = today.isocalendar()[1]

    response = []
    for row in results:
        # Check if this is the current week
        week_number = row.WeekStartDate.isocalendar()[1]
        is_current_week = (week_number == current_week_number)

        response.append({
            "WeekNumber": row.WeekNumber,
            "WeekStartDate": row.WeekStartDate,
            "TotalVisits": row.TotalVisits,
            "CurrentWeekTotalVisits": row.TotalVisits if is_current_week else 0
        })

    return response




@router.get("/Visits-by-Site")
def get_weekly_site_visits(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # site_id: Optional[int] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    # Default to current month if dates not provided
    if not start_date:
        start_date = today.replace(day=1)

    if not end_date:
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)

    CustomerContact = aliased(Contact)

    query = db.query(
        Visit.SiteId,
        func.count(func.distinct(Visit.VisitId)).label("TotalVisits")
    ).outerjoin(
        Visitors, Visit.VisitId == Visitors.VisitId
    ).outerjoin(
        Contact, Visitors.ContactId == Contact.ContactId
    ).filter(
        Visit.VisitDate >= start_date,
        Visit.VisitDate <= end_date
    )

    # if site_id:
    #     query = query.filter(Visit.SiteId == site_id)

    if site_id:
        query = query.filter(Visit.SiteId.in_(site_id))

    if broker_id:
        query = query.filter(Contact.ContactType == 'Broker', Contact.ContactId == broker_id)

    if customer_id:
        query = query.join(
            CustomerContact, Visitors.ContactId == CustomerContact.ContactId
        ).filter(
            CustomerContact.ContactType == 'Customer',
            CustomerContact.ContactId == customer_id
        )

    query = query.group_by(
        Visit.SiteId
    ).order_by(
        Visit.SiteId
    )

    results = query.all()

    return [
        {
            "SiteId": row.SiteId,
            "TotalVisits": row.TotalVisits
        }
        for row in results
    ]


@router.get("/visit-status-weekly")
def get_weekly_visit_status(user: user_dependency, db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # site_id: Optional[int] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),

    customer_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    if not start_date:
        start_date = date(2000, 1, 1)  # Default to earliest if not provided
    if not end_date:
        end_date = today

    # Remove time component from VisitDate
    visit_date_expr = cast(Visit.VisitDate, Date).label("VisitDate")

    completed_count = func.sum(
        case((Visit.VisitStatus == 'Completed', 1), else_=0)
    ).label("CompletedCount")

    rescheduled_count = func.sum(
        case((Visit.VisitStatus == 'Rescheduled', 1), else_=0)
    ).label("RescheduledCount")

    cancelled_count = func.sum(
        case((Visit.VisitStatus == 'Cancelled', 1), else_=0)
    ).label("CancelledCount")

    # Base query only from Visit table
    query = db.query(
        visit_date_expr,
        completed_count,
        rescheduled_count,
        cancelled_count
    ).filter(
        Visit.VisitStatus.in_(['Completed', 'Rescheduled', 'Cancelled']),
        cast(Visit.VisitDate, Date) >= start_date,
        cast(Visit.VisitDate, Date) <= end_date
    )

    # if site_id:
    #     query = query.filter(Visit.SiteId == site_id)

    if site_id:
        query = query.filter(Visit.SiteId.in_(site_id))

    if broker_id:
        query = query.filter(Visit.CreatedById == broker_id)

    if customer_id:
        query = query.filter(Visit.CreatedById == customer_id)

    query = query.group_by(visit_date_expr).order_by(visit_date_expr)

    results = query.all()

    return [
        {
            "VisitDate": row.VisitDate,
            "CompletedCount": row.CompletedCount,
            "RescheduledCount": row.RescheduledCount,
            "CancelledCount": row.CancelledCount
        }
        for row in results
    ]


@router.get("/buying-intent-summary")
def get_buying_intent_summary(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),
    contact_id: Optional[int] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    try:
        today = get_date()

        if not start_date:
            start_date = today.replace(day=1)
        if not end_date:
            end_date = today

        # Base query with joins for broker filtering
        query = db.query(
            Visitors.BuyingIntent,
            func.count().label("Count")
        ).join(
            Visit, Visitors.VisitId == Visit.VisitId
        ).join(
            Contact, Visitors.ContactId == Contact.ContactId
        )

        # Apply date filters
        query = query.filter(
            Visitors.CreatedDate >= start_date,
            Visitors.CreatedDate <= end_date
        )

        # Apply site filter if provided
        # if site_id:
        #     query = query.filter(Visit.SiteId == site_id)

        if site_id:
            query = query.filter(Visit.SiteId.in_(site_id))

        # Apply broker filter if provided
        if broker_id:
            query = query.filter(Contact.ContactType == 'Broker', Contact.ContactId == broker_id)

        # Apply contact ID filter if provided
        if contact_id:
            query = query.filter(Contact.ContactId == contact_id)

        # Group by BuyingIntent
        results = query.group_by(Visitors.BuyingIntent).all()

        # Initialize summary
        summary = {
            "Very High": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        for buying_intent, count in results:
            if buying_intent is None:
                continue
            elif buying_intent == 0:
                summary["Very High"] += count
            elif buying_intent == 3:
                summary["High"] += count
            elif buying_intent == 6:
                summary["Medium"] += count
            elif buying_intent > 6:
                summary["Low"] += count

        # Return structured result
        return [
            {"Category": "Very High", "Total": summary["Very High"]},
            {"Category": "High", "Total": summary["High"]},
            {"Category": "Medium", "Total": summary["Medium"]},
            {"Category": "Low", "Total": summary["Low"]},
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/Sales-Team-Pref")
def get_Sales_Team_Pref(
    user: user_dependency,
    db: db_dependency,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # site_id: Optional[int] = Query(None),
    site_id: Optional[List[int]] = Query(None),
    broker_id: Optional[int] = Query(None),
    contact_id: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    today = get_date()

    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    total_visits = func.count(Visit.VisitId).label("TotalVisits")
    total_completed = func.count(
        case((Visit.VisitStatus == 'Completed', 1))
    ).label("TotalCompleted")

    query = db.query(
        Users.FirstName,
        Users.LastName,
        total_visits,
        total_completed
    ).outerjoin(
        Visit, Visit.CreatedById == Users.id
    ).outerjoin(
        Visitors, Visit.VisitId == Visitors.VisitId
    ).outerjoin(
        Contact, Visitors.ContactId == Contact.ContactId
    )

    query = query.filter(
        Visit.CreatedDate >= start_date,
        Visit.CreatedDate <= end_date
    )

    # if site_id:
    #     query = query.filter(Visit.SiteId == site_id)

    if site_id:
        query = query.filter(Visit.SiteId.in_(site_id))

    if broker_id:
        query = query.filter(Contact.ContactType == 'Broker', Contact.ContactId == broker_id)

    if contact_id:
        query = query.filter(Contact.ContactId == contact_id)

    # Group, order by TotalVisits descending, and limit to top 5
    results = query.group_by(Users.FirstName, Users.LastName)\
        .order_by(desc("TotalVisits"))\
        .limit(5)\
        .all()

    return [
        {
            "FirstName": row.FirstName,
            "LastName": row.LastName,
            "TotalVisits": row.TotalVisits,
            "TotalCompleted": row.TotalCompleted
        }
        for row in results
    ]



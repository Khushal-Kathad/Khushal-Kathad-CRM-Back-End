

# from fastapi import APIRouter, Depends, HTTPException,status
# from sqlalchemy.orm import Session,joinedload, load_only
# from database import SessionLocal
# from datetime import datetime
# from pytz import timezone
# from typing import Annotated
# from .auth import get_current_user
# from pydantic import EmailStr
# from twilio.rest import Client
# import requests
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.image import MIMEImage
#
#
# router = APIRouter(
#     prefix="/weekly Report",
#     tags = ['weekly Report']
# )
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def get_time():
#     ind_time = datetime.now(timezone("Asia/Kolkata"))
#     return ind_time
#
# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]
#
#
# # Twilio setup - USE ENVIRONMENT VARIABLES
# TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
# TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
# TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
# TWILIO_SMS_FROM = os.getenv('TWILIO_SMS_FROM')
# TWILIO_TO_NUMBER = os.getenv('TWILIO_TO_NUMBER')
#
# # Email setup - USE ENVIRONMENT VARIABLES
# SENDER_EMAIL = os.getenv('SENDER_EMAIL')
# SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
# RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
#
# VISIT_REPORT_URL = 'http://127.0.0.1:8000/visit/visit_report/'
#
# @router.post("/send_report")
# def send_report(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     # Step 1: Fetch report data
#     try:
#         response = requests.get(VISIT_REPORT_URL)
#         response.raise_for_status()
#         data = response.json()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching report data: {e}")
#
#     # Step 2: Parse data
#     new_visit_count = data.get("New Visit", 0)
#     revisit_count = data.get("Re-Visit", 0)
#     direct_visit_count = data.get("Direct Visit", 0)
#     re_visit_alias = data.get("Re-visit", 0)  # fallback key
#
#     total_visit = new_visit_count + revisit_count + direct_visit_count + re_visit_alias
#
#     # Step 3: Message body
#     message_body = (
#         f'Pillar CRM weekly Report\n'
#         f'Total Site Visit - {total_visit}\n'
#         f'Direct Visit - {direct_visit_count}\n'
#         f'Re-Visit - {revisit_count}\n'
#         f'New Visit - {new_visit_count}'
#     )
#
#     # Step 4: Send WhatsApp and SMS
#     try:
#         twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#
#         twilio_client.messages.create(
#             from_=TWILIO_WHATSAPP_FROM,
#             body=message_body,
#             to=f'whatsapp:{TWILIO_TO_NUMBER}'
#         )
#
#         twilio_client.messages.create(
#             from_=TWILIO_SMS_FROM,
#             body=message_body,
#             to=TWILIO_TO_NUMBER
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Twilio error: {e}")
#
#     try:
#         from email.mime.image import MIMEImage
#         msg = MIMEMultipart('related')
#         msg['From'] = SENDER_EMAIL
#         msg['To'] = RECIPIENT_EMAIL
#         msg['Subject'] = "Pillar CRM Weekly Visit Report"
#
#         msg_alt = MIMEMultipart('alternative')
#         msg.attach(msg_alt)
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(SENDER_EMAIL, SENDER_PASSWORD)
#             server.send_message(msg)
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Email error: {e}")
#
#     return {"message": "Report sent via WhatsApp, SMS, and Email successfully."}










# -----------------------------------------------------------------------------------------------------------



# from fastapi import APIRouter, Depends, HTTPException,status
# from sqlalchemy.orm import Session,joinedload, load_only
# from database import SessionLocal
# from datetime import datetime
# from pytz import timezone
# from typing import Annotated
# from .auth import get_current_user
# from pydantic import EmailStr
# from twilio.rest import Client
# import requests
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
#
#
# router = APIRouter(
#     prefix="/weekly Report",
#     tags = ['weekly Report']
# )
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def get_time():
#     ind_time = datetime.now(timezone("Asia/Kolkata"))
#     return ind_time
#
# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]
#
#
# # Twilio setup - USE ENVIRONMENT VARIABLES
# TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
# TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
# TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
# TWILIO_SMS_FROM = os.getenv('TWILIO_SMS_FROM')
# TWILIO_TO_NUMBER = os.getenv('TWILIO_TO_NUMBER')
#
# # Email setup - USE ENVIRONMENT VARIABLES
# SENDER_EMAIL = os.getenv('SENDER_EMAIL')
# SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
# RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
#
# VISIT_REPORT_URL = 'http://127.0.0.1:8000/visit/visit_report/'
#
#
#
#
# @router.post("/send_report")
# def send_report(user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     try:
#         response = requests.get(VISIT_REPORT_URL)
#         response.raise_for_status()
#         data = response.json()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching report data: {e}")
#
#     # Step 2: Parse data
#     new_visit_count = data.get("New Visit", 0)
#     revisit_count = data.get("Re-Visit", 0)
#     direct_visit_count = data.get("Direct Visit", 0)
#     re_visit_alias = data.get("Re-visit", 0)  # Inconsistent key fallback
#
#     total_visit = new_visit_count + revisit_count + direct_visit_count + re_visit_alias
#
#     # Step 3: Message body
#     message_body = (
#         f'Pillar CRM weekly Report\n'
#         f'Total Site Visit - {total_visit}\n'
#         f'Direct Visit - {direct_visit_count}\n'
#         f'Re-Visit - {revisit_count}\n'
#         f'New Visit - {new_visit_count}'
#     )
#
#     # Step 4: Send WhatsApp and SMS
#     try:
#         twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#
#         whatsapp_message = twilio_client.messages.create(
#             from_=TWILIO_WHATSAPP_FROM,
#             body=message_body,
#             to=f'whatsapp:{TWILIO_TO_NUMBER}'
#         )
#
#         sms_message = twilio_client.messages.create(
#             from_=TWILIO_SMS_FROM,
#             body=message_body,
#             to=TWILIO_TO_NUMBER
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Twilio error: {e}")
#
#     # Step 5: Send Email with unchanged HTML
#     html = f"""
#     <html>
#     <head>
#       <style>
#         .container {{
#             font-family: Arial, sans-serif;
#             padding: 20px;
#             background-color: #f9f9f9;
#             max-width: 600px;
#             margin: auto;
#             border: 1px solid #ddd;
#             border-radius: 10px;
#         }}
#         h2 {{
#             text-align: center;
#             color: #2c3e50;
#         }}
#         table {{
#             width: 100%;
#             border-collapse: collapse;
#             margin-top: 20px;
#         }}
#         th, td {{
#             padding: 12px;
#             border: 1px solid #ddd;
#             text-align: center;
#         }}
#         th {{
#             background-color: #4CAF50;
#             color: white;
#         }}
#         .footer {{
#             text-align: center;
#             color: #999;
#             margin-top: 30px;
#             font-size: 12px;
#         }}
#       </style>
#     </head>
#     <body>
#       <div class="container">
#         <h2>Pillar CRM Weekly Visit Report</h2>
#         <table>
#           <tr>
#             <th>Visit Type</th>
#             <th>Count</th>
#           </tr>
#           <tr>
#             <td>Total Site Visit</td>
#             <td>{total_visit}</td>
#           </tr>
#           <tr>
#             <td>Direct Visit</td>
#             <td>{direct_visit_count}</td>
#           </tr>
#           <tr>
#             <td>Re-Visit</td>
#             <td>{revisit_count + re_visit_alias}</td>
#           </tr>
#           <tr>
#             <td>New Visit</td>
#             <td>{new_visit_count}</td>
#           </tr>
#         </table>
#         <div class="footer">
#           This report was generated automatically by Pillar CRM.
#         </div>
#       </div>
#     </body>
#     </html>
#     """
#
#     try:
#         msg = MIMEMultipart('alternative')
#         msg['From'] = SENDER_EMAIL
#         msg['To'] = RECIPIENT_EMAIL
#         msg['Subject'] = "Pillar CRM Weekly Visit Report"
#         msg.attach(MIMEText(html, 'html'))
#
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(SENDER_EMAIL, SENDER_PASSWORD)
#             server.send_message(msg)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Email error: {e}")
#
#     return {
#         "message": "Report sent successfully via WhatsApp, SMS, and Email.",
#         "sms_sid": sms_message.sid,
#         "whatsapp_sid": whatsapp_message.sid
#     }



# ----------------------------------------------------------------------------------------------------------------------
# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from sqlalchemy.orm import Session, joinedload, load_only
# from sqlalchemy import func, and_
# from database import SessionLocal
# from datetime import datetime, timedelta
# from pytz import timezone
# from typing import Annotated
# from .auth import get_current_user
# from pydantic import EmailStr
# from twilio.rest import Client
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
#
# # Import your models here - adjust according to your actual model names
# from models import Visit  # Replace with your actual model import path
#
# from fastapi.templating import Jinja2Templates
# import os
#
# router = APIRouter(
#     prefix="/weekly_report",
#     tags=['weekly_report']
# )
#
# templates = Jinja2Templates(directory="templates")
#
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def get_time():
#     ind_time = datetime.now(timezone("Asia/Kolkata"))
#     return ind_time
#
#
# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]
#
# # Twilio setup - USE ENVIRONMENT VARIABLES
# TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
# TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
# TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
# TWILIO_SMS_FROM = os.getenv('TWILIO_SMS_FROM')
# TWILIO_TO_NUMBER = os.getenv('TWILIO_TO_NUMBER')
#
# # Email setup - USE ENVIRONMENT VARIABLES
# SENDER_EMAIL = os.getenv('SENDER_EMAIL')
# SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
# RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
#
# def fetch_report_data_from_db(db: Session):
#     try:
#         visit_counts = (
#             db.query(Visit.VisitType, func.count(Visit.VisitId))
#             .filter(Visit.VisitType.in_(["New Visit", "Re-visit", "Direct Visit"]))
#             .group_by(Visit.VisitType)
#             .all()
#         )
#
#         # Initialize response with default values
#         response = {
#             "New Visit": 0,
#             "Re-visit": 0,
#             "Direct Visit": 0
#         }
#
#         # Update with actual counts
#         for visit_type, count in visit_counts:
#             response[visit_type] = count
#
#         # Extract individual counts (matching your original variable names)
#         new_visit_count = response.get("New Visit", 0)
#         revisit_count = response.get("Re-visit", 0)  # Note: "Re-visit" not "Re-Visit"
#         direct_visit_count = response.get("Direct Visit", 0)
#         re_visit_alias = response.get("Re-Visit", 0)  # Fallback for inconsistent key (if any)
#
#         total_visit = new_visit_count + revisit_count + direct_visit_count + re_visit_alias
#
#         return {
#             "new_visit_count": new_visit_count,
#             "revisit_count": revisit_count,
#             "direct_visit_count": direct_visit_count,
#             "re_visit_alias": re_visit_alias,
#             "total_visit": total_visit
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching report data from database: {e}")
#
# @router.post("/send_whatsapp")
# def send_whatsapp_report(user: user_dependency, db: db_dependency):
#     """Send weekly report via WhatsApp"""
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     # Fetch report data from database
#     report_data = fetch_report_data_from_db(db)
#
#     # Create message body
#     message_body = (
#         f'Pillar CRM Weekly Report\n'
#         f'Total Site Visit - {report_data["total_visit"]}\n'
#         f'Direct Visit - {report_data["direct_visit_count"]}\n'
#         f'Re-Visit - {report_data["revisit_count"]}\n'
#         f'New Visit - {report_data["new_visit_count"]}'
#     )
#
#     # Send WhatsApp message
#     try:
#         twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#
#         whatsapp_message = twilio_client.messages.create(
#             from_=TWILIO_WHATSAPP_FROM,
#             body=message_body,
#             to=f'whatsapp:{TWILIO_TO_NUMBER}'
#         )
#
#         return {
#             "message": "WhatsApp report sent successfully",
#             "whatsapp_sid": whatsapp_message.sid,
#             "timestamp": get_time().isoformat()
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"WhatsApp error: {e}")
#
#
# @router.post("/send_sms")
# def send_sms_report(user: user_dependency, db: db_dependency):
#     """Send weekly report via SMS"""
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     # Fetch report data from database
#     report_data = fetch_report_data_from_db(db)
#
#     # Create message body
#     message_body = (
#         f'Pillar CRM Weekly Report\n'
#         f'Total Site Visit - {report_data["total_visit"]}\n'
#         f'Direct Visit - {report_data["direct_visit_count"]}\n'
#         f'Re-Visit - {report_data["revisit_count"]}\n'
#         f'New Visit - {report_data["new_visit_count"]}'
#     )
#
#     # Send SMS
#     try:
#         twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#
#         sms_message = twilio_client.messages.create(
#             from_=TWILIO_SMS_FROM,
#             body=message_body,
#             to=TWILIO_TO_NUMBER
#         )
#
#         return {
#             "message": "SMS report sent successfully",
#             "sms_sid": sms_message.sid,
#             "timestamp": get_time().isoformat()
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"SMS error: {e}")
#
#
# @router.post("/send_email")
# def send_email_report(request: Request,user: user_dependency, db: db_dependency):
#     """Send weekly report via Email"""
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     report_data = fetch_report_data_from_db(db)
#     html_ = templates.get_template("email_report.html").render({
#         "request": request,
#         "user": user,
#         "report_data": report_data
#     })
#     try:
#         msg = MIMEMultipart('alternative')
#         msg['From'] = SENDER_EMAIL
#         msg['To'] = RECIPIENT_EMAIL
#         msg['Subject'] = "Pillar CRM Weekly Visit Report"
#         msg.attach(MIMEText(html_, 'html'))
#
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(SENDER_EMAIL, SENDER_PASSWORD)
#             server.send_message(msg)
#
#         return {
#             "message": "Email report sent successfully",
#             "recipient": RECIPIENT_EMAIL,
#             "timestamp": get_time().isoformat()
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Email error: {e}")



# ---------------------------------------------------------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pytz import timezone
from typing import Annotated
from twilio.rest import Client

from database import SessionLocal
from models import APIConfiguration, Visitors, NotificationConfiguration, Visit, Contact
from .auth import get_current_user
from schemas.schemas import APIConfigurationBase
import json


router = APIRouter(
    prefix="/weekly_report",
    tags=["weekly_report"]
)

# Dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Utility to get current India time
def get_time():
    return datetime.now(timezone("Asia/Kolkata"))

def fetch_report_data_from_db(db: Session):
    total_visit = db.query(Visitors).count()

    # Direct visit: Visitors.ContactId → Contact.ContactId and Contact.ContactType == 'Customer'
    direct_visit_count = (
        db.query(Visitors)
        .join(Contact, Visitors.ContactId == Contact.ContactId)
        .filter(Contact.ContactType == 'Customer')
        .count()
    )

    revisit_count = db.query(Visitors).filter(Visitors.VisitType == 'Re-visit').count()
    new_visit_count = db.query(Visitors).filter(Visitors.VisitType == 'New Visit').count()

    return {
        "total_visit": total_visit,
        "direct_visit_count": direct_visit_count,
        "revisit_count": revisit_count,
        "new_visit_count": new_visit_count
    }

# @router.post("/send_whatsapp", status_code=status.HTTP_201_CREATED)
# def send_whatsapp_report(user: user_dependency,db: db_dependency,api: APIConfigurationBase):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#
#     # Save the API configuration into the DB
#     api_configuration = APIConfiguration(**api.dict(),CreatedBy=user.get('id'), CreatedAt=get_time(),UpdatedAt=get_time())
#     db.add(api_configuration)
#     db.commit()
#
#     # Fetch report data
#     report_data = fetch_report_data_from_db(db)
#
#     # Format message for WhatsApp
#     message_body = (
#         f"*Weekly Visit Report*\n"
#         f"--------------------------\n"
#         f"Total Visits: {report_data['total_visit']}\n"
#         f"Direct Visits: {report_data['direct_visit_count']}\n"
#         f"Revisits: {report_data['revisit_count']}\n"
#         f"New Visits: {report_data['new_visit_count']}\n"
#         f"\nSent on: {get_time().strftime('%d-%m-%Y %H:%M')}"
#     )
#
#     # Send WhatsApp via Twilio
#     try:
#         client = Client(api.ConfigKey, api.ConfigValue)
#
#         whatsapp_from = f"whatsapp:{api.WhatsAppFrom}"
#         whatsapp_to = f"whatsapp:{api.ToNumber}"  # Ensure this starts with country code, like +91
#
#         message = client.messages.create(
#             body=message_body,
#             from_=whatsapp_from,
#             to=whatsapp_to
#         )
#
#         return {"message": "WhatsApp report sent successfully", "sid": message.sid}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp message: {str(e)}")



@router.post("/send_whatsapp", status_code=status.HTTP_201_CREATED)
def send_whatsapp_report(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Step 1: Fetch active Twilio credentials from APIConfiguration
    api_config = db.query(APIConfiguration).filter(
        APIConfiguration.ConfigType == "WA",  # Assuming 'WA' means WhatsApp
        APIConfiguration.IsActive == True
    ).order_by(APIConfiguration.ConfigId.desc()).first()

    if not api_config:
        raise HTTPException(status_code=404, detail="No active Twilio WhatsApp configuration found")

    # Step 2: Fetch active recipient config from NotificationConfiguration
    notification_config = db.query(NotificationConfiguration).filter(
        NotificationConfiguration.IsActive == True
    ).order_by(NotificationConfiguration.NotificationId.desc()).first()

    if not notification_config:
        raise HTTPException(status_code=404, detail="No active notification configuration found")

    # Step 3: Fetch report data
    report_data = fetch_report_data_from_db(db)

    # Step 4: Format WhatsApp message
    # message_body = (
    #     f"*Weekly Visit Report*\n"
    #     f"--------------------------\n"
    #     f"Total Visits: {report_data['total_visit']}\n"
    #     f"Direct Visits: {report_data['direct_visit_count']}\n"
    #     f"Revisits: {report_data['revisit_count']}\n"
    #     f"New Visits: {report_data['new_visit_count']}\n"
    #     f"\nSent on: {get_time().strftime('%d-%m-%Y %H:%M')}"
    # )
    #
    # # Step 5: Send message using Twilio
    # try:
    #     client = Client(api_config.ConfigKey, api_config.ConfigValue)
    #
    #     whatsapp_from = f"whatsapp:{api_config.WhatsAppFrom}"
    #     whatsapp_to = f"whatsapp:{notification_config.ToNumber}"
    #
    #     message = client.messages.create(
    #         body=message_body,
    #         from_=whatsapp_from,
    #         to=whatsapp_to
    #     )
    #
    #     return {"message": "WhatsApp report sent successfully", "sid": message.sid}
    #
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp message: {str(e)}")

    # Send WhatsApp via Template
    try:
        client = Client(api_config.ConfigKey, api_config.ConfigValue)

        whatsapp_from = f"whatsapp:{api_config.WhatsAppFrom}"
        whatsapp_to = f"whatsapp:{notification_config.ToNumber}"

        message = client.messages.create(
            from_=whatsapp_from,
            to=whatsapp_to,
            content_sid=api_config.ContentTemplateSID,  # ✅ Using Template SID
            content_variables=json.dumps({  # ✅ Mapping Variables
                "1": str(report_data['total_visit']),
                "2": str(report_data['direct_visit_count']),
                "3": str(report_data['revisit_count']),
                "4": str(report_data['new_visit_count']),
                "5": get_time().strftime('%d-%m-%Y %H:%M')
            })
        )

        return {"message": "WhatsApp weekly report sent successfully", "sid": message.sid}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp message: {str(e)}")











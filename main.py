from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

import models
import uvicorn
from database import engine,SessionLocal
from routers import (auth, todos, admin, users, lead, site, contact, prospect_type,
                      site_infra, infra, infra_unit, amenity, lead_history, action_item, targets,
                     home_api, search, developer, user_target_allotment, Follow_Ups, Account,
                     LeaveApplication, SiteType, AmenitySite, visit, upload_excel, reports, visitors,WeeklySiteVisitReport,
                     ConversionReport, MonthlyBrokerReport, weekly_report, apiConfiguration, notificationconfiguration,
                     Roles, UsersRoles, Permissions, PermissionAssignment, PermissionFilters, PermissionFilterValues, FileTracker,
                     scheduler_status, brochure)

# Import WhatsApp chatbot router
import whatsapp_chatbot

from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates
import os

# Import scheduler for lead scoring (OPTIMIZED VERSION for <10s performance)
from scheduler.score_updater_optimized import start_scheduler, shutdown_scheduler


# TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
# templates = Jinja2Templates(directory=TEMPLATES_DIR)



app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allows all origins from the list
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Comment out create_all since tables already exist in production database
# models.Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup_event():
    """Start background scheduler when app starts"""
    start_scheduler()
    print("✅ Background score update scheduler started - runs every 30 minutes")


@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown scheduler"""
    print("🛑 Shutting down background scheduler")
    shutdown_scheduler()


@app.get("/healthy")
def healthy_check():
    return {'status' : 'Healthy'}


# app.include_router(auth.router)
# # app.include_router(weekly_report.router)
# app.include_router(search.router)
# app.include_router(WeeklySiteVisitReport.router)
# app.include_router(ConversionReport.router)
# app.include_router(MonthlyBrokerReport.router)
# app.include_router(visit.router)
# app.include_router(visitors.router)
# app.include_router(infra.router)
# app.include_router(site.router)
# app.include_router(site_infra.router)
# app.include_router(developer.router)
# app.include_router(infra_unit.router)
# app.include_router(targets.router)
# app.include_router(user_target_allotment.router)
# app.include_router(contact.router)
# app.include_router(Account.router)
# app.include_router(lead.router)
# app.include_router(Follow_Ups.router)
# app.include_router(LeaveApplication.router)
# app.include_router(todos.router)
# app.include_router(action_item.router)
# app.include_router(prospect_type.router)
# app.include_router(lead_history.router)
# app.include_router(AmenitySite.router)
# app.include_router(SiteType.router)
# app.include_router(amenity.router)
# app.include_router(reports.router)
#
# app.include_router(home_api.router)
# app.include_router(admin.router)
# app.include_router(users.router)
#
# # app.include_router(broker.router)
# # app.include_router(infra_type.router)
#
#
# app.include_router(upload_excel.router)

# ----------------------------------------------
app.include_router(Account.router)
app.include_router(action_item.router)
app.include_router(admin.router)
app.include_router(amenity.router)
app.include_router(AmenitySite.router)
app.include_router(auth.router)

app.include_router(apiConfiguration.router)
app.include_router(brochure.router)
app.include_router(contact.router)
app.include_router(ConversionReport.router)
app.include_router(developer.router)
app.include_router(Follow_Ups.router)
app.include_router(home_api.router)
app.include_router(infra.router)
app.include_router(infra_unit.router)
# app.include_router(infra_type.router)
app.include_router(lead.router)
app.include_router(lead_history.router)
app.include_router(LeaveApplication.router)
app.include_router(MonthlyBrokerReport.router)
app.include_router(notificationconfiguration.router)

app.include_router(weekly_report.router)
app.include_router(prospect_type.router)
app.include_router(reports.router)
app.include_router(search.router)
app.include_router(site.router)
app.include_router(site_infra.router)
app.include_router(SiteType.router)
app.include_router(targets.router)
app.include_router(todos.router)
app.include_router(upload_excel.router)
app.include_router(user_target_allotment.router)
app.include_router(users.router)
app.include_router(visit.router)
app.include_router(visitors.router)
app.include_router(WeeklySiteVisitReport.router)
# app.include_router(weekly_report.router)
# app.include_router(broker.router)
app.include_router(Roles.router)
app.include_router(UsersRoles.router)
app.include_router(PermissionAssignment.router)
app.include_router(Permissions.router)
app.include_router(PermissionFilters.router)
app.include_router(PermissionFilterValues.router)
app.include_router(FileTracker.router)
app.include_router(scheduler_status.router)

# Include WhatsApp chatbot router
# app.include_router(whatsapp_chatbot.router)


# ============================================================
# STATIC FRONTEND SERVING (Next.js Static Export)
# ============================================================

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "out"

# Mount static assets only if directories exist (prevents crash on Databricks Apps)
if FRONTEND_DIR.exists():
    if (FRONTEND_DIR / "_next").exists():
        app.mount("/_next", StaticFiles(directory=FRONTEND_DIR / "_next"), name="next-static")
    if (FRONTEND_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    if (FRONTEND_DIR / "fonts").exists():
        app.mount("/fonts", StaticFiles(directory=FRONTEND_DIR / "fonts"), name="fonts")
    if (FRONTEND_DIR / "logo").exists():
        app.mount("/logo", StaticFiles(directory=FRONTEND_DIR / "logo"), name="logo")


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_path = FRONTEND_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return {"status": "no favicon"}


@app.get("/{full_path:path}")
async def serve_frontend(request: Request, full_path: str):
    """
    Catch-all route to serve the Next.js static frontend.
    This must be defined AFTER all API routes.
    """
    # Skip if it's an API route (already handled by routers)
    if full_path.startswith("api/"):
        return {"error": "Not found"}

    # Try to serve the exact path (e.g., /dashboard/lead -> /dashboard/lead/index.html)
    file_path = FRONTEND_DIR / full_path / "index.html"
    if file_path.exists():
        return FileResponse(file_path)

    # Try to serve as direct file (e.g., /404.html)
    file_path = FRONTEND_DIR / f"{full_path}.html"
    if file_path.exists():
        return FileResponse(file_path)

    # Try to serve the file directly (for .txt, .json, etc.)
    file_path = FRONTEND_DIR / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    # Default: serve index.html for SPA client-side routing
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    # Fallback to 404
    fallback_path = FRONTEND_DIR / "404.html"
    if fallback_path.exists():
        return FileResponse(fallback_path, status_code=404)
    return {"error": "Not found"}







#
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


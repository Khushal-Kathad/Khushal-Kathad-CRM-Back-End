import json
import os

from fastapi import APIRouter, UploadFile, File, Request, Depends, Body, HTTPException,status, Form
import pandas as pd
import io
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Lead, Contact, Visit, Infra, InfraUnit, Employees, ColumnMapping, TempUpload, ContactTemp, BrokerTemp, SiteTemp, FileTracker
from typing import Annotated, Dict
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import AmenitySiteRequest


router = APIRouter(
    prefix="/Employee",
    tags = ['Employee']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_time():
    ind_time = datetime.now(timezone("Asia/Kolkata"))
    return ind_time

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# @router.post("/upload_excel/")
# async def upload_excel(
#     # column_mapping: ColumnMapping,  # Ensure this is the first parameter
#     column_mapping: Annotated[str, Form(...)],
#     file: UploadFile = File(...),  # File parameter
#     db: Session = Depends(get_db)
# ):
#     print("Step 1: Received request to upload Excel file")
#
#     # print(f"Step 2: Column Mapping received: {column_mapping.mapping}")
#     #
#     # if not column_mapping.mapping:
#     #     print("Error: Column mapping is missing")
#     #     raise HTTPException(status_code=400, detail="Column mapping is required")
#
#     print(f"Step 1: Received request to upload Excel file: {column_mapping}")
#
#     # Convert the received string into a dictionary
#     try:
#         mapping_data = json.loads(column_mapping)
#         print(f"Step 2: Column Mapping received: {mapping_data}")
#     except json.JSONDecodeError:
#         print("Error: Invalid JSON format for column mapping")
#         raise HTTPException(status_code=400, detail="Invalid JSON format for column mapping")
#
#         # Ensure mapping is provided
#     if not mapping_data.get("mapping"):
#         print("Error: Column mapping is missing")
#         raise HTTPException(status_code=400, detail="Column mapping is required")
#
#     mapping = mapping_data["mapping"]
#
#     # Read the Excel file into a Pandas DataFrame
#     contents = await file.read()
#     print(f"Step 3: File read successfully. Size: {len(contents)} bytes")
#
#     try:
#         df = pd.read_excel(io.BytesIO(contents))
#         print(f"Step 4: Excel file loaded successfully. Columns: {df.columns.tolist()}")
#     except Exception as e:
#         print(f"Error: Failed to load Excel file. Exception: {e}")
#         raise HTTPException(status_code=400, detail="Invalid Excel file")
#
#     # Validate that provided mapping keys exist in Excel columns
#     missing_columns = [col for col in mapping.keys() if col not in df.columns]
#     print(df.columns)
#     if missing_columns:
#         print(f"Error: Missing columns in Excel: {missing_columns}")
#         raise HTTPException(status_code=400, detail=f"Missing columns in Excel: {missing_columns}")
#
#     print("Step 5: Column mapping validation successful")
#
#     # Rename columns based on user-provided mapping
#     df.rename(columns=mapping_data, inplace=True)
#     print(f"Step 6: Columns renamed successfully. New columns: {df.columns.tolist()}")
#
#     # Define the required SQL columns
#     required_columns = ["EmployeeName", "Email", "PhoneNumber"]
#
#     # Ensure missing columns are filled with NULL
#     for col in required_columns:
#         if col not in df.columns:
#             print(f"Step 7: Column '{col}' missing in data, filling with NULL")
#             df[col] = None
#
#     # Fill NaN values with None (SQL-friendly)
#     # df = df.fillna(None)
#     df = df.where(pd.notna(df), None)
#     print(f"Step 8: NaN values replaced with None")
#
#     # Convert DataFrame to a list of Employee objects
#     employees = []
#     for _, row in df.iterrows():
#         emp = Employees(
#             EmployeeName=row.get("EmployeeName"),
#             Email=row.get("Email"),
#             PhoneNumber=row.get("PhoneNumber"),
#         )
#         employees.append(emp)
#
#     print(f"Step 9: Converted {len(employees)} rows to Employee objects")
#
#     if not employees:
#         print("Error: No valid data to insert")
#         raise HTTPException(status_code=400, detail="No valid employee data found")
#
#     # Insert into database
#     try:
#         db.bulk_save_objects(employees)
#         db.commit()
#         print("Step 10: Data committed to the database successfully")
#     except Exception as e:
#         db.rollback()
#         print(f"Error: Failed to insert data into the database. Exception: {e}")
#         raise HTTPException(status_code=500, detail="Failed to insert data into the database")
#
#     return {"message": "Excel data uploaded successfully!"}




# ------------------------------------------------------------------------------------------


@router.post("/upload_excel/")
async def upload_excel(
    model_name: Annotated[str, Form(...)],
    column_mapping: Annotated[str, Form(...)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    MODEL_MAPPING = {
        "employees": Employees,
        "lead": Lead,
        "contact": Contact,
        "visit": Visit,
        "infra": Infra,
        "infraunit": InfraUnit
    }
    if model_name.lower() not in MODEL_MAPPING:
        raise HTTPException(status_code=400, detail="Invalid model name")

    model = MODEL_MAPPING[model_name.lower()]

    try:
        mapping_data = json.loads(column_mapping)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for column mapping")

    if not mapping_data.get("mapping"):
        raise HTTPException(status_code=400, detail="Column mapping is required")

    mapping = mapping_data["mapping"]

    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Excel file")

    missing_columns = [col for col in mapping.keys() if col not in df.columns]
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Missing columns in Excel: {missing_columns}")

    df.rename(columns=mapping, inplace=True)

    required_columns = [col.name for col in model.__table__.columns if col.name != 'id']

    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    df = df.where(pd.notna(df), None)

    objects = []
    for _, row in df.iterrows():
        obj = model(**{col: row.get(col) for col in required_columns})
        objects.append(obj)

    if not objects:
        raise HTTPException(status_code=400, detail="No valid data to insert")

    try:
        db.bulk_save_objects(objects)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to insert data into the database")

    return {"message": f"Data uploaded successfully to {model_name}!"}



# ---------------------------------------------------------------------------

#  Define a Pydantic model to ensure proper JSON structure
# class ColumnMapping(BaseModel):
#     mapping: Dict[str, str]

# @router.post("/upload_excel/")
# async def upload_excel(
#     column_mapping: ColumnMapping,  #  Place this first
#     file: UploadFile = File(...),   #  Keep File after required parameters
#     db: Session = Depends(get_db)
# ):
#     if not column_mapping.mapping:
#         raise HTTPException(status_code=400, detail="Column mapping is required")
#
#     # Read the Excel file into a Pandas DataFrame
#     contents = await file.read()
#     df = pd.read_excel(io.BytesIO(contents))
#
#     # Validate that provided mapping keys exist in Excel columns
#     missing_columns = [col for col in column_mapping.mapping.keys() if col not in df.columns]
#     if missing_columns:
#         raise HTTPException(status_code=400, detail=f"Missing columns in Excel: {missing_columns}")
#
#     # Rename columns based on user-provided mapping
#     df.rename(columns=column_mapping.mapping, inplace=True)
#
#     # Define the required SQL columns
#     required_columns = ["EmployeeName", "Email", "PhoneNumber"]
#
#     # Ensure missing columns are filled with NULL
#     for col in required_columns:
#         if col not in df.columns:
#             df[col] = None
#
#     # Fill NaN values with None (SQL-friendly)
#     df = df.fillna(None)
#
#     # Convert DataFrame to a list of Employee objects
#     employees = [
#         Employees(
#             EmployeeName=row.get("EmployeeName"),
#             Email=row.get("Email"),
#             PhoneNumber=row.get("PhoneNumber")
#         )
#         for _, row in df.iterrows()
#     ]
#
#     # Insert into database
#     db.bulk_save_objects(employees)
#     db.commit()
#
#     return {"message": "Excel data uploaded successfully!"}

#async def map_columns(data: ColumnMapping):
 #   return {"message": "Mapping received", "mapping": data.mapping}

#
# @router.post("/upload_excel/")
# async def upload_excel(
#     column_mapping: ColumnMapping,  # Ensure this is the first parameter
#
#     file: UploadFile = File(...),    # File parameter
#     db: Session = Depends(get_db)
# ):
#     print("Step 1: Received request to upload Excel file")
#
#     print(f"Step 2: Column Mapping received: {column_mapping.mapping}")
#     # print(f"Mapping received : {column_mapping.mapping}")
#
#     # Check if mapping is provided
#     if not column_mapping.mapping:
#         print("Error: Column mapping is missing")
#         raise HTTPException(status_code=400, detail="Column mapping is required")
#
#     # Read the Excel file into a Pandas DataFrame
#     contents = await file.read()
#     print(f"Step 3: File read successfully. Size: {len(contents)} bytes")
#
#     df = pd.read_excel(io.BytesIO(contents))
#
#     # Validate that provided mapping keys exist in Excel columns
#     missing_columns = [col for col in column_mapping.mapping.keys() if col not in df.columns]
#     if missing_columns:
#         raise HTTPException(status_code=400, detail=f"Missing columns in Excel: {missing_columns}")
#
#     # Rename columns based on user-provided mapping
#     df.rename(columns=column_mapping.mapping, inplace=True)
#
#     # Define the required SQL columns
#     required_columns = ["EmployeeName", "Email", "PhoneNumber"]
#
#     # Ensure missing columns are filled with NULL
#     for col in required_columns:
#         if col not in df.columns:
#             df[col] = None
#
#     # Fill NaN values with None (SQL-friendly)
#     df = df.fillna(None)
#
#     # Convert DataFrame to a list of Employee objects
#     employees = [
#         Employees(
#             EmployeeName=row.get("EmployeeName"),
#             Email=row.get("Email"),
#             PhoneNumber=row.get("PhoneNumber")
#         )
#         for _, row in df.iterrows()
#     ]
#
#     # Insert into database
#     db.bulk_save_objects(employees)
#     db.commit()
#
#     return {"message": "Excel data uploaded successfully!"}



# ----------------------------------------------------------------------------------------------------------


# @router.post("/upload_excel/")
# async def upload_excel(
#     column_mapping: Annotated[str, Form(...)],  # Accept JSON as a string
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     print(f"Step 1: Received request to upload Excel file: {column_mapping}")
#
#     # Convert the received string into a dictionary
#     try:
#         mapping_data = json.loads(column_mapping)
#         print(f"Step 2: Column Mapping received: {mapping_data}")
#     except json.JSONDecodeError:
#         print("Error: Invalid JSON format for column mapping")
#         raise HTTPException(status_code=400, detail="Invalid JSON format for column mapping")
#
#     # Ensure mapping is provided
#     if not mapping_data.get("mapping"):
#         print("Error: Column mapping is missing")
#         raise HTTPException(status_code=400, detail="Column mapping is required")
#
#     mapping = mapping_data["mapping"]
#
#     # Read Excel File
#     contents = await file.read()
#     print(f"Step 3: File read successfully. Size: {len(contents)} bytes")
#     print(f"Step 4: read contents: {contents}")
#
#     return {"message": "Excel file processed successfully!"}



# -----------------------------------------------------------------------------------




# @router.post("upload_excel2/")
# async def upload_excel2(
#     model_name: Annotated[str, Form(...)],
#     column_mapping: Annotated[str, Form(...)],
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     """
#     Upload Excel, store column mapping in ColumnMapping, and store data in TempUpload
#     """
#
#     # Parse column mapping JSON
#     try:
#         mapping_data = json.loads(column_mapping)
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format for column mapping")
#
#     if not mapping_data.get("mapping"):
#         raise HTTPException(status_code=400, detail="Column mapping is required")
#
#     mapping = mapping_data["mapping"]  # {ExcelColumn: DbColumn}
#
#     # Store column mapping in DB
#     mapping_objects = []
#     for excel_col, db_col in mapping.items():
#         mapping_objects.append(ColumnMapping(
#             ModelName=model_name,
#             ExcelColumn=excel_col,
#             DbColumn=db_col,
#             CreatedAt=datetime.utcnow()
#         ))
#     db.bulk_save_objects(mapping_objects)
#     db.commit()
#
#     # Read Excel file
#     contents = await file.read()
#     if not contents:
#         raise HTTPException(status_code=400, detail="Uploaded file is empty")
#
#     try:
#         # Explicitly use openpyxl for .xlsx
#         df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")
#
#     # Check for missing columns
#     missing_columns = [col for col in mapping.keys() if col not in df.columns]
#     if missing_columns:
#         raise HTTPException(status_code=400, detail=f"Missing columns in Excel: {missing_columns}")
#
#     # Rename columns according to mapping
#     df.rename(columns=mapping, inplace=True)
#
#     # Prepare TempUpload objects
#     temp_objects = []
#     for _, row in df.iterrows():
#         row_data = {"ModelName": model_name}
#         # Only fill columns that exist in TempUpload
#         for db_col in mapping.values():
#             if hasattr(TempUpload, db_col):
#                 row_data[db_col] = row.get(db_col)
#         # Store upload timestamp
#         row_data["uploaded_at"] = datetime.utcnow()
#         temp_objects.append(TempUpload(**row_data))
#
#     if not temp_objects:
#         raise HTTPException(status_code=400, detail="No valid data to insert")
#
#     # Insert into TempUpload
#     try:
#         db.bulk_save_objects(temp_objects)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Failed to insert temp data: {e}")
#
#     return {
#         "message": f"Data uploaded successfully to TempUpload for {model_name}!",
#         "rows_inserted": len(temp_objects)
#     }
# {     "mapping": {         "PartyName": "LeadName",         "Source": "LeadSource"     } }


# ----------------------------------------------------------------------------------------------------

@router.post("/upload_excel2/")
async def upload_excel2(user: user_dependency,
    model_name: Annotated[str, Form(...)],
    column_mapping: Annotated[str, Form(...)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Parse column mapping JSON
    try:
        mapping_data = json.loads(column_mapping)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for column mapping")

    if not mapping_data.get("mapping"):
        raise HTTPException(status_code=400, detail="Column mapping is required")

    mapping = mapping_data["mapping"]  # {ExcelColumn: DbColumn}

    # ---- Table mapping (source temp + destination final) ----
    table_map = {
        "lead": {"source": "TempUpload", "destination": "Lead", "model": TempUpload},
        "contact": {"source": "ContactTemp", "destination": "Contact", "model": ContactTemp},
        "site": {"source": "SiteTemp", "destination": "Site", "model": SiteTemp},
        "broker": {"source": "BrokerTemp", "destination": "Broker", "model": BrokerTemp}
    }

    table_info = table_map.get(model_name.lower())
    if not table_info:
        raise HTTPException(status_code=400, detail=f"Invalid model name: {model_name}")

    model_cls = table_info["model"]

    # ---- Read file content once ----
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    file_extension = os.path.splitext(file.filename)[1] or None
    file_size = len(file_bytes)

    # ---- Save File Info into FileTracker ----
    file_tracker = FileTracker(
        FileName=file.filename,
        FileSize=file_size,
        Status="Uploaded",
        Priority= 0,
        SourceTableName=table_info["source"],
        DestinationTableName=table_info["destination"],
        SourceSchema = "dbo",
        DestinationSchema = "dbo",
        CreatedDate=get_time(),
        ModifiedDate=get_time(),
        UploadedBy=user.get('id')  # replace with logged-in user if available
    )
    db.add(file_tracker)
    db.commit()
    db.refresh(file_tracker)

    # Reset file pointer & read Excel
    await file.seek(0)
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")

    # Check for missing columns
    missing_columns = [col for col in mapping.keys() if col not in df.columns]
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Missing columns in Excel: {missing_columns}")

    # Rename columns according to mapping
    df.rename(columns=mapping, inplace=True)

    # ---- Store column mapping in DB ----
    mapping_objects = []
    for excel_col, db_col in mapping.items():
        mapping_objects.append(ColumnMapping(
            ModelName=model_name,
            ExcelColumn=excel_col,
            DbColumn=db_col,
            CreatedAt=get_time()
        ))
    db.bulk_save_objects(mapping_objects)
    db.commit()

    # ---- Prepare Temp Table Objects ----
    temp_objects = []
    for _, row in df.iterrows():
        row_data = {
            "UploadFileId": file_tracker.FileId,
            "uploaded_at": get_time()
        }

        # Only TempUpload needs ModelName
        if model_name.lower() == "lead":
            row_data["ModelName"] = model_name

        # Only include valid columns
        for db_col in mapping.values():
            if hasattr(model_cls, db_col):
                row_data[db_col] = row.get(db_col)
        temp_objects.append(model_cls(**row_data))

    if not temp_objects:
        raise HTTPException(status_code=400, detail="No valid data to insert")

    # ---- Insert into Temp Table ----
    try:
        db.bulk_save_objects(temp_objects)
        db.commit()

        # ✅ Verify rows inserted
        inserted_count = db.query(model_cls).filter(
            getattr(model_cls, "UploadFileId") == file_tracker.FileId
        ).count()

        if inserted_count > 0:
            db.query(FileTracker).filter(
                FileTracker.FileId == file_tracker.FileId
            ).update({
                "Status": "IN_PROGRESS",
                "ModifiedDate": get_time()
            })
            db.commit()
        else:
            raise HTTPException(status_code=500, detail="Data not inserted into temp table")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert temp data: {e}")

    return {
        "message": f"Data uploaded successfully to {model_cls.__tablename__} for {model_name}!",
        "rows_inserted": inserted_count,
        "file_id": file_tracker.FileId,
        "status": file_tracker.Status,
    }

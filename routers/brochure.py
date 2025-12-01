from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pytz import timezone
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from database import SessionLocal
from models import Brochure, Site
from .auth import get_current_user
from datetime import datetime
import os
import logging
from groq import Groq
import json
import tempfile
import pdf2image
from PIL import Image
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/brochure",
    tags=['brochure']
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


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF using vision model.
    Handles image-based PDFs by converting pages to images.
    """
    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Save PDF to temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name

        logger.info(f"Converting PDF to images...")

        # Convert PDF to images (process first 10 pages for brochure info)
        images = pdf2image.convert_from_path(
            tmp_path,
            first_page=1,
            last_page=10,
            dpi=150
        )

        # Clean up temp file
        os.unlink(tmp_path)

        logger.info(f"Processing {len(images)} pages with vision AI...")

        all_text = []
        for idx, image in enumerate(images, 1):
            try:
                # Resize if too large
                max_size = 1024
                if image.width > max_size or image.height > max_size:
                    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                # Convert to base64
                img_base64 = image_to_base64(image)

                # Extract text using Groq vision model
                response = groq_client.chat.completions.create(
                    model="llama-3.2-90b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract ALL text from this property brochure page. Include prices, sizes, amenities, contact details, and all other information. Format it clearly."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }],
                    temperature=0.1,
                    max_tokens=2000
                )

                page_text = response.choices[0].message.content
                all_text.append(f"\n--- Page {idx} ---\n{page_text}")

                logger.info(f"Processed page {idx}/{len(images)} ({len(page_text)} chars)")

            except Exception as e:
                logger.warning(f"Error processing page {idx}: {e}")
                continue

        full_text = "\n\n".join(all_text)
        logger.info(f"Extracted {len(full_text)} total characters from PDF")

        return full_text

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from uploaded file.
    Supports .txt and .pdf files.
    """
    try:
        # For text files
        if filename.lower().endswith('.txt'):
            return file_content.decode('utf-8')

        # For PDF files
        elif filename.lower().endswith('.pdf'):
            return extract_text_from_pdf(file_content)

        else:
            raise ValueError(f"Unsupported file type: {filename}. Please upload .txt or .pdf files.")

    except Exception as e:
        logger.error(f"Error extracting text from file: {e}")
        raise


def extract_structured_data_with_groq(raw_text: str) -> dict:
    """
    Use Groq AI to extract structured data from brochure text.
    """
    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        # Limit text to avoid token limits
        content_sample = raw_text[:15000]

        prompt = f"""Extract comprehensive property information from this brochure and return as JSON:

{content_sample}

Extract ALL available information including:
- project_name (name of the project)
- tagline (project tagline/slogan)
- developer (object with name, established, experience_years, happy_families, projects_completed, area_constructed, mission)
- location (object with address, area, city, state)
- philosophy (project philosophy/vision)
- project_highlights (array of key features like "144 Units Only", "40+ Amenities", etc.)
- connectivity (object with nearby locations and their distances)
- configurations (array of property types with type, carpet_area, balcony, wash, total_area, floors, flat_numbers if applicable)
- amenities (array of all amenities/facilities)
- design_philosophy (object with modern, elegance, greenery themes)
- contact (object with site_office, phone array, website, social_media array)
- professional_team (object with architect, structure_engineer, facade_designer, legal_advisor, certifications)
- tower_layout (tower configuration)
- total_units (total number of units)
- total_amenities (total amenities count)

Return ONLY valid JSON with the above structure. Extract ALL details found in the brochure."""

        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction expert. Extract all relevant information from property brochures and return it as valid, comprehensive JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        logger.info(f"Structured data extracted: {data.get('project_name', 'Unknown')}")
        return data

    except Exception as e:
        logger.error(f"Error extracting structured data: {e}")
        # Return basic structure on error
        return {
            "project_name": "Unknown",
            "error": str(e)
        }


@router.post('/upload', status_code=status.HTTP_201_CREATED)
async def upload_brochure(
    user: user_dependency,
    db: db_dependency,
    file: UploadFile = File(...),
    project_name: str = Form(...),
    site_id: Optional[int] = Form(None),
    set_active: bool = Form(True)
):
    """
    Upload and process a brochure file.
    Extracts text and structured data, then stores in database.

    - **file**: Brochure file (.txt or .pdf)
    - **project_name**: Name of the project
    - **site_id**: Optional site ID to link brochure to a site
    - **set_active**: Whether to set this as the active brochure (default: True)
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        logger.info(f"Processing brochure upload: {file.filename} ({file_size} bytes)")

        # Extract text from file
        raw_text = extract_text_from_file(file_content, file.filename)

        if not raw_text:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from file"
            )

        logger.info(f"Extracted {len(raw_text)} characters from {file.filename}")

        # Extract structured data using Groq AI
        structured_data = extract_structured_data_with_groq(raw_text)

        # If set_active is True, deactivate all other brochures for this project
        if set_active:
            db.query(Brochure).filter(
                Brochure.ProjectName == project_name,
                Brochure.IsActive == True
            ).update({"IsActive": False, "UpdatedDate": get_time()})

        # Create brochure record
        brochure = Brochure(
            ProjectName=project_name,
            SiteId=site_id,
            FileName=file.filename,
            FilePath=f"./uploads/brochures/{file.filename}",
            FileSize=file_size,
            RawText=raw_text,
            StructuredData=structured_data,
            IsActive=set_active,
            IsDeleted=False,
            CreatedDate=get_time(),
            CreatedById=user.get('user_id')
        )

        db.add(brochure)
        db.commit()
        db.refresh(brochure)

        logger.info(f"Brochure saved successfully: ID {brochure.BrochureId}")

        return {
            "message": "Brochure uploaded and processed successfully",
            "brochure_id": brochure.BrochureId,
            "project_name": project_name,
            "file_type": "PDF" if file.filename.lower().endswith('.pdf') else "TEXT",
            "text_length": len(raw_text),
            "structured_data_preview": {
                "project_name": structured_data.get("project_name"),
                "location": structured_data.get("location"),
                "configurations_count": len(structured_data.get("configurations", [])),
                "amenities_count": len(structured_data.get("amenities", []))
            }
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error uploading brochure: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing brochure: {str(e)}"
        )


@router.get('/active/{project_name}', status_code=status.HTTP_200_OK)
async def get_active_brochure(
    user: user_dependency,
    db: db_dependency,
    project_name: str
):
    """
    Get the active brochure data for a specific project.
    This is used by the WhatsApp bot to get current property information.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    brochure = db.query(Brochure).filter(
        Brochure.ProjectName == project_name,
        Brochure.IsActive == True,
        Brochure.IsDeleted == False
    ).first()

    if not brochure:
        raise HTTPException(
            status_code=404,
            detail=f"No active brochure found for project: {project_name}"
        )

    return {
        "brochure_id": brochure.BrochureId,
        "project_name": brochure.ProjectName,
        "site_id": brochure.SiteId,
        "file_name": brochure.FileName,
        "structured_data": brochure.StructuredData,
        "raw_text": brochure.RawText,
        "created_date": brochure.CreatedDate,
        "updated_date": brochure.UpdatedDate
    }


@router.get('/list', status_code=status.HTTP_200_OK)
async def list_brochures(
    user: user_dependency,
    db: db_dependency,
    project_name: Optional[str] = None,
    include_deleted: bool = False
):
    """
    List all brochures with optional filtering.

    - **project_name**: Filter by project name (optional)
    - **include_deleted**: Include deleted brochures (default: False)
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    query = db.query(Brochure)

    if project_name:
        query = query.filter(Brochure.ProjectName == project_name)

    if not include_deleted:
        query = query.filter(Brochure.IsDeleted == False)

    brochures = query.order_by(desc(Brochure.CreatedDate)).all()

    return {
        "total": len(brochures),
        "brochures": [
            {
                "brochure_id": b.BrochureId,
                "project_name": b.ProjectName,
                "site_id": b.SiteId,
                "file_name": b.FileName,
                "file_size": b.FileSize,
                "is_active": b.IsActive,
                "is_deleted": b.IsDeleted,
                "created_date": b.CreatedDate,
                "updated_date": b.UpdatedDate,
                "structured_data_summary": {
                    "project_name": b.StructuredData.get("project_name") if b.StructuredData else None,
                    "location": b.StructuredData.get("location", {}).get("area") if b.StructuredData else None,
                    "configurations_count": len(b.StructuredData.get("configurations", [])) if b.StructuredData else 0,
                    "amenities_count": len(b.StructuredData.get("amenities", [])) if b.StructuredData else 0
                }
            }
            for b in brochures
        ]
    }


@router.put('/activate/{brochure_id}', status_code=status.HTTP_200_OK)
async def activate_brochure(
    user: user_dependency,
    db: db_dependency,
    brochure_id: int
):
    """
    Activate a specific brochure version.
    Deactivates all other brochures for the same project.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    brochure = db.query(Brochure).filter(
        Brochure.BrochureId == brochure_id,
        Brochure.IsDeleted == False
    ).first()

    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")

    # Deactivate all other brochures for this project
    db.query(Brochure).filter(
        Brochure.ProjectName == brochure.ProjectName,
        Brochure.BrochureId != brochure_id,
        Brochure.IsActive == True
    ).update({"IsActive": False, "UpdatedDate": get_time()})

    # Activate this brochure
    brochure.IsActive = True
    brochure.UpdatedDate = get_time()
    brochure.UpdatedById = user.get('user_id')

    db.commit()

    return {
        "message": f"Brochure {brochure_id} activated successfully",
        "project_name": brochure.ProjectName
    }


@router.delete('/delete/{brochure_id}', status_code=status.HTTP_200_OK)
async def delete_brochure(
    user: user_dependency,
    db: db_dependency,
    brochure_id: int
):
    """
    Soft delete a brochure.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    brochure = db.query(Brochure).filter(
        Brochure.BrochureId == brochure_id
    ).first()

    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")

    brochure.IsDeleted = True
    brochure.IsActive = False
    brochure.UpdatedDate = get_time()
    brochure.UpdatedById = user.get('user_id')

    db.commit()

    return {
        "message": f"Brochure {brochure_id} deleted successfully"
    }


@router.get('/{brochure_id}', status_code=status.HTTP_200_OK)
async def get_brochure_by_id(
    user: user_dependency,
    db: db_dependency,
    brochure_id: int
):
    """
    Get a specific brochure by ID with full details.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    brochure = db.query(Brochure).filter(
        Brochure.BrochureId == brochure_id
    ).first()

    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")

    return {
        "brochure_id": brochure.BrochureId,
        "project_name": brochure.ProjectName,
        "site_id": brochure.SiteId,
        "file_name": brochure.FileName,
        "file_path": brochure.FilePath,
        "file_size": brochure.FileSize,
        "structured_data": brochure.StructuredData,
        "raw_text": brochure.RawText,
        "is_active": brochure.IsActive,
        "is_deleted": brochure.IsDeleted,
        "created_date": brochure.CreatedDate,
        "updated_date": brochure.UpdatedDate,
        "created_by_id": brochure.CreatedById,
        "updated_by_id": brochure.UpdatedById
    }

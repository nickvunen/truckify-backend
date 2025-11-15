from datetime import datetime, date
from typing import List, Optional
import os
import shutil

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import Base, Booking, Camper, Attribute, Settings, SessionLocal, engine

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Truckify API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize settings if not exists
def init_settings(db: Session):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
        db.commit()


##### PYDANTIC MODELS #####

class CamperCreate(BaseModel):
    name: str
    license_plate: Optional[str] = None
    price_per_day: float
    color: str = "#3B82F6"
    description: Optional[str] = None
    facilities: Optional[List[str]] = []
    images: Optional[List[str]] = []
    max_passengers: int = 2
    year: Optional[int] = None
    is_active: bool = True


class CamperUpdate(BaseModel):
    name: Optional[str] = None
    license_plate: Optional[str] = None
    price_per_day: Optional[float] = None
    color: Optional[str] = None
    description: Optional[str] = None
    facilities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    max_passengers: Optional[int] = None
    year: Optional[int] = None
    is_active: Optional[bool] = None


class CamperResponse(BaseModel):
    id: int
    name: str
    license_plate: Optional[str]
    price_per_day: float
    color: str
    description: Optional[str]
    facilities: Optional[List[str]]
    images: Optional[List[str]]
    max_passengers: int
    year: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttributeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = 0.0
    is_active: bool = True


class AttributeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    camper_id: int
    start_date: date
    end_date: date
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    customer_message: Optional[str] = None
    selected_attributes: Optional[List[int]] = []


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_message: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    camper_id: int
    start_date: date
    end_date: date
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    customer_message: Optional[str]
    base_price: float
    attributes_price: float
    total_price: float
    selected_attributes: Optional[List[int]]
    status: str
    payment_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    charge_type: Optional[str] = None
    auto_accept_bookings: Optional[bool] = None
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    company_color: Optional[str] = None
    company_logo: Optional[str] = None
    language: Optional[str] = None
    booking_page_language: Optional[str] = None
    minimum_booking_days: Optional[int] = None
    maximum_booking_days: Optional[int] = None


class SettingsResponse(BaseModel):
    id: int
    charge_type: str
    auto_accept_bookings: bool
    business_name: str
    business_email: Optional[str]
    business_phone: Optional[str]
    company_color: str
    company_logo: Optional[str]
    language: str
    booking_page_language: str
    minimum_booking_days: int
    maximum_booking_days: int
    updated_at: datetime

    class Config:
        from_attributes = True


##### CAMPER ENDPOINTS #####

@app.get("/api/campers", response_model=List[CamperResponse])
def get_campers(include_inactive: bool = False, db: Session = Depends(get_db)):
    """Get all campers"""
    query = db.query(Camper)
    if not include_inactive:
        query = query.filter(Camper.is_active == True)
    campers = query.all()
    return campers


@app.get("/api/campers/{camper_id}", response_model=CamperResponse)
def get_camper(camper_id: int, db: Session = Depends(get_db)):
    """Get a specific camper by ID"""
    camper = db.query(Camper).filter(Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    return camper


@app.post("/api/campers", response_model=CamperResponse)
def create_camper(camper: CamperCreate, db: Session = Depends(get_db)):
    """Create a new camper"""
    new_camper = Camper(**camper.model_dump())
    db.add(new_camper)
    db.commit()
    db.refresh(new_camper)
    return new_camper


@app.put("/api/campers/{camper_id}", response_model=CamperResponse)
def update_camper(camper_id: int, camper: CamperUpdate, db: Session = Depends(get_db)):
    """Update a camper"""
    db_camper = db.query(Camper).filter(Camper.id == camper_id).first()
    if not db_camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    update_data = camper.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_camper, key, value)
    
    db_camper.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_camper)
    return db_camper


@app.delete("/api/campers/{camper_id}")
def delete_camper(camper_id: int, db: Session = Depends(get_db)):
    """Delete (deactivate) a camper"""
    camper = db.query(Camper).filter(Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    camper.is_active = False
    db.commit()
    return {"message": "Camper deactivated successfully"}


##### ATTRIBUTE ENDPOINTS #####

@app.get("/api/attributes", response_model=List[AttributeResponse])
def get_attributes(include_inactive: bool = False, db: Session = Depends(get_db)):
    """Get all attributes"""
    query = db.query(Attribute)
    if not include_inactive:
        query = query.filter(Attribute.is_active == True)
    attributes = query.all()
    return attributes


@app.post("/api/attributes", response_model=AttributeResponse)
def create_attribute(attribute: AttributeCreate, db: Session = Depends(get_db)):
    """Create a new attribute"""
    new_attribute = Attribute(**attribute.model_dump())
    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)
    return new_attribute


@app.put("/api/attributes/{attribute_id}", response_model=AttributeResponse)
def update_attribute(attribute_id: int, attribute: AttributeCreate, db: Session = Depends(get_db)):
    """Update an attribute"""
    db_attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not db_attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    
    for key, value in attribute.model_dump().items():
        setattr(db_attribute, key, value)
    
    db.commit()
    db.refresh(db_attribute)
    return db_attribute


@app.delete("/api/attributes/{attribute_id}")
def delete_attribute(attribute_id: int, db: Session = Depends(get_db)):
    """Delete (deactivate) an attribute"""
    attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    
    attribute.is_active = False
    db.commit()
    return {"message": "Attribute deactivated successfully"}


##### BOOKING ENDPOINTS #####

def calculate_booking_price(
    camper: Camper,
    start_date: date,
    end_date: date,
    attribute_ids: List[int],
    db: Session,
    settings: Settings
) -> tuple[float, float, float]:
    """Calculate booking prices"""
    # Calculate number of days/nights
    days_diff = (end_date - start_date).days
    if settings.charge_type == "per_night":
        charge_units = days_diff
    else:  # per_day
        charge_units = days_diff + 1
    
    base_price = camper.price_per_day * charge_units
    
    # Calculate attributes price
    attributes_price = 0.0
    if attribute_ids:
        attributes = db.query(Attribute).filter(Attribute.id.in_(attribute_ids)).all()
        attributes_price = sum(attr.price for attr in attributes) * charge_units
    
    total_price = base_price + attributes_price
    
    return base_price, attributes_price, total_price


@app.get("/api/bookings", response_model=List[BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    """Get all bookings"""
    bookings = db.query(Booking).all()
    return bookings


@app.get("/api/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Get a specific booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@app.post("/api/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """Create a new booking"""
    # Validate camper exists
    camper = db.query(Camper).filter(Camper.id == booking.camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    # Check availability
    overlapping_bookings = db.query(Booking).filter(
        and_(
            Booking.camper_id == booking.camper_id,
            Booking.status.in_(["reserved", "confirmed"]),
            or_(
                and_(Booking.start_date <= booking.start_date, Booking.end_date >= booking.start_date),
                and_(Booking.start_date <= booking.end_date, Booking.end_date >= booking.end_date),
                and_(Booking.start_date >= booking.start_date, Booking.end_date <= booking.end_date)
            )
        )
    ).first()
    
    if overlapping_bookings:
        raise HTTPException(status_code=400, detail="Camper is not available for the selected dates")
    
    # Get settings
    settings = db.query(Settings).first()
    if not settings:
        init_settings(db)
        settings = db.query(Settings).first()
    
    # Calculate prices
    base_price, attributes_price, total_price = calculate_booking_price(
        camper, booking.start_date, booking.end_date, booking.selected_attributes or [], db, settings
    )
    
    # Determine initial status based on settings
    initial_status = "confirmed" if settings.auto_accept_bookings else "reserved"
    
    # Create booking
    new_booking = Booking(
        camper_id=booking.camper_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        customer_name=booking.customer_name,
        customer_email=booking.customer_email,
        customer_phone=booking.customer_phone,
        customer_message=booking.customer_message,
        base_price=base_price,
        attributes_price=attributes_price,
        total_price=total_price,
        selected_attributes=booking.selected_attributes or [],
        status=initial_status,
        payment_status="not_paid"
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


@app.put("/api/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, booking: BookingUpdate, db: Session = Depends(get_db)):
    """Update a booking (mainly for status changes)"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    update_data = booking.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_booking, key, value)
    
    db_booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_booking)
    return db_booking


@app.delete("/api/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """Cancel a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "cancelled"
    db.commit()
    return {"message": "Booking cancelled successfully"}


##### AVAILABILITY ENDPOINT #####

@app.get("/api/availability")
def check_availability(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Check availability of all campers for given date range"""
    campers = db.query(Camper).filter(Camper.is_active == True).all()
    
    availability = []
    for camper in campers:
        # Check for overlapping bookings
        overlapping = db.query(Booking).filter(
            and_(
                Booking.camper_id == camper.id,
                Booking.status.in_(["reserved", "confirmed"]),
                or_(
                    and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
                    and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
                    and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
                )
            )
        ).first()
        
        # Get settings for price calculation
        settings = db.query(Settings).first()
        if not settings:
            init_settings(db)
            settings = db.query(Settings).first()
        
        # Calculate price
        days_diff = (end_date - start_date).days
        if settings.charge_type == "per_night":
            charge_units = days_diff
        else:
            charge_units = days_diff + 1
        
        price = camper.price_per_day * charge_units
        
        availability.append({
            "camper": CamperResponse.model_validate(camper),
            "available": overlapping is None,
            "price": price
        })
    
    return {"availability": availability}


##### SETTINGS ENDPOINTS #####

@app.get("/api/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get business settings"""
    settings = db.query(Settings).first()
    if not settings:
        init_settings(db)
        settings = db.query(Settings).first()
    return settings


@app.put("/api/settings", response_model=SettingsResponse)
def update_settings(settings_data: SettingsUpdate, db: Session = Depends(get_db)):
    """Update business settings"""
    settings = db.query(Settings).first()
    if not settings:
        init_settings(db)
        settings = db.query(Settings).first()
    
    update_data = settings_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    return settings


##### CALENDAR DATA ENDPOINT #####

@app.get("/api/calendar")
def get_calendar_data(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Get all bookings for a specific month for calendar display"""
    from calendar import monthrange
    
    # Get first and last day of the month
    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    # Get all active campers
    campers = db.query(Camper).filter(Camper.is_active == True).all()
    
    # Get all bookings that overlap with this month
    bookings = db.query(Booking).filter(
        and_(
            or_(
                and_(Booking.start_date >= start_date, Booking.start_date <= end_date),
                and_(Booking.end_date >= start_date, Booking.end_date <= end_date),
                and_(Booking.start_date <= start_date, Booking.end_date >= end_date)
            ),
            Booking.status.in_(["reserved", "confirmed", "cancelled"])
        )
    ).all()
    
    return {
        "campers": [CamperResponse.model_validate(c) for c in campers],
        "bookings": [BookingResponse.model_validate(b) for b in bookings]
    }


##### FILE UPLOAD #####

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file (logo, images, etc.)"""
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return URL
        return {"url": f"/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


##### HEALTH CHECK #####

@app.get("/")
def health_check():
    """API health check"""
    return {"status": "healthy", "message": "Truckify API is running"}


# Mount static files (must be last, after all routes!)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

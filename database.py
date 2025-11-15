from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, Float, Boolean, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Camper(Base):
    """Camper/Truck model with all details"""
    __tablename__ = "campers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)  # e.g., "VW California Ocean"
    license_plate = Column(String)
    price_per_day = Column(Float, nullable=False)
    color = Column(String, default="#3B82F6")  # Hex color for calendar display
    description = Column(Text)
    facilities = Column(JSON)  # List of facilities like ["Kitchen", "Shower", "Bed"]
    images = Column(JSON)  # List of image URLs
    max_passengers = Column(Integer, default=2)
    year = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bookings = relationship("Booking", back_populates="camper")


class Attribute(Base):
    """Additional attributes/add-ons that can be added to bookings"""
    __tablename__ = "attributes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)  # e.g., "Porta-Potty"
    description = Column(Text)
    price = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Booking(Base):
    """Booking model with payment status and customer info"""
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    camper_id = Column(Integer, ForeignKey("campers.id"), nullable=False)
    
    # Date information
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Customer information
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String)
    customer_message = Column(Text)
    
    # Pricing
    base_price = Column(Float, nullable=False)
    attributes_price = Column(Float, default=0.0)
    total_price = Column(Float, nullable=False)
    
    # Selected attributes (JSON array of attribute IDs)
    selected_attributes = Column(JSON, default=[])
    
    # Booking status
    status = Column(String, default="reserved")  # reserved, confirmed, cancelled
    payment_status = Column(String, default="not_paid")  # not_paid, partially_paid, paid, refunded
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    camper = relationship("Camper", back_populates="bookings")


class Settings(Base):
    """Business settings for the booking system"""
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Pricing settings
    charge_type = Column(String, default="per_day")  # per_day or per_night
    
    # Booking settings
    auto_accept_bookings = Column(Boolean, default=True)
    
    # Business information
    business_name = Column(String, default="Truckify")
    business_email = Column(String)
    business_phone = Column(String)
    
    # Branding
    company_color = Column(String, default="#3B82F6")  # Primary brand color
    company_logo = Column(String)  # URL to company logo
    
    # Localization
    language = Column(String, default="en")  # en, de, fr, nl, es, pt (Dashboard language)
    booking_page_language = Column(String, default="en")  # Default language for booking page
    
    # Other settings (can be extended)
    minimum_booking_days = Column(Integer, default=1)
    maximum_booking_days = Column(Integer, default=365)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

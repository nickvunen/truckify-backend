from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from database import (
    Base,
    Booking,
    SessionLocal,
    StringItem,
    Truck,
    engine,
    fill_bookings,
    fill_trucks,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for more security
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


##### ROUTERS #####
test_router = APIRouter()
truck_router = APIRouter()
booking_router = APIRouter()
availability_router = APIRouter()


##### TEST ENDPOINTS #####


@test_router.get("/string")
def read_string(db: Session = Depends(get_db)):
    item = db.query(StringItem).first()
    if item:
        return {"result": item.value}
    return {"result": ""}


@test_router.post("/fill_database")
def fill_database(db: Session = Depends(get_db)):
    # Fill the database with some sample data
    fill_trucks(db)
    fill_bookings(db)
    return {"message": "Database filled with sample data"}


##### TRUCK ENDPOINTS #####


# Define a Pydantic model for Truck response
class TruckResponse(BaseModel):
    license: str
    price_per_day: int
    level: str
    image: str

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models


@truck_router.get("/{truck_id}")
def get_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if truck:
        return {"truck": truck}
    return {"error": "Truck not found"}


@truck_router.get("/")
def get_trucks(db: Session = Depends(get_db)):
    trucks = db.query(Truck).all()
    return {"trucks": trucks}


@truck_router.post("/truck", response_model=TruckResponse)
def create_truck(truck: TruckResponse, db: Session = Depends(get_db)):
    new_truck = Truck(**truck.model_dump())
    db.add(new_truck)
    db.commit()
    db.refresh(new_truck)
    return new_truck


@truck_router.delete("/{truck_id}")
def delete_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if truck:
        db.delete(truck)
        db.commit()
        return {"message": "Truck deleted"}
    return {"error": "Truck not found"}


# ##### BOOKING ENDPOINTS #####

COST_PORTA_POTTI = 60
COST_CLEANING_SERVICE = 75


class BookingResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    email: str
    truck_id: int
    porta_potti: bool = False
    cleaning_service: bool = False

    class Config:
        from_attributes = True


@booking_router.get("/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        return {"booking": booking}
    return {"error": "Booking not found"}


@booking_router.get("/")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return {"bookings": bookings}


@booking_router.post("/booking")
def create_booking(booking: BookingResponse, db: Session = Depends(get_db)):
    new_booking = Booking(**booking.model_dump())

    # Check that the start_date and end_date are at least three days apart
    if (booking.end_date - booking.start_date).days < 3:
        return {"error": "Booking must be at least 3 days long"}

    price = db.query(Truck.price_per_day).filter(Truck.id == booking.truck_id).first()
    if price:
        new_booking.total_price = (
            price[0] * (booking.end_date - booking.start_date).days
        )
        if booking.porta_potti:
            new_booking.total_price += COST_PORTA_POTTI
        if booking.cleaning_service:
            new_booking.total_price += COST_CLEANING_SERVICE
    else:
        return {"error": "Truck not found"}

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {"booking": new_booking}


@booking_router.put("/paid/{booking_id}")
def put_booking_paid(booking_id: int, paid: bool, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.paid = paid
        db.commit()
        return {"message": "Booking updated"}
    return {"error": "Booking not found"}


@booking_router.put("/confirm/{booking_id}")
def put_booking_confirm(
    booking_id: int, confirmed: bool, db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.confirmed = confirmed
        db.commit()
        return {"message": "Booking updated"}
    return {"error": "Booking not found"}


@booking_router.delete("/{booking_id}")
def delete_booking(booking_id: int, confirmed: bool, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.confirmed = confirmed
        db.commit()
        return {"message": "Booking deleted"}
    return {"error": "Booking not found"}


##### TRUCK AVAILABILITY ENDPOINTS #####


class TruckAvailabilityResponse(BaseModel):
    start: datetime
    end: datetime


@availability_router.post("/trucks_available")
def post_available_trucks(
    truck_availability: TruckAvailabilityResponse, db: Session = Depends(get_db)
):
    start_date = truck_availability.start
    end_date = truck_availability.end

    # Query to find all trucks that are not booked during the specified period
    available_trucks = (
        db.query(Truck)
        .outerjoin(Booking)
        .filter(and_(Booking.start_date > end_date, Booking.end_date < start_date))
        .all()
    )

    # Query to find all trucks that are booked but are near the end of their booking period
    buffer_period = timedelta(days=3)
    proposed_trucks = (
        db.query(Truck)
        .outerjoin(Booking)
        .filter(
            and_(
                Booking.start_date >= start_date - buffer_period,
                Booking.start_date < end_date,
                Booking.end_date <= end_date + buffer_period,
                Booking.end_date > start_date,
            )
        )
        .all()
    )

    return {"available_trucks": available_trucks, "proposed_trucks": proposed_trucks}


app.include_router(test_router, prefix="/test", tags=["test"])
app.include_router(truck_router, prefix="/trucks", tags=["trucks"])
app.include_router(booking_router, prefix="/bookings", tags=["bookings"])
app.include_router(availability_router, prefix="/availability", tags=["availability"])

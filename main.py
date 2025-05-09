from datetime import datetime

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, Booking, SessionLocal, StringItem, Truck, engine

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


##### STRING ENDPOINTS #####


@app.get("/string")
def read_string(db: Session = Depends(get_db)):
    item = db.query(StringItem).first()
    if item:
        return {"result": item.value}
    return {"result": ""}


##### TRUCK ENDPOINTS #####


# Define a Pydantic model for Truck response
class TruckResponse(BaseModel):
    license: str
    price_per_day: int
    level: str
    image: str

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models


@app.get("/trucks/{truck_id}")
def get_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if truck:
        return {"truck": truck}
    return {"error": "Truck not found"}


@app.get("/trucks")
def get_trucks(db: Session = Depends(get_db)):
    trucks = db.query(Truck).all()
    return {"trucks": trucks}


@app.post("/trucks", response_model=TruckResponse)
def create_truck(truck: TruckResponse, db: Session = Depends(get_db)):
    new_truck = Truck(**truck.model_dump())
    db.add(new_truck)
    db.commit()
    db.refresh(new_truck)
    return new_truck


# ##### BOOKING ENDPOINTS #####


class BookingResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    email: str
    truck_id: int

    class Config:
        from_attributes = True


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        return {"booking": booking}
    return {"error": "Booking not found"}


@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return {"bookings": bookings}


@app.post("/bookings")
def create_booking(booking: BookingResponse, db: Session = Depends(get_db)):
    new_booking = Booking(**booking.model_dump())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {"booking": new_booking}

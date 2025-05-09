from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StringItem(Base):
    __tablename__ = "strings"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, index=True)


class Truck(Base):
    __tablename__ = "trucks"
    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    license = Column(String, nullable=False)
    price_per_day = Column(Integer, nullable=False)
    level = Column(String)
    image = Column(String)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    email = Column(String)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    total_price = Column(Integer)
    paid = Column(Boolean, default=False)
    confirmed = Column(Boolean, default=False)


def fill_trucks(db):
    # Fill the database with some sample trucks
    sample_trucks = [
        Truck(
            license="ABC123",
            price_per_day=100,
            level="Standard",
            image="https://www.truckcamperadventure.com/wp-content/uploads/2023/07/BCR-Front-3_4-scaled.jpeg",
        ),
        Truck(
            license="XYZ789",
            price_per_day=150,
            level="Luxury",
            image="https://www.trucks.nl/img/956c5ad21d93b4887f80573cdf80d775/motorhome_camper_scania_g410_xt_4x4_fully_equipped_expedition_truck_2023_8114190.jpg??width=2220&height=1664&quality=70",
        ),
        Truck(
            license="LMN456",
            price_per_day=120,
            level="Standard",
            image="https://images.squarespace-cdn.com/content/v1/5a150361c027d861562cd5cd/1707784454333-X67T8T6SNWEEKSSJJVDU/Copy+of+Swissliner+Auto-41.jpg?format=1500w",
        ),
    ]
    db.add_all(sample_trucks)
    db.commit()


def fill_bookings(db):
    # Fill the database with some sample bookings
    sample_bookings = [
        Booking(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 10),
            email="gayguy@hotmail.com",
            truck_id=1,
            total_price=500,
            paid=True,
            confirmed=True,
        ),
        Booking(
            start_date=date(2025, 4, 1),
            end_date=date(2025, 5, 10),
            email="hetroguy@hotmail.com",
            truck_id=2,
            total_price=600,
            paid=True,
            confirmed=False,
        ),
        Booking(
            start_date=date(2025, 6, 15),
            end_date=date(2025, 6, 20),
            email="example@example.com",
            truck_id=3,
            total_price=700,
            paid=False,
            confirmed=True,
        ),
        Booking(
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 10),
            email="test@test.com",
            truck_id=1,
            total_price=800,
            paid=True,
            confirmed=True,
        ),
        Booking(
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 10),
            email="user@example.com",
            truck_id=2,
            total_price=900,
            paid=False,
            confirmed=False,
        ),
    ]
    db.add_all(sample_bookings)
    db.commit()

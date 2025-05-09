from sqlalchemy import Column, Date, ForeignKey, Integer, String, create_engine
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

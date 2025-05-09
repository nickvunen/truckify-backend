from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, StringItem

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

@app.get("/string")
def read_string(db: Session = Depends(get_db)):
    item = db.query(StringItem).first()
    if item:
        return {"result": item.value}
    return {"result": ""}

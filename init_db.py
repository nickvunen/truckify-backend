# Script to initialize the database with a sample string

from database import SessionLocal, Base, engine, StringItem

def init():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(StringItem).count() == 0:
        db.add(StringItem(value="Hello from the database!"))
        db.commit()
    db.close()

if __name__ == "__main__":
    init()

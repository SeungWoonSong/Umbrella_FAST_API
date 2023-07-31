from fastapi import FastAPI, HTTPException, Depends
from backend import schemas, models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/borrow_umbrella/")
def borrow_umbrella(umbrella: schemas.BorrowUmbrellaSchema, db: SessionLocal = Depends(get_db)):
    db_umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella.umbrella_id).first()
    if db_umbrella is None:
        raise HTTPException(status_code=404, detail="Umbrella not found")
    elif db_umbrella.status == 'borrowed':
        raise HTTPException(status_code=400, detail="Umbrella is already borrowed")
    else:
        db_umbrella.status = 'borrowed'
        db_umbrella.owner_id = umbrella.user_id
        db.commit()
        return db_umbrella

@app.post("/return_umbrella/")
def return_umbrella(umbrella: schemas.ReturnUmbrellaSchema, db: SessionLocal = Depends(get_db)):
    db_umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella.umbrella_id).first()
    if db_umbrella is None:
        raise HTTPException(status_code=404, detail="Umbrella not found")
    elif db_umbrella.status == 'available':
        raise HTTPException(status_code=400, detail="Umbrella is not borrowed")
    else:
        db_umbrella.status = 'available'
        db_umbrella.owner_id = None
        db.commit()
        return db_umbrella

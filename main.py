from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.params import Depends
from sqlalchemy.orm import Session
from schemas import ItemCreate, Item, ItemUpdate
from databases import SessionLocal, engine
from models import DBItem, Base
from typing import List
app = FastAPI()


# Now we connect the tamplates folder to the main file for the views to rander.

tamplates=Jinja2Templates(directory="tamplates")

# Dependency to get the database session.
def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
# This is our first route to display the user that the server is working 
# ("/") means home route
# response_class= HTMLResponse means the response will be in Html it can be in json as well
# "root" is the function name for logic
#
@app.get("/",response_class=HTMLResponse)
def root(request: Request):
     # return "pakistan"
     return tamplates.TemplateResponse(request=request,name="home.html")

@app.get("/items")
async def get_all_items(db: Session = Depends(get_db)) -> List[Item]:
    db_items = db.query(DBItem)
    result = []
    for item in db_items:
        result.append(Item(**item.__dict__))
    return result

@app.post("/items")
def create_item(item: ItemCreate, db: Session = Depends(get_db)) -> Item:
    db_item = DBItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return Item(**db_item.__dict__)


@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(**db_item.__dict__)


@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return Item(**db_item.__dict__)


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return Item(**db_item.__dict__)
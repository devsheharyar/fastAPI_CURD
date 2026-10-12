from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.params import Depends
from sqlalchemy.orm import Session
from schemas import ItemCreate, Item, ItemUpdate
from databases import SessionLocal, engine
from models import DBItem, Base
app = FastAPI()


# Now we connect the tamplates folder to the main file for the views to rander.

tamplates=Jinja2Templates(directory="tamplates")

# to add css in the fast api we should mount the staticFiles directory and place the css and images files in it.

app.mount("/static", StaticFiles(directory="static"), name="static2")

# • app.mount(...): This attaches an independent sub-application (powered by Starlette) to your main FastAPI app to handle a specific URL prefix.
# • "/static": This is the URL path in the browser. Any request starting with http://your-domain/static/... will look inside this mounted directory.
# • StaticFiles(...): This is the helper class imported from fastapi.staticfiles that handles reading and streaming files from your disk.
# • directory="static": This is the actual folder name on your computer's hard drive (relative to where you run your Python command) where your files are stored.
# • name="static": This is the internal identifier used by FastAPI. It allows you to generate dynamic URLs in your HTML templates using request.url_for("static", path="/style.css")


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
@app.get("/")
def root(request1: Request):
     # return "pakistan"
     return tamplates.TemplateResponse(request=request1,name="home.html")

@app.get("/allitems")
async def get_all_items(request: Request, db: Session = Depends(get_db)):
    db_items = db.query(DBItem).all()
    return tamplates.TemplateResponse(
        request=request,
        name="allItems.html",
        context={"db_items": db_items},
    )

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
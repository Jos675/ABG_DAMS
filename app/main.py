from fastapi import FastAPI, Request, Depends, Form, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import database, models, crud, schemas
from app.routers.api import router as api_router, get_current_user
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from decouple import config
import os
import uuid
from PIL import Image
import aiofiles

app = FastAPI(title="DAM System", description="Digital Asset Management System")

app.add_middleware(SessionMiddleware, secret_key=config("SECRET_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
def create_tables():
    database.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = crud.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user_id"] = user.id
    return RedirectResponse(url="/assets", status_code=303)

def get_current_user_web(request: Request, db: Session = Depends(database.get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/assets")
def assets_page(request: Request, current_user: models.User = Depends(get_current_user_web), db: Session = Depends(database.get_db)):
    assets = crud.get_assets(db=db, user=current_user, skip=0, limit=100)
    return templates.TemplateResponse("assets.html", {"request": request, "assets": assets, "user": current_user})

@app.get("/upload")
def upload_form(request: Request, current_user: models.User = Depends(get_current_user_web)):
    return templates.TemplateResponse("upload.html", {"request": request, "user": current_user})

@app.post("/upload")
async def upload_asset_web(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    tags: str = Form(None),
    classification: str = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user_web),
    db: Session = Depends(database.get_db)
):
    tag_list = [t.strip() for t in tags.split(',')] if tags else None
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = str(uuid.uuid4()) + file_extension
    file_path = os.path.join("uploads", unique_filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    thumbnail_path = None
    if file.content_type.startswith('image/'):
        thumbnail_filename = str(uuid.uuid4()) + "_thumb.jpg"
        thumbnail_path = os.path.join("uploads", thumbnail_filename)
        image = Image.open(file_path)
        image.thumbnail((200, 200))
        image.save(thumbnail_path)
    asset_data = schemas.AssetCreate(
        title=title,
        description=description,
        tags=tag_list,
        classification=schemas.Classification(classification)
    )
    asset = crud.create_asset(
        db=db,
        asset=asset_data,
        file_path=file_path,
        filename=unique_filename,
        original_filename=file.filename,
        file_type=file.content_type,
        size=len(content),
        owner_id=current_user.id
    )
    crud.log_action(db, current_user.id, "upload", asset.id, f"Uploaded {file.filename}")
    return RedirectResponse(url="/assets", status_code=303)

@app.get("/reports")
def reports_page(request: Request, current_user: models.User = Depends(get_current_user_web), db: Session = Depends(database.get_db)):
    assets = crud.get_assets(db=db, user=current_user, skip=0, limit=100)
    return templates.TemplateResponse("reports.html", {"request": request, "assets": assets, "user": current_user})

@app.get("/settings")
def settings_page(request: Request, current_user: models.User = Depends(get_current_user_web)):
    return templates.TemplateResponse("settings.html", {"request": request, "user": current_user})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/download/{asset_id}")
def download_asset_web(asset_id: int, request: Request, current_user: models.User = Depends(get_current_user_web), db: Session = Depends(database.get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not crud.can_access_asset(asset, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    crud.log_action(db, current_user.id, "download", asset.id)
    from fastapi.responses import FileResponse
    return FileResponse(asset.file_path, media_type=asset.file_type, filename=asset.original_filename)
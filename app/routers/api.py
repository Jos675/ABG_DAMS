from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import database, models, schemas, crud
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from decouple import config
from typing import List
from datetime import timedelta
import os
import uuid
from PIL import Image
import aiofiles
from fastapi.responses import FileResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.post("/upload/")
async def upload_asset(
    title: str = Form(...),
    description: str = Form(None),
    tags: str = Form(None),  # comma separated
    classification: str = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # Parse tags
    tag_list = [t.strip() for t in tags.split(',')] if tags else None

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = str(uuid.uuid4()) + file_extension
    file_path = os.path.join("uploads", unique_filename)

    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Generate thumbnail if image
    thumbnail_path = None
    if file.content_type.startswith('image/'):
        thumbnail_filename = str(uuid.uuid4()) + "_thumb.jpg"
        thumbnail_path = os.path.join("uploads", thumbnail_filename)
        image = Image.open(file_path)
        image.thumbnail((200, 200))
        image.save(thumbnail_path)

    # Create asset
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

    # Log action
    crud.log_action(db, current_user.id, "upload", asset.id, f"Uploaded {file.filename}")

    return {"message": "Asset uploaded successfully", "asset_id": asset.id}

@router.get("/assets/", response_model=List[schemas.Asset])
def read_assets(skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    assets = crud.get_assets(db=db, user=current_user, skip=skip, limit=limit)
    return assets

@router.get("/assets/{asset_id}", response_model=schemas.Asset)
def read_asset(asset_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    # Check permission
    if not can_access_asset(asset, current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    return asset

def can_access_asset(asset: models.Asset, user: models.User, db: Session = Depends(database.get_db)):
    return crud.can_access_asset(asset, user, db)

@router.get("/download/{asset_id}")
def download_asset(asset_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset or not can_access_asset(asset, current_user):
        raise HTTPException(status_code=404, detail="Asset not found or not authorized")
    crud.log_action(db, current_user.id, "download", asset.id)
    return FileResponse(asset.file_path, media_type=asset.file_type, filename=asset.original_filename)
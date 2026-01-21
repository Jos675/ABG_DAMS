from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from decouple import config
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["scrypt"], deprecated="auto")

SECRET_KEY = config("SECRET_KEY", default="your-secret-key-here-change-in-production")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_assets(db: Session, user: models.User, skip: int = 0, limit: int = 100):
    # Basic permission check: PUBLIC always, REGULAR if authenticated, CONFIDENTIAL if admin or assigned
    query = db.query(models.Asset)
    if user.role != models.Role.admin:
        # Filter based on classification and access
        public_assets = query.filter(models.Asset.classification == models.Classification.public)
        regular_assets = query.filter(models.Asset.classification == models.Classification.regular)
        confidential_assets = db.query(models.Asset).join(models.AssetAccess).filter(
            models.Asset.classification == models.Classification.confidential,
            models.AssetAccess.user_id == user.id,
            models.AssetAccess.can_access == True
        )
        query = public_assets.union(regular_assets).union(confidential_assets)
    return query.offset(skip).limit(limit).all()

def create_asset(db: Session, asset: schemas.AssetCreate, file_path: str, filename: str, original_filename: str, file_type: str, size: int, owner_id: int):
    db_asset = models.Asset(
        title=asset.title,
        description=asset.description,
        tags=asset.tags,
        classification=asset.classification,
        file_path=file_path,
        filename=filename,
        original_filename=original_filename,
        file_type=file_type,
        size=size,
        owner_id=owner_id
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def can_access_asset(asset: models.Asset, user: models.User, db: Session):
    if asset.classification == models.Classification.public:
        return True
    if asset.classification == models.Classification.regular and user.is_active:
        return True
    if asset.classification == models.Classification.confidential:
        if user.role == models.Role.admin:
            return True
        # Check overrides
        access = db.query(models.AssetAccess).filter(
            models.AssetAccess.asset_id == asset.id,
            models.AssetAccess.user_id == user.id,
            models.AssetAccess.can_access == True
        ).first()
        return access is not None
    return False
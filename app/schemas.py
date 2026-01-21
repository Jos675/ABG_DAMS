from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models import Role, Classification

class UserBase(BaseModel):
    username: str
    email: str
    role: Role = Role.viewer

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AssetBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    classification: Classification = Classification.regular

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    filename: str
    original_filename: str
    file_path: str
    thumbnail_path: Optional[str]
    file_type: str
    size: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AssetMetadataBase(BaseModel):
    key: str
    value: str

class AssetMetadata(AssetMetadataBase):
    id: int
    asset_id: int

    class Config:
        from_attributes = True

class AuditLogBase(BaseModel):
    action: str
    details: Optional[str] = None

class AuditLog(AuditLogBase):
    id: int
    user_id: int
    asset_id: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True
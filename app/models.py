from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class Role(enum.Enum):
    admin = "admin"
    archivist = "archivist"
    regular = "regular"
    viewer = "viewer"

class Classification(enum.Enum):
    public = "public"
    regular = "regular"
    confidential = "confidential"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(Role), default=Role.viewer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assets = relationship("Asset", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_filename = Column(String)
    file_path = Column(String)
    thumbnail_path = Column(String, nullable=True)
    file_type = Column(String)
    size = Column(Integer)
    classification = Column(Enum(Classification), default=Classification.regular)
    title = Column(String)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # list of strings
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="assets")
    custom_metadata = relationship("AssetMetadata", back_populates="asset")
    access_overrides = relationship("AssetAccess", back_populates="asset")
    audit_logs = relationship("AuditLog", back_populates="asset")

class AssetMetadata(Base):
    __tablename__ = "asset_metadata"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    key = Column(String)
    value = Column(String)

    asset = relationship("Asset", back_populates="custom_metadata")

class AssetAccess(Base):
    __tablename__ = "asset_access"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    can_access = Column(Boolean, default=True)

    asset = relationship("Asset", back_populates="access_overrides")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    action = Column(String)  # upload, download, edit, delete
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)

    user = relationship("User", back_populates="audit_logs")
    asset = relationship("Asset", back_populates="audit_logs")
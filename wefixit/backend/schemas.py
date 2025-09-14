# backend/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

# ----------------------------
# ObjectId Handling
# ----------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):  # For Pydantic v2
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, _handler):
        return {"type": "string"}


# ----------------------------
# Admin User Schema
# ----------------------------
class AdminUserSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    password_hash: str
    is_superuser: bool = True

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True
    )


# ----------------------------
# Review Schemas
# ----------------------------
class ReviewSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    projectType: Optional[str] = None
    rating: float
    comment: str = Field(..., alias="message")
    published: bool = True
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True
    )


# ----------------------------
# Portfolio Schemas
# ----------------------------
class PortfolioBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, alias="image")  # Accept "image" from frontend
    link: Optional[str] = None
    tags: List[str] = []
    is_featured: bool = False
    is_active: bool = True

    model_config = ConfigDict(
        populate_by_name=True
    )


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio item"""
    pass


class PortfolioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, alias="image")
    link: Optional[str] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        populate_by_name=True
    )


class PortfolioOut(PortfolioBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True
    )


# backend/models.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

# Helper for ObjectId fields with Pydantic v2 syntax
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
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
        return JsonSchemaValue(type='string')

# Admin User
class AdminUser(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    password_hash: str
    is_superuser: bool = True

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )

# Review
class Review(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    rating: float  # 1–5, halves allowed
    comment: str
    published: bool = True
    created_at: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )

# Portfolio Item
class PortfolioItem(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    image_url: Optional[str] = None
    link: Optional[str] = None
    tags: Optional[List[str]] = []
    is_featured: bool = False
    is_active: bool = True
    created_at: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )
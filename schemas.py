"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    subtitle: Optional[str] = Field(None, description="Short tagline")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    currency: str = Field("USD", description="Currency code")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    in_stock: bool = Field(True, description="Whether product is in stock")
    sku: Optional[str] = Field(None, description="Stock keeping unit")
    limited_drop: bool = Field(False, description="Is part of a limited drop")
    units_per_case: Optional[int] = Field(None, description="Units included per case")

class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str
    email: EmailStr
    shipping_address: str
    items: List[OrderItem]
    total: float = Field(..., ge=0)
    note: Optional[str] = None

class Subscriber(BaseModel):
    """
    Subscribers collection schema for limited drop notifications
    Collection name: "subscriber"
    """
    email: EmailStr
    source: Optional[str] = Field(None, description="Where the subscriber came from")

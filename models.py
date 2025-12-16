from pydantic import BaseModel, Field
from typing import Optional


class Product(BaseModel):
    """Product model for API responses"""
    product_name: str = Field(..., description="Name of the product")
    price: float = Field(..., description="Price of the product")
    image_url: str = Field(..., description="URL of the product image")
    product_url: str = Field(..., description="URL of the product page")
    store: str = Field(..., description="Store name (e.g., 'disco', 'fravega')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Sample Product",
                "price": 29.99,
                "image_url": "https://example.com/image.jpg",
                "product_url": "https://example.com/product/sample-product",
                "store": "disco"
            }
        }


class ProductResponse(BaseModel):
    """Response model for products endpoint"""
    products: list[Product]
    count: int

class ScrapeRequest(BaseModel):
    search_term: str

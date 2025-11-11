from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Product, ProductResponse
from database import db
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to SQLite
    print("🚀 Starting FastAPI application...")
    if not db.connect():
        print("⚠ Warning: Failed to connect to SQLite")
    yield
    # Shutdown: Close SQLite connection
    print("👋 Shutting down FastAPI application...")
    db.close()


# Initialize FastAPI app
app = FastAPI(
    title="Product Scraper API",
    description="API for accessing scraped e-commerce product data",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Product Scraper API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/v1/products", response_model=ProductResponse)
async def get_products():
    """
    Retrieve all scraped products from SQLite
    
    Returns:
        ProductResponse: List of products with count
    """
    try:
        products_data = db.get_all_products()
        
        # Validate and convert to Pydantic models
        products = [Product(**product) for product in products_data]
        
        return ProductResponse(
            products=products,
            count=len(products)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@app.post("/api/v1/scrape")
async def trigger_scrape():
    """
    Manually trigger the scraping process
    
    Returns:
        dict: Status message and count of scraped products
    """
    try:
        from scraper import ProductScraper
        
        url = os.getenv("SCRAPE_URL", "https://www.disco.com.ar/bebidas")
        scraper = ProductScraper(url, max_products=20)
        
        # Scrape products
        products, error = scraper.scrape()
        
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        
        # db.clear_products()
        count = db.insert_products(products)
        
        return {
            "message": "Scraping completed successfully",
            "products_scraped": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

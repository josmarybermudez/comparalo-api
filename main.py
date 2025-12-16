from fastapi import FastAPI, HTTPException, BackgroundTasks
from tasks import run_multi_store_scraper_task
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Product, ProductResponse
from database import db
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from models import Product, ProductResponse, ScrapeRequest # <-- IMPORT ScrapeRequest
from tasks import run_multi_store_scraper_task

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


@app.post("/api/v1/scrape")
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks): # <-- ADD request BODY
    """
    Triggers the multi-store scraping process as a background task.
    """
    
    # 1. Input validation (FastAPI does this automatically, but a quick check is good)
    if not request.search_term or len(request.search_term.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search term cannot be empty.")

    term = request.search_term.strip()

    # 2. Add the synchronous scraping function to the background
    # Pass the search term from the request body.
    background_tasks.add_task(run_multi_store_scraper_task, term)
    
    # 3. Immediately return 200 OK or 202 Accepted status
    return {
        "message": "Multi-store scraping initiated successfully in the background.",
        "search_term": term,
        "next_action": "Check the /api/v1/products endpoint shortly for results."
    }
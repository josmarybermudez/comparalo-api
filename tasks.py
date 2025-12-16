# tasks.py (New File)

import os
import importlib
from database import db
from dotenv import load_dotenv

# Ensure environment variables are loaded in the background task context
load_dotenv() 

STORE_SCRAPERS = {
    "disco": "scraper_disco",     
    "jumbo": "scraper_jumbo",
    "fravega": "scraper_fravega",
    "coto": "scraper_coto",
    "vea": "scraper_vea"
}

def run_multi_store_scraper_task(search_term: str):
    """
    Synchronous function to perform the scraping for a given term across all stores.
    """
    print(f"🤖 Starting multi-store background scrape for term: **{search_term}**")
    
    total_products_scraped = 0
    
    for store_name, module_name in STORE_SCRAPERS.items():
        try:
            # 1. Dynamically import the specific scraper module (e.g., scraper_disco)
            scraper_module = importlib.import_module(module_name)
            
            # 2. Get the specific Scraper class from the module (e.g., DiscoScraper)
            # ASSUMPTION: The scraper class is named 'ProductScraper' in all modules.
            ScraperClass = getattr(scraper_module, 'ProductScraper')

            print(f"\n--- Running: {store_name.upper()} ---")
            
            # Initialize scraper with the search term
            # ASSUMPTION: Your scraper constructor accepts a search term.
            scraper = ScraperClass(search_term=search_term, max_products=20) 
            products, error = scraper.scrape()
            
            if error:
                print(f"❌ Scrape failed for {store_name}: {error}")
                continue
            
            if not products:
                print(f"⚠️ No products found for {store_name}.")
                continue

            # 3. CRITICAL FIX: Pass the 'store_name' argument to the database function
            count = db.insert_products(products, store=store_name)
            total_products_scraped += count
            
            print(f"✅ {store_name.upper()} completed. Inserted {count} products.")

        except ImportError:
            print(f"🔥 Error: Could not find module: {module_name}. Skipping {store_name}.")
        except AttributeError:
             print(f"🔥 Error: 'ProductScraper' class not found in {module_name}. Skipping {store_name}.")
        except Exception as e:
            print(f"🔥 Critical error during scrape for {store_name}: {e}")

    print(f"\n🎉 Multi-Store Scrape finished. Total products inserted: {total_products_scraped}")

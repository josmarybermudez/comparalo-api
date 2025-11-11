#!/usr/bin/env python3
"""
Unified scraper runner - Choose which store to scrape from
"""
import sys
# Define available stores and their corresponding default search terms
AVAILABLE_STORES = {
    "disco": "bebidas",
    "fravega": "freidora",
    "jumbo": "lacteos" # Assuming Jumbo is now properly supported
}


def print_usage():
    """Print usage instructions"""
    store_list = "\n".join(
        [f"  {store:9} - {details}" for store, details in [
            ("disco", "Disco.com.ar (Argentine supermarket)"),
            ("fravega", "Fravega.com (Argentine electronics retailer)"),
            ("jumbo", "Jumbo.com.ar (Argentine supermarket) - *Needs implementation in scraper.py*")
        ]]
    )
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              Web Scraper - Multi-Store Support               ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  python run_scraper.py <store> <search_term>
  python run_scraper.py all <search_term>  (Run all available stores)

Stores:
{store_list}

Examples:
  python run_scraper.py disco bebidas
  python run_scraper.py fravega monitor
  python run_scraper.py all notebook       <-- NEW: Runs Disco, Fravega, Jumbo for 'notebook'
  python run_scraper.py disco notebook
    """)


def run_single_scraper(store, search_term):
    """Function to call the specific scraper for a given store"""
    print(f"\n========================================================")
    print(f"🏪 Running Scraper for Store: **{store.upper()}**")
    print(f"🔍 Search Term: **{search_term}**")
    print(f"========================================================")
    
    # Import the appropriate scraper module and run it
    if store == "disco":
        try:
            from scraper import run_scraper
            run_scraper(search_term)
        except ImportError:
            print(f"✗ ERROR: Could not import 'run_scraper' from `scraper.py`.")
    elif store == "jumbo":
        try:
            from scraper_jumbo import run_scraper
            run_scraper(search_term)
        except ImportError:
            print(f"✗ ERROR: Could not import 'run_scraper' from `scraper_jumbo.py`.")
    elif store == "fravega":
        try:
            from scraper_fravega import run_scraper
            run_scraper(search_term)
        except ImportError:
            print(f"✗ ERROR: Could not import 'run_scraper' from `scraper_fravega.py`.")
    else:
        print(f"✗ Internal Error: Scraper not defined for store: {store}")


def main():
    """Main entry point for the scraper"""
    
    # --- Argument Parsing ---
    if len(sys.argv) < 2:
        print("⚠ No store specified, using default: disco bebidas\n")
        store_to_run = "disco"
        search_term = AVAILABLE_STORES.get(store_to_run)
    elif sys.argv[1] in ['--help', '-h', 'help']:
        print_usage()
        return
    else:
        store_to_run = sys.argv[1].lower()
        search_term = sys.argv[2] if len(sys.argv) > 2 else None

    # --- "Run All" Logic ---
    if store_to_run == 'all':
        if not search_term:
            # If 'all' is used without a search term, default to a general one
            search_term = "notebook" 
            print(f"⚠ No search term specified for 'all', using default: **{search_term}**")
            
        print(f"\n🚀 **Running ALL {len(AVAILABLE_STORES)} Scrapers** for search term: **{search_term}**")
        
        for store in AVAILABLE_STORES.keys():
            run_single_scraper(store, search_term)
        
        print("\n✅ All scraper runs completed.")
        return

    # --- Single Store Logic ---
    
    # 1. Validate store
    if store_to_run not in AVAILABLE_STORES:
        print(f"✗ Invalid store: {store_to_run}")
        print(f"  Valid options: {', '.join(AVAILABLE_STORES.keys())} or **all**\n")
        print_usage()
        sys.exit(1)
    
    # 2. Set default search terms if not provided
    if not search_term:
        search_term = AVAILABLE_STORES.get(store_to_run)
        print(f"⚠ No search term provided for {store_to_run}, using default: **{search_term}**\n")

    # 3. Run the selected scraper
    run_single_scraper(store_to_run, search_term)


if __name__ == "__main__":
    main()
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re
import sys

# Define the expected structure for the final product data
# NOTE: You'll need to define this Product type in your actual TypeScript/Python environment
# For simplicity here, we'll use Dict, but good practice is to use TypedDict or dataclasses.
# Final product keys: product_name, price, image_url, product_url, store

class ProductScraper:
    """Web scraper for Fravega.com product data, prioritizing JSON-LD."""
    
    def __init__(self, search_term: str = "freidora", max_products: int = 20):
        self.search_term = search_term
        self.url = f"https://www.fravega.com/l/?keyword={search_term}"
        self.max_products = max_products
        self.base_url = "https://www.fravega.com"
        self.headers = {
            # Use a standard, non-bot User-Agent for better success
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def scrape(self) -> tuple[List[Dict], Optional[str]]:
        """
        Scrape product data from Fravega.com
        """
        try:
            print(f"🔍 Scraping products for '{self.search_term}' from: {self.url}")
            
            # Fetch the page
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Save response for debugging
            # with open('debug_fravega_response.html', 'w', encoding='utf-8') as f:
            #     f.write(response.text)
            # print(f"📄 Saved response to debug_fravega_response.html (size: {len(response.text)} chars)")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract products (JSON-LD first, then HTML fallback)
            products = self._extract_data(soup)
            
            if not products:
                return [], "No products found. Page structure may have changed or search failed."
            
            # Limit to max_products
            products = products[:self.max_products]
            
            print(f"✓ Successfully scraped {len(products)} products")
            return products, None
            
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"✗ {error_msg}")
            return [], error_msg
        except Exception as e:
            error_msg = f"Error during scraping: {str(e)}"
            print(f"✗ {error_msg}")
            return [], error_msg

    # ------------------------------------------------------------------------
    # 🎯 PRIMARY EXTRACTION METHOD (JSON-LD)
    # ------------------------------------------------------------------------
    
    def _extract_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Attempts JSON-LD extraction first, falls back to HTML."""
        products = []
        
        # 1. Look for the JSON-LD script tag
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        
        if script_tag:
            try:
                json_content = script_tag.string
                data = json.loads(json_content)
                
                # Navigate to the list of products (common structures)
                product_items = []
                if isinstance(data, list):
                    product_items = data
                elif isinstance(data, dict):
                    if 'itemListElement' in data:
                        product_items = data['itemListElement']
                    elif 'mainEntity' in data and 'itemListElement' in data['mainEntity']:
                        product_items = data['mainEntity']['itemListElement']

                print(f"📦 Found {len(product_items)} product items via JSON-LD")
                
                # Map the JSON-LD data
                for item in product_items:
                    # Get the actual product object (often nested in 'item')
                    product_json = item.get('item', item) if isinstance(item, dict) else item
                    
                    if isinstance(product_json, dict) and product_json.get('@type') in ['Product', 'Offer']:
                        product_data = self._map_json_to_product(product_json)
                        if product_data:
                            products.append(product_data)

            except json.JSONDecodeError:
                print("❌ JSON Decode Error. Falling back to HTML parsing.")
            except Exception as e:
                print(f"⚠ JSON-LD extraction failed: {e}. Falling back to HTML parsing.")
        
        if products:
            return products
        
        # 2. FALLBACK to HTML parsing if JSON-LD fails or is empty
        print("↪ JSON-LD failed or empty. Attempting HTML fallback...")
        return self._extract_from_html_fallback(soup)

    def _map_json_to_product(self, data: Dict) -> Optional[Dict]:
        """Maps Schema.org Product/Offer JSON data to the desired output format."""
        
        product_name = data.get('name', '')
        product_url = data.get('url', '')
        
        # Extract Offer and Price
        offer = data.get('offers')
        if isinstance(offer, list):
            offer = offer[0] if offer else {}
        elif not isinstance(offer, dict):
            offer = {}

        price = offer.get('price')
        
        # Extract Image
        image_url_raw = data.get('image')
        image_url = ''
        if isinstance(image_url_raw, list):
            image_url = image_url_raw[0] if image_url_raw else ''
        elif isinstance(image_url_raw, str):
            image_url = image_url_raw

        # Validation and Price Formatting
        try:
            final_price = float(price)
        except (ValueError, TypeError):
            final_price = None

        if not all([product_name, final_price is not None, product_url, image_url]):
            return None
            
        return {
            'product_name': product_name,
            'price': final_price,
            'image_url': image_url,
            'product_url': product_url,
            'store': 'fravega',
        }

    # ------------------------------------------------------------------------
    # 🔨 FALLBACK HTML PARSING (Your original code)
    # ------------------------------------------------------------------------
    
    def _extract_from_html_fallback(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract product information from Fravega HTML structure (FALLBACK)
        """
        products = []
        
        try:
            # Find product containers - Fravega uses article tags with data-test-id
            product_containers = soup.find_all('article', attrs={'data-test-id': 'result-item'})
            
            if not product_containers:
                # Try alternative selectors based on common CSS patterns (less reliable)
                product_containers = soup.find_all('article', class_=lambda x: x and 'sc-' in str(x))
            
            print(f"📦 Found {len(product_containers)} product containers in HTML (Fallback)")
            
            for container in product_containers:
                try:
                    product_data = self._extract_product_from_html(container)
                    if product_data:
                        products.append(product_data)
                        print(f"  ✓ Extracted (HTML): {product_data['product_name'][:50]}... - ${product_data['price']}")
                except Exception as e:
                    # print(f"  ⚠ Warning: Failed to extract product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"⚠ HTML extraction failed: {e}")
            return []
    
    def _extract_product_from_html(self, container) -> Optional[Dict]:
        """Extract individual product data from HTML container (FALLBACK)"""
        try:
            # Extract product URL
            link_elem = container.find('a', attrs={'data-test-id': 'product-link'})
            if not link_elem:
                link_elem = container.find('a', href=True)
            
            product_url = ''
            if link_elem:
                product_url = link_elem.get('href', '')
                if product_url and not product_url.startswith('http'):
                    product_url = self.base_url + product_url
            
            # Extract product name
            name_elem = container.find('h3', attrs={'data-test-id': 'product-title'})
            if not name_elem:
                name_elem = container.find('h3')
            
            if not name_elem:
                return None
            
            product_name = name_elem.get_text(strip=True)
            
            # Extract price
            price_elem = container.find('span', attrs={'data-test-id': 'price'})
            
            if not price_elem:
                return None
            
            price_text = price_elem.get_text(strip=True)
            price = self._parse_price(price_text)
            
            if price is None:
                return None
            
            # Extract image URL
            img_elem = container.find('img', attrs={'data-test-id': 'product-image'})
            if not img_elem:
                img_elem = container.find('img')
            
            if not img_elem:
                return None
            
            # Prioritize src, then data-src, then the first URL in srcset
            image_url = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('srcset', '').split(',')[0].split(' ')[0] or ''
            
            # Clean up/normalize image URL
            if image_url and not image_url.startswith('http'):
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                else:
                    image_url = self.base_url + image_url
            
            if not all([product_name, price is not None, image_url]):
                return None
            
            return {
                'product_name': product_name,
                'price': price,
                'image_url': image_url,
                'product_url': product_url,
                'store': 'fravega',
            }
            
        except Exception:
            # print(f"  ⚠ Error extracting product (HTML): {e}")
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price string to float, handling Argentine peso format (FALLBACK)"""
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[^\d.,]', '', price_text)
            
            # Handle Argentine format: thousands separator (.) and decimal (,)
            if ',' in cleaned and '.' in cleaned:
                # Format: 1.234,56 -> 1234.56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned and cleaned.count(',') == 1 and len(cleaned.split(',')[-1]) == 2:
                 # Format: 1234,56 -> 1234.56 (assuming last comma is the decimal separator)
                cleaned = cleaned.replace(',', '.')
            else:
                 # Assume no decimal or comma is used as thousands separator
                cleaned = cleaned.replace('.', '').replace(',', '')
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return None


def run_scraper(search_term: str = "freidora"):
    """
    Main function to run the Fravega scraper.
    """
    # NOTE: You need to replace this block with your actual database/output logic
    # import { database } 
    # if not db.connect(): ...
    
    try:
        scraper = ProductScraper(search_term, max_products=20)
        products, error = scraper.scrape()
        
        if error:
            print(f"✗ Scraping failed: {error}")
            return False
        
        if not products:
            print("✗ No products scraped")
            return False

        # --- Example Output ---
        print("\n--- FINAL SCRAPED DATA ---")
        for p in products:
             print(f"Name: {p.get('product_name', 'N/A')}")
             print(f"Price: ${p.get('price', 'N/A')}")
             print(f"URL: {p.get('product_url', 'N/A')}\n")
        # ------------------------
        
        # db.clear_products(store='fravega') # Example DB function
        # db.insert_products(products, store='fravega') # Example DB function
        
        print(f"✓ Scraping completed successfully! {len(products)} products processed.")
        return True
        
    except Exception as e:
        print(f"✗ Error during scraping process: {e}")
        return False


if __name__ == "__main__":
    # Get search term from command line arguments or use 'freidora' as default
    search_term = sys.argv[1] if len(sys.argv) > 1 else "freidora"
    
    print(f"🚀 Starting Fravega scraper for: {search_term}")
    
    run_scraper(search_term)
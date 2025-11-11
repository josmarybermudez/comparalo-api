import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re
import sys


class ProductScraper:
    """Web scraper for Jumbo.com.ar product data using JSON-LD structured data"""
    
    def __init__(self, search_term: str = "bebidas", max_products: int = 20):
        self.search_term = search_term
        self.url = f"https://www.jumbo.com.ar/{search_term}?_q={search_term}&map=ft"
        self.max_products = max_products
        self.base_url = "https://www.jumbo.com.ar"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def scrape(self) -> tuple[List[Dict], Optional[str]]:
        """
        Scrape product data from Jumbo.com.ar using JSON-LD structured data
        
        Returns:
            tuple: (list of products, error message if any)
        """
        try:
            print(f"🔍 Scraping products for '{self.search_term}' from: {self.url}")
            
            # Fetch the page
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            print(f"📄 Response received (size: {len(response.text)} chars)")
            
            products = self._extract_from_state_object(response.text)
            
            if not products:
                print("⚠ __STATE__ extraction failed, trying JSON-LD...")
                soup = BeautifulSoup(response.content, 'html.parser')
                products = self._extract_from_json_ld(soup)
            
            if not products:
                return [], "No products found on the page. Page structure may have changed."
            
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
    
    def _extract_from_state_object(self, html_content: str) -> List[Dict]:
        """
        Extract product data from __STATE__ JavaScript object embedded in the page
        This is the most reliable method for VTEX/Jumbo.com.ar
        """
        products = []
        
        try:
            # Find the __STATE__ = {...} JavaScript object
            state_match = re.search(r'__STATE__\s*=\s*({.+?})\s*</script>', html_content, re.DOTALL)
            
            if not state_match:
                print("⚠ Could not find __STATE__ object in page")
                return []
            
            state_json = state_match.group(1)
            state_data = json.loads(state_json)
            
            print(f"✓ Found __STATE__ object with {len(state_data)} keys")
            
            # Look for Product entries in the state
            for key, value in state_data.items():
                if not isinstance(value, dict):
                    continue
                
                # Check if this is a product object
                if value.get('__typename') == 'Product' or 'productName' in value:
                    try:
                        product_name = value.get('productName')
                        link_text = value.get('linkText', '')
                        
                        # Get price from priceRange
                        price = None
                        price_range = value.get('priceRange')
                        if isinstance(price_range, dict):
                            selling_price = price_range.get('sellingPrice')
                            if isinstance(selling_price, dict):
                                price = selling_price.get('highPrice') or selling_price.get('lowPrice')
                        
                        # Get image from items
                        image_url = ''
                        items = value.get('items', [])
                        if items and isinstance(items, list):
                            first_item = items[0]
                            if isinstance(first_item, dict):
                                images = first_item.get('images', [])
                                if images and isinstance(images, list):
                                    first_image = images[0]
                                    if isinstance(first_image, dict):
                                        image_url = first_image.get('imageUrl', '')
                        
                        # Construct product URL
                        product_url = ''
                        if link_text:
                            product_url = f"{self.base_url}/{link_text}/p"
                        
                        if product_name and price and image_url and product_url:
                            products.append({
                                'product_name': product_name,
                                'price': float(price),
                                'image_url': image_url,
                                'product_url': product_url
                            })
                            print(f"  ✓ Extracted: {product_name[:50]}... - ${price}")
                    
                    except Exception as e:
                        continue
            
            print(f"📦 Found {len(products)} products from __STATE__")
            return products
            
        except json.JSONDecodeError as e:
            print(f"⚠ Failed to parse __STATE__ JSON: {e}")
            return []
        except Exception as e:
            print(f"⚠ __STATE__ extraction failed: {e}")
            return []
    
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract product data from JSON-LD structured data (fallback method)
        """
        products = []
        
        try:
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            
            print(f"📄 Found {len(json_ld_scripts)} JSON-LD scripts")
            
            for script in json_ld_scripts:
                try:
                    if not script.string:
                        continue
                    
                    data = json.loads(script.string)
                    
                    if isinstance(data, dict) and data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        
                        print(f"  ✓ Found ItemList with {len(items)} items")
                        
                        for item in items:
                            try:
                                product_info = item.get('item', {})
                                
                                name = product_info.get('name')
                                image = product_info.get('image')
                                product_id = product_info.get('@id', '')
                                
                                product_url = product_id if product_id.startswith('http') else ''
                                
                                offers = product_info.get('offers', {})
                                price = None
                                
                                if isinstance(offers, dict):
                                    # Try AggregateOffer first
                                    if offers.get('@type') == 'AggregateOffer':
                                        price = offers.get('lowPrice') or offers.get('highPrice')
                                    # Then try regular Offer
                                    elif offers.get('@type') == 'Offer':
                                        price = offers.get('price')
                                    # Try offers array
                                    elif 'offers' in offers:
                                        offers_list = offers.get('offers', [])
                                        if offers_list and isinstance(offers_list, list):
                                            first_offer = offers_list[0]
                                            if isinstance(first_offer, dict):
                                                price = first_offer.get('price')
                                
                                if name and price and image and product_url:
                                    products.append({
                                        'product_name': name,
                                        'price': float(price),
                                        'image_url': image,
                                        'product_url': product_url
                                    })
                                    print(f"    ✓ {name[:40]}... - ${price}")
                            
                            except Exception as e:
                                print(f"    ✗ Failed to parse item: {e}")
                                continue
                
                except json.JSONDecodeError as e:
                    print(f"  ✗ Failed to parse JSON-LD: {e}")
                    continue
                except Exception as e:
                    print(f"  ✗ Error processing JSON-LD: {e}")
                    continue
            
            print(f"📦 Found {len(products)} products from JSON-LD")
            return products
            
        except Exception as e:
            print(f"⚠ JSON-LD extraction failed: {e}")
            return []

    def _extract_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Fallback: Extract product information from HTML structure
        For Jumbo.com.ar VTEX platform
        """
        products = []
        
        try:
            # Find product containers using VTEX-specific classes
            product_containers = soup.find_all('article', class_=lambda x: x and 'vtex-product-summary' in str(x))
            
            if not product_containers:
                # Try alternative selectors
                product_containers = soup.find_all('section', attrs={'aria-label': lambda x: x and 'Producto' in str(x)})
            
            print(f"📦 Found {len(product_containers)} product containers in HTML")
            
            for container in product_containers:
                try:
                    product_data = self._extract_product_from_html(container)
                    if product_data:
                        products.append(product_data)
                        print(f"  ✓ Extracted: {product_data['product_name'][:50]}...")
                except Exception as e:
                    continue
            
            return products
            
        except Exception as e:
            print(f"⚠ HTML extraction failed: {e}")
            return []
    
    def _extract_product_from_html(self, container) -> Optional[Dict]:
        """Extract individual product data from HTML container"""
        try:
            link_elem = container.find('a', href=True)
            product_url = ''
            if link_elem:
                product_url = link_elem.get('href', '')
                if product_url and not product_url.startswith('http'):
                    product_url = self.base_url + product_url
            
            # Extract product name
            name_elem = container.find('span', class_=lambda x: x and 'productName' in str(x))
            if not name_elem:
                name_elem = container.find(attrs={'aria-label': lambda x: x and 'View product details' in str(x)})
                if name_elem:
                    aria_label = name_elem.get('aria-label', '')
                    name_elem = type('obj', (object,), {'get_text': lambda strip=True: aria_label.replace('View product details for ', '')})()
            
            if not name_elem:
                return None
            
            product_name = name_elem.get_text(strip=True)
            
            # Extract price
            price_elem = container.find('span', class_=lambda x: x and 'sellingPrice' in str(x))
            if not price_elem:
                price_elem = container.find('span', class_=lambda x: x and 'price' in str(x).lower())
            
            if not price_elem:
                return None
            
            price_text = price_elem.get_text(strip=True)
            price = self._parse_price(price_text)
            
            # Extract image URL
            img_elem = container.find('img')
            if not img_elem:
                return None
            
            image_url = img_elem.get('src') or img_elem.get('data-src') or ''
            
            # Make sure image URL is absolute
            if image_url and not image_url.startswith('http'):
                image_url = self.base_url + image_url
            
            if not all([product_name, price is not None, image_url, product_url]):
                return None
            
            return {
                'product_name': product_name,
                'price': price,
                'image_url': image_url,
                'product_url': product_url
            }
            
        except Exception as e:
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price string to float, handling Argentine peso format"""
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[^\d.,]', '', price_text)
            
            # Handle Argentine format: thousands separator (.) and decimal (,)
            if ',' in cleaned and '.' in cleaned:
                # Format: 1.234,56 -> 1234.56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                # Format: 1234,56 -> 1234.56
                cleaned = cleaned.replace(',', '.')
            elif '.' in cleaned:
                # Could be either thousands or decimal
                parts = cleaned.split('.')
                if len(parts[-1]) > 2:
                    # It's a thousands separator
                    cleaned = cleaned.replace('.', '')
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return None


def run_scraper(search_term: str = "bebidas"):
    """
    Main function to run the scraper and store data in SQLite
    
    Args:
        search_term: Product category or search query (e.g., 'monitor', 'bebidas', 'notebooks')
    """
    from database import db
    
    if not db.connect():
        print("✗ Failed to connect to database. Exiting.")
        return False
    
    try:
        # Initialize scraper with search term
        scraper = ProductScraper(search_term, max_products=20)
        
        # Scrape products
        products, error = scraper.scrape()
        
        if error:
            print(f"✗ Scraping failed: {error}")
            return False
        
        if not products:
            print("✗ No products scraped")
            return False

        # db.clear_products(store='jumbo')
        db.insert_products(products, store='jumbo')

        print(f"✓ Scraping completed successfully! {len(products)} products stored.")
        return True
        
    except Exception as e:
        print(f"✗ Error during scraping process: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    search_term = sys.argv[1] if len(sys.argv) > 1 else "bebidas"
    
    print(f"🚀 Starting scraper for: {search_term}")
    print(f"📍 URL will be: https://www.disco.com.ar/{search_term}?_q={search_term}&map=ft\n")
    
    # Run the scraper
    run_scraper(search_term)

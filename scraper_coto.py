# scraper_coto.py
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urljoin, quote

# La clase debe llamarse ProductScraper para que tasks.py pueda importarla dinámicamente
class ProductScraper:
    
    # El constructor debe aceptar 'search_term' como argumento
    def __init__(self, search_term: str, max_products: int = 20):
        self.base_url = "https://www.cotodigital.com.ar"
        # Codifica el término de búsqueda y construye la URL
        encoded_term = quote(search_term)
        self.search_url = (
            f"{self.base_url}/sitios/cdigi/categoria?_dyncharset=utf-8&Dy=1&Ntt={encoded_term}"
        )
        self.store = "coto"
        self.max_products = max_products

    def clean_price(self, price_str: str) -> float:
        """Limpia el string de precio y lo convierte a float."""
        # Ejemplo: "$1.214.999,10" -> "1214999.10"
        if not price_str:
            return 0.0
        
        # 1. Quitar el símbolo de moneda ($, etc.)
        cleaned = price_str.strip().replace('$', '')
        # 2. Reemplazar punto (separador de miles) por vacío
        cleaned = cleaned.replace('.', '')
        # 3. Reemplazar coma (separador decimal) por punto
        cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def scrape(self):
        products_data = []
        
        print(f"Buscando en COTO: {self.search_url}")
        
        # 1. Petición HTTP
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.search_url, headers=headers, timeout=15)
            response.raise_for_status() # Lanza un error para códigos de estado 4xx/5xx
        except requests.exceptions.RequestException as e:
            return None, f"Error de petición a Coto: {e}"

        # 2. Parseo con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selector para todos los contenedores de producto
        product_cards = soup.select('.productos .producto-card')
        
        if not product_cards:
            # Podría ser un error de estructura o la página cargada dinámicamente
            if "productos encontrados" not in soup.text:
                return None, "No se encontraron tarjetas de producto. La página podría requerir Selenium."

        for card in product_cards:
            if len(products_data) >= self.max_products:
                break
                
            try:
                # 4. Extracción de datos
                
                # Nombre
                name_tag = card.select_one('.nombre-producto')
                name = name_tag.text.strip() if name_tag else "N/A"
                
                # Precio (Precio principal de la oferta/tarjeta)
                price_tag = card.select_one('.centro-precios h4.card-title')
                price_value = self.clean_price(price_tag.text) if price_tag else 0.0
                
                # URL del Producto
                url_tag = card.select_one('.top-imagen-promos a')
                relative_url = url_tag.get('href') if url_tag else "N/A"
                full_url = urljoin(self.base_url, relative_url.split('%3F')[0])

                # URL de la Imagen
                img_tag = card.select_one('.product-image')
                image_url = img_tag.get('src') if img_tag else "N/A"
                
                products_data.append({
                    'product_name': name,
                    'price': price_value,
                    'image_url': image_url,
                    'product_url': full_url,
                    'store': self.store,
                    # El 'timestamp' se agrega en tasks.py
                })

            except Exception as e:
                print(f"Error procesando tarjeta de Coto: {e}")
                continue

        return products_data, None

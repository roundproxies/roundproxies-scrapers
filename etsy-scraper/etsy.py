#!/usr/bin/env python3
"""
Etsy Scraper - Educational Purpose Only
======================================

WARNING: This scraper is for educational purposes only.
For production use, please use Etsy's official API.
Always respect robots.txt and terms of service.
"""

import requests
import json
import time
import csv
import re
from datetime import datetime
from urllib.parse import urljoin, quote_plus
import random
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class EtsyScraper:
    def __init__(self, delay_range=(2, 4)):
        """
        Initialize the Etsy scraper with rate limiting.
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
        """
        self.base_url = "https://www.etsy.com"
        self.session = requests.Session()
        self.delay_range = delay_range
        
        # Set a proper user agent to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
    
    def _rate_limit(self):
        """Add delay between requests to be respectful."""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make a request with error handling and rate limiting."""
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_price(self, price_text: str) -> Dict[str, str]:
        """Extract price information from price text."""
        if not price_text:
            return {"price": "", "currency": "", "raw": ""}
        
        # Remove extra whitespace
        price_text = self._clean_text(price_text)
        
        # Extract currency and price using regex
        price_match = re.search(r'([£$€¥₹])\s*([0-9,]+\.?\d*)', price_text)
        if price_match:
            return {
                "currency": price_match.group(1),
                "price": price_match.group(2),
                "raw": price_text
            }
        
        return {"price": "", "currency": "", "raw": price_text}
    
    def search_products(self, query: str, limit: int = 20, sort_by: str = "relevancy") -> List[Dict]:
        """
        Search for products on Etsy.
        
        Args:
            query: Search term
            limit: Number of products to fetch
            sort_by: Sort method (relevancy, most_recent, price_low_to_high, price_high_to_low)
        
        Returns:
            List of product dictionaries
        """
        products = []
        page = 1
        per_page = min(20, limit)  # Etsy shows ~20 items per page
        
        print(f"Searching for '{query}' on Etsy...")
        
        while len(products) < limit:
            search_url = f"{self.base_url}/search?q={quote_plus(query)}&order={sort_by}&page={page}"
            
            response = self._make_request(search_url)
            if not response:
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product listings
            product_elements = soup.find_all('div', {'data-test-id': 'listing-card'}) or \
                             soup.find_all('div', class_=re.compile(r'listing-card'))
            
            if not product_elements:
                print(f"No more products found on page {page}")
                break
            
            for element in product_elements:
                if len(products) >= limit:
                    break
                
                try:
                    product_data = self._extract_product_from_listing(element)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    print(f"Error extracting product: {e}")
                    continue
            
            page += 1
            if page > 10:  # Safety limit
                break
        
        print(f"Found {len(products)} products for '{query}'")
        return products[:limit]
    
    def _extract_product_from_listing(self, element) -> Optional[Dict]:
        """Extract product information from a listing element."""
        try:
            # Title and link
            title_element = element.find('h3') or element.find('a', title=True)
            title = ""
            product_url = ""
            
            if title_element:
                title = self._clean_text(title_element.get_text())
                link_element = title_element.find('a') or title_element
                if link_element and link_element.get('href'):
                    product_url = urljoin(self.base_url, link_element['href'])
            
            # Price
            price_element = element.find('span', class_=re.compile(r'currency-value')) or \
                          element.find('p', class_=re.compile(r'price'))
            price_info = {"price": "", "currency": "", "raw": ""}
            if price_element:
                price_info = self._extract_price(price_element.get_text())
            
            # Shop name
            shop_element = element.find('p', class_=re.compile(r'shop')) or \
                         element.find('span', class_=re.compile(r'shop'))
            shop_name = ""
            if shop_element:
                shop_name = self._clean_text(shop_element.get_text())
            
            # Rating
            rating_element = element.find('span', class_=re.compile(r'rating')) or \
                           element.find('div', {'aria-label': re.compile(r'stars?')})
            rating = ""
            if rating_element:
                rating_text = rating_element.get('aria-label', '') or rating_element.get_text()
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of 5|stars?)', rating_text)
                if rating_match:
                    rating = rating_match.group(1)
            
            # Reviews count
            reviews_element = element.find('span', class_=re.compile(r'reviews?')) or \
                            element.find('a', href=re.compile(r'reviews'))
            reviews_count = ""
            if reviews_element:
                reviews_text = reviews_element.get_text()
                reviews_match = re.search(r'(\d+)', reviews_text)
                if reviews_match:
                    reviews_count = reviews_match.group(1)
            
            # Image URL
            img_element = element.find('img')
            image_url = ""
            if img_element and img_element.get('src'):
                image_url = img_element['src']
            
            # Free shipping indicator
            shipping_element = element.find(text=re.compile(r'free shipping', re.I))
            free_shipping = bool(shipping_element)
            
            return {
                'title': title,
                'price': price_info['price'],
                'currency': price_info['currency'],
                'price_raw': price_info['raw'],
                'shop_name': shop_name,
                'rating': rating,
                'reviews_count': reviews_count,
                'product_url': product_url,
                'image_url': image_url,
                'free_shipping': free_shipping,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None
    
    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific product.
        
        Args:
            product_url: URL of the product page
        
        Returns:
            Dictionary with detailed product information
        """
        print(f"Fetching product details from: {product_url}")
        
        response = self._make_request(product_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            # Title
            title_element = soup.find('h1') or soup.find('h2', class_=re.compile(r'listing'))
            title = self._clean_text(title_element.get_text()) if title_element else ""
            
            # Price
            price_element = soup.find('p', class_=re.compile(r'currency-value')) or \
                          soup.find('span', class_=re.compile(r'currency-value'))
            price_info = {"price": "", "currency": "", "raw": ""}
            if price_element:
                price_info = self._extract_price(price_element.get_text())
            
            # Description
            description_element = soup.find('div', {'data-test-id': 'listing-page-description'}) or \
                                soup.find('div', class_=re.compile(r'description'))
            description = ""
            if description_element:
                description = self._clean_text(description_element.get_text())
            
            # Shop information
            shop_element = soup.find('a', href=re.compile(r'/shop/')) or \
                         soup.find('span', class_=re.compile(r'shop'))
            shop_name = ""
            shop_url = ""
            if shop_element:
                shop_name = self._clean_text(shop_element.get_text())
                if shop_element.get('href'):
                    shop_url = urljoin(self.base_url, shop_element['href'])
            
            # Images
            image_elements = soup.find_all('img', class_=re.compile(r'listing-page-image|carousel'))
            images = []
            for img in image_elements[:5]:  # Limit to first 5 images
                if img.get('src'):
                    images.append(img['src'])
            
            # Tags/Categories
            tag_elements = soup.find_all('a', href=re.compile(r'/c/'))
            tags = [self._clean_text(tag.get_text()) for tag in tag_elements[:10]]
            
            # Materials
            materials_section = soup.find('div', string=re.compile(r'Materials?', re.I))
            materials = []
            if materials_section:
                materials_list = materials_section.find_next('div')
                if materials_list:
                    materials = [self._clean_text(m.get_text()) for m in materials_list.find_all('span')[:5]]
            
            return {
                'title': title,
                'price': price_info['price'],
                'currency': price_info['currency'],
                'price_raw': price_info['raw'],
                'description': description[:500],  # Limit description length
                'shop_name': shop_name,
                'shop_url': shop_url,
                'images': images,
                'tags': tags,
                'materials': materials,
                'product_url': product_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting product details: {e}")
            return None
    
    def search_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """
        Search products by category.
        
        Args:
            category: Category name (e.g., 'jewelry', 'home-living', 'clothing')
            limit: Number of products to fetch
        
        Returns:
            List of product dictionaries
        """
        category_url = f"{self.base_url}/c/{category.lower().replace(' ', '-')}"
        print(f"Fetching products from category: {category}")
        
        response = self._make_request(category_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        product_elements = soup.find_all('div', {'data-test-id': 'listing-card'}) or \
                         soup.find_all('div', class_=re.compile(r'listing-card'))
        
        for element in product_elements[:limit]:
            try:
                product_data = self._extract_product_from_listing(element)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                print(f"Error extracting product: {e}")
                continue
        
        print(f"Found {len(products)} products in category '{category}'")
        return products
    
    def save_to_csv(self, products: List[Dict], filename: str):
        """Save products to a CSV file."""
        if not products:
            print("No products to save.")
            return
        
        # Flatten nested lists for CSV
        flattened_products = []
        for product in products:
            flat_product = product.copy()
            if isinstance(product.get('images'), list):
                flat_product['images'] = '; '.join(product['images'])
            if isinstance(product.get('tags'), list):
                flat_product['tags'] = '; '.join(product['tags'])
            if isinstance(product.get('materials'), list):
                flat_product['materials'] = '; '.join(product['materials'])
            flattened_products.append(flat_product)
        
        fieldnames = flattened_products[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_products)
        
        print(f"Saved {len(products)} products to {filename}")
    
    def save_to_json(self, products: List[Dict], filename: str):
        """Save products to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(products)} products to {filename}")


def main():
    """Example usage of the Etsy scraper."""
    scraper = EtsyScraper(delay_range=(2, 4))  # Be respectful with delays
    
    # Example 1: Search for products
    print("=== Searching for 'handmade jewelry' ===")
    jewelry_products = scraper.search_products("handmade jewelry", limit=10, sort_by="relevancy")
    
    if jewelry_products:
        scraper.save_to_csv(jewelry_products, "etsy_jewelry.csv")
        scraper.save_to_json(jewelry_products, "etsy_jewelry.json")
    
    # Example 2: Get detailed information for first product
    if jewelry_products and jewelry_products[0]['product_url']:
        print("\n=== Getting detailed product information ===")
        detailed_product = scraper.get_product_details(jewelry_products[0]['product_url'])
        if detailed_product:
            print(f"Product: {detailed_product['title']}")
            print(f"Price: {detailed_product['currency']}{detailed_product['price']}")
            print(f"Shop: {detailed_product['shop_name']}")
    
    # Example 3: Browse by category
    print("\n=== Browsing 'jewelry' category ===")
    category_products = scraper.search_by_category("jewelry", limit=5)
    
    if category_products:
        scraper.save_to_csv(category_products, "etsy_category_jewelry.csv")
    
    # Display sample results
    print("\n=== Sample Products ===")
    for i, product in enumerate(jewelry_products[:3]):
        print(f"\n{i+1}. {product['title']}")
        print(f"   Price: {product['currency']}{product['price']}")
        print(f"   Shop: {product['shop_name']}")
        print(f"   Rating: {product['rating']}")
        print(f"   Reviews: {product['reviews_count']}")


if __name__ == "__main__":
    print("Required packages: requests beautifulsoup4")
    print("Install with: pip install requests beautifulsoup4")
    print("\nIMPORTANT: This scraper is for educational purposes only.")
    print("For production use, please use Etsy's official API.")
    print("Always respect robots.txt and terms of service.")
    print("Be respectful with request frequency.\n")
    
    main()

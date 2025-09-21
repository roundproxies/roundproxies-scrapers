# **Etsy.com Scraper**

This scraper is using Python, requests, and BeautifulSoup libraries to scrape product data from etsy.com.

Full tutorial: https://roundproxies.com/blog/reddit/

The scraping code is located in the `etsy_scraper.py` file. It's fully documented and simplified for educational purposes with built-in rate limiting, error handling, and respectful scraping practices.

This scraper scrapes:
* Etsy search results for product listings and metadata
* Individual product pages for detailed information including descriptions, materials, and images
* Category browsing for discovering products by category
* Shop information and product ratings/reviews data
* Product pricing, shipping information, and availability

For output examples, the scraper generates files like `etsy_jewelry.csv`, `etsy_jewelry.json`, and `etsy_category_jewelry.csv`.

## **Fair Use Disclaimer**

**Important**: This code is provided free of charge for **educational purposes only**.

- This scraper is intended for learning web scraping concepts and techniques
- Always respect Etsy's robots.txt and terms of service
- Use appropriate rate limiting to avoid overloading Etsy's servers
- The code includes built-in delays (2-4 seconds) and respectful scraping practices
- Do not use this for commercial purposes or high-volume scraping
- Be aware that excessive scraping may result in IP blocking

For any issues, please use the issue tracker. This tool is not affiliated with or endorsed by Etsy.

## **Setup and Use**

This Etsy.com scraper uses **Python 3.7+** with requests and BeautifulSoup4 for web scraping and HTML parsing.

### Prerequisites
- **Python 3.7** or higher
- Basic understanding of Python and web scraping concepts
- Familiarity with HTML structure and CSS selectors

### Installation

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd etsy-scraper
```

2. **Install required dependencies:**
```bash
pip install requests beautifulsoup4
```

3. **Run the scraper:**
```bash
python etsy_scraper.py
```

### **Basic Usage Examples**

**Search for products by keyword:**
```python
from etsy_scraper import EtsyScraper

scraper = EtsyScraper()
products = scraper.search_products("handmade jewelry", limit=20, sort_by="relevancy")
scraper.save_to_csv(products, "jewelry_products.csv")
```

**Get detailed product information:**
```python
# Get detailed info for a specific product
product_url = "https://www.etsy.com/listing/123456789/example-product"
detailed_info = scraper.get_product_details(product_url)
```

**Browse products by category:**
```python
# Browse specific categories
category_products = scraper.search_by_category("jewelry", limit=15)
home_products = scraper.search_by_category("home-living", limit=15)
```

**Available sorting options:**
- `relevancy` - Most relevant to search query (default)
- `most_recent` - Newest listings first
- `price_low_to_high` - Lowest price first
- `price_high_to_low` - Highest price first

**Popular categories:**
- `jewelry` - Jewelry and accessories
- `clothing` - Clothing and shoes
- `home-living` - Home decor and furniture
- `wedding` - Wedding accessories and decor
- `toys-games` - Toys and games
- `art-collectibles` - Art and collectibles
- `craft-supplies` - Craft supplies and tools

### **Configuration Options**

**Rate Limiting:**
```python
# Adjust delay between requests (min, max seconds)
# Default is (2, 4) seconds - be respectful!
scraper = EtsyScraper(delay_range=(3, 6))
```

**Output Formats:**
- CSV: `scraper.save_to_csv(products, "filename.csv")`
- JSON: `scraper.save_to_json(products, "filename.json")`

### **Extracted Data Fields**

**Basic Product Information:**
- `title` - Product title/name
- `price` - Product price (numeric)
- `currency` - Currency symbol (e.g., $, €, £)
- `price_raw` - Raw price text from page
- `shop_name` - Name of the Etsy shop
- `rating` - Product/shop rating (out of 5)
- `reviews_count` - Number of reviews
- `product_url` - Direct link to product page
- `image_url` - Main product image URL
- `free_shipping` - Boolean indicating free shipping
- `scraped_at` - Timestamp of data collection

**Detailed Product Information (from product pages):**
- `description` - Product description (truncated to 500 chars)
- `shop_url` - Link to the shop page
- `images` - List of product image URLs
- `tags` - Product tags and categories
- `materials` - List of materials used
- `variations` - Product variations (size, color, etc.)

### **Best Practices**

**Respectful Scraping:**
- Always use appropriate delays between requests (minimum 2 seconds)
- Don't make concurrent requests to avoid overloading servers
- Monitor your scraping frequency and adjust as needed
- Check robots.txt: `https://www.etsy.com/robots.txt`

**Error Handling:**
```python
# The scraper includes built-in error handling
products = scraper.search_products("vintage items", limit=10)
if products:
    print(f"Successfully scraped {len(products)} products")
    scraper.save_to_csv(products, "results.csv")
else:
    print("No products found or error occurred")
```

**Data Quality:**
- The scraper cleans and normalizes text data automatically
- Empty or missing fields are handled gracefully
- Price parsing handles multiple currency formats
- Image URLs are validated before extraction

### **Limitations**

**Current Limitations:**
- Etsy frequently updates their HTML structure, which may break selectors
- Some product details may not be available without JavaScript rendering
- Large-scale scraping may trigger anti-bot measures
- Search results may be limited compared to logged-in users
- Dynamic pricing and availability require real-time scraping

**Troubleshooting:**
- If scraping fails, check if Etsy has updated their page structure
- Increase delay times if you receive HTTP errors
- Use VPN or proxy rotation for large-scale projects (educational only)
- Monitor response times and adjust accordingly

### **Contributing**

This is an educational project focused on learning web scraping techniques. Contributions that enhance the learning experience while maintaining ethical scraping practices are welcome:

- Improve error handling and data extraction accuracy
- Add support for additional product fields
- Enhance documentation and examples
- Submit bug fixes for HTML structure changes

### **Legal Notice**

This scraper is provided for educational purposes only. Users are responsible for:
- Complying with Etsy's Terms of Service
- Respecting rate limits and server resources
- Not using scraped data for commercial purposes without permission
- Following applicable laws and regulations regarding data scraping

### **License**

This project is provided as-is for educational purposes. Please respect Etsy's terms of service and use responsibly. The authors are not responsible for any misuse of this tool.

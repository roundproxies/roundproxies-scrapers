# **Crunchbase.com Scraper**

This scraper is using Python, requests, and BeautifulSoup libraries to scrape business data from crunchbase.com.

Full tutorial: https://roundproxies.com/blog/crunchbase/

The scraping code is located in the `crunchbase_scraper.py` file. It's fully documented and simplified for educational purposes with conservative rate limiting, error handling, and respectful scraping practices.

This scraper scrapes:
* Company search results and detailed company profiles
* Funding rounds and investment history
* Investor information and investment portfolios  
* Key personnel and executive data
* Industry categorizations and business descriptions
* Headquarters locations and founding dates

For output examples, the scraper generates files like `crunchbase_ai_companies.csv`, `company_funding_rounds.csv`, and `crunchbase_investors.csv`.

## **Fair Use Disclaimer**

**CRITICAL**: This code is provided free of charge for **educational purposes only**.

- **Business data is sensitive and valuable** - use with extreme care and responsibility
- This scraper is intended **solely for learning web scraping concepts and techniques**
- For production use, **you MUST use Crunchbase's official API** instead
- Always respect Crunchbase's robots.txt and terms of service
- Use conservative rate limiting (3-6 seconds) to avoid overloading servers
- **Do not use this for commercial purposes, competitive intelligence, or data resale**
- **Do not scrape large volumes of data** - this violates terms of service
- Be aware that excessive scraping will result in IP blocking and potential legal action
- Some data may be behind paywalls and should not be accessed without permission

**Legal Notice**: Users are fully responsible for compliance with all applicable laws, terms of service, and data protection regulations. The authors assume no liability for misuse of this tool.

For any issues, please use the issue tracker. This tool is not affiliated with or endorsed by Crunchbase.

## **Setup and Use**

This Crunchbase.com scraper uses **Python 3.7+** with requests and BeautifulSoup4 for web scraping and HTML parsing.

### Prerequisites
- **Python 3.7** or higher
- Basic understanding of Python and web scraping concepts
- Familiarity with business data structures and terminology
- **Understanding of ethical scraping practices and legal implications**

### Installation

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd crunchbase-scraper
```

2. **Install required dependencies:**
```bash
pip install requests beautifulsoup4
```

3. **Run the scraper (educational use only):**
```bash
python crunchbase_scraper.py
```

### **Basic Usage Examples**

**Search for companies by keyword:**
```python
from crunchbase_scraper import CrunchbaseScraper

# Use conservative delays (3-6 seconds between requests)
scraper = CrunchbaseScraper(delay_range=(3, 6))

# Search for companies
companies = scraper.search_companies("fintech startups", limit=10)
scraper.save_to_csv(companies, "fintech_companies.csv")
```

**Get detailed company information:**
```python
# Get comprehensive company details
company_url = "https://www.crunchbase.com/organization/example-company"
detailed_info = scraper.get_company_details(company_url)
```

**Analyze funding rounds:**
```python
# Extract funding history for a company
funding_rounds = scraper.get_funding_rounds(company_url)
scraper.save_to_csv(funding_rounds, "funding_history.csv")
```

**Search for investors:**
```python
# Find investors and venture capital firms
investors = scraper.search_investors("venture capital", limit=10)
scraper.save_to_csv(investors, "vc_firms.csv")
```

### **Configuration Options**

**Conservative Rate Limiting (REQUIRED):**
```python
# Use longer delays to be respectful - minimum 3 seconds!
scraper = CrunchbaseScraper(delay_range=(3, 6))

# For educational exploration only - even longer delays
scraper = CrunchbaseScraper(delay_range=(5, 10))
```

**Output Formats:**
- CSV: `scraper.save_to_csv(data, "filename.csv")`
- JSON: `scraper.save_to_json(data, "filename.json")`

### **Extracted Data Fields**

**Company Information:**
- `company_name` - Official company name
- `description` - Business description (truncated to 500 chars)
- `founded_date` - Founding date
- `headquarters` - Primary location
- `employee_count` - Number of employees
- `website` - Official website URL
- `industries` - List of industry categories
- `key_people` - Names of executives and founders
- `recent_news` - Recent press releases or news
- `company_url` - Crunchbase profile URL
- `scraped_at` - Data collection timestamp

**Funding Round Information:**
- `round_type` - Type of funding (Seed, Series A, B, C, etc.)
- `amount` - Funding amount (numeric)
- `currency` - Currency symbol
- `amount_raw` - Raw amount text from page
- `date` - Date of funding round
- `investors` - List of participating investors
- `scraped_at` - Data collection timestamp

**Investor Information:**
- `investor_name` - Name of investor or firm
- `investor_type` - Type (VC, Angel, Corporate, etc.)
- `location` - Geographic location
- `investment_count` - Number of investments made
- `investor_url` - Crunchbase profile URL
- `scraped_at` - Data collection timestamp

### **Important Limitations**

**Technical Limitations:**
- Crunchbase frequently updates their HTML structure
- Many features require JavaScript rendering not available in basic scraping
- Premium data is behind paywalls and login walls
- Anti-bot measures may block scraping attempts
- Rate limiting is enforced strictly

**Legal and Ethical Limitations:**
- **Business data is proprietary and valuable**
- Bulk data extraction violates terms of service
- Commercial use requires proper licensing
- Some data is confidential and not publicly available
- International data protection laws may apply

**Data Quality Limitations:**
- Public data may be incomplete or outdated
- Financial information may be estimates or self-reported
- Company status and details change frequently
- Search results may be filtered or limited

### **Best Practices for Educational Use**

**Respectful Scraping:**
```python
# ALWAYS use conservative delays
scraper = CrunchbaseScraper(delay_range=(5, 8))

# Limit your requests
companies = scraper.search_companies("AI", limit=5)  # Small limit only

# Don't run automated scripts continuously
# Manual, educational exploration only
```

**Data Handling:**
- Only collect data necessary for your learning objectives
- Do not store or redistribute scraped business data
- Respect confidential and sensitive information
- Use aggregated or anonymized data when possible
- Delete scraped data after educational use

**Error Handling:**
```python
# The scraper includes robust error handling
try:
    companies = scraper.search_companies("blockchain", limit=3)
    if companies:
        print(f"Found {len(companies)} companies for educational analysis")
    else:
        print("No results found or access denied")
except Exception as e:
    print(f"Scraping failed: {e}")
```

### **Troubleshooting**

**Common Issues:**
```python
# If you get blocked or see errors:
# 1. Increase delays significantly
scraper = CrunchbaseScraper(delay_range=(8, 12))

# 2. Reduce request volume
companies = scraper.search_companies("tech", limit=2)

# 3. Check if you're accessing premium/login-required content
# 4. Verify robots.txt compliance: https://www.crunchbase.com/robots.txt
```

**Response to Rate Limiting:**
- If you receive HTTP 429 errors, you're making requests too quickly
- Increase delay ranges to 10-15 seconds between requests
- Consider using proxy rotation (for educational purposes only)
- Take breaks between scraping sessions

### **Contributing**

This is an educational project focused on learning ethical web scraping practices. Contributions that enhance the learning experience while maintaining legal and ethical standards are welcome:

- Improve error handling for changing HTML structures
- Add better data validation and cleaning methods
- Enhance documentation and educational examples
- Submit bug fixes for structural changes
- **Do not contribute features that enable bulk data extraction**

### **Legal and Ethical Guidelines**

**Before using this scraper:**
1. **Read and understand** Crunchbase's Terms of Service
2. **Check robots.txt**: https://www.crunchbase.com/robots.txt
3. **Understand applicable data protection laws** (GDPR, CCPA, etc.)
4. **Consider the impact** on Crunchbase's servers and business
5. **Use only for legitimate educational purposes**

**Red Flags - DO NOT:**
- Scrape large volumes of data (>50 companies per session)
- Run automated scraping scripts continuously
- Access premium or login-required content without permission
- Store or redistribute business data
- Use scraped data for commercial advantage
- Ignore HTTP error codes or anti-bot measures

### **License**

This project is provided as-is for **educational purposes only**. Users are fully responsible for:
- Compliance with all applicable laws and regulations
- Respecting terms of service and intellectual property rights
- Using data ethically and responsibly
- Seeking proper licensing for any commercial use

The authors are not responsible for any misuse of this tool or any legal consequences resulting from its use.

#!/usr/bin/env python3
"""
Crunchbase Scraper - Educational Purpose Only
============================================

WARNING: This scraper is for educational purposes only.
For production use, please use Crunchbase's official API.
Always respect robots.txt and terms of service.
Business data is sensitive - use responsibly.
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

class CrunchbaseScraper:
    def __init__(self, delay_range=(3, 6)):
        """
        Initialize the Crunchbase scraper with conservative rate limiting.
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
        """
        self.base_url = "https://www.crunchbase.com"
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
            'Cache-Control': 'max-age=0',
        })
    
    def _rate_limit(self):
        """Add conservative delay between requests to be respectful."""
        delay = random.uniform(*self.delay_range)
        print(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make a request with error handling and rate limiting."""
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=20)
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
    
    def _parse_funding_amount(self, amount_text: str) -> Dict[str, str]:
        """Parse funding amount from text."""
        if not amount_text:
            return {"amount": "", "currency": "", "raw": ""}
        
        amount_text = self._clean_text(amount_text)
        
        # Extract currency and amount
        amount_match = re.search(r'([£$€¥₹])\s*([0-9,.]+)\s*([KMB]?)', amount_text, re.I)
        if amount_match:
            currency = amount_match.group(1)
            amount = amount_match.group(2)
            multiplier = amount_match.group(3).upper()
            
            return {
                "currency": currency,
                "amount": amount,
                "multiplier": multiplier,
                "raw": amount_text
            }
        
        return {"amount": "", "currency": "", "multiplier": "", "raw": amount_text}
    
    def search_companies(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for companies on Crunchbase.
        
        Args:
            query: Search term (company name, industry, etc.)
            limit: Number of companies to fetch
        
        Returns:
            List of company dictionaries
        """
        companies = []
        
        print(f"Searching for companies: '{query}'")
        search_url = f"{self.base_url}/discover/organization.companies/f/text/{quote_plus(query)}"
        
        response = self._make_request(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find company elements (this selector may need updates as Crunchbase changes)
        company_elements = soup.find_all('div', class_=re.compile(r'grid-card|entity-card|company-card')) or \
                         soup.find_all('a', href=re.compile(r'/organization/'))
        
        if not company_elements:
            print("No company listings found. Crunchbase may have updated their structure.")
            return []
        
        for element in company_elements[:limit]:
            try:
                company_data = self._extract_company_from_search(element)
                if company_data:
                    companies.append(company_data)
            except Exception as e:
                print(f"Error extracting company: {e}")
                continue
        
        print(f"Found {len(companies)} companies")
        return companies
    
    def _extract_company_from_search(self, element) -> Optional[Dict]:
        """Extract company information from search result element."""
        try:
            # Company name and URL
            name_element = element.find('a', href=re.compile(r'/organization/')) or \
                         element.find('h3') or element.find('h4')
            
            company_name = ""
            company_url = ""
            
            if name_element:
                company_name = self._clean_text(name_element.get_text())
                if name_element.get('href'):
                    company_url = urljoin(self.base_url, name_element['href'])
            
            # Description
            description_element = element.find('p') or \
                                element.find('div', class_=re.compile(r'description'))
            description = ""
            if description_element:
                description = self._clean_text(description_element.get_text())
            
            # Industry/Category
            category_element = element.find('span', class_=re.compile(r'industry|category')) or \
                             element.find('div', class_=re.compile(r'industry|category'))
            industry = ""
            if category_element:
                industry = self._clean_text(category_element.get_text())
            
            # Location
            location_element = element.find('span', class_=re.compile(r'location')) or \
                             element.find('div', class_=re.compile(r'location'))
            location = ""
            if location_element:
                location = self._clean_text(location_element.get_text())
            
            # Funding information
            funding_element = element.find('span', class_=re.compile(r'funding|money')) or \
                            element.find('div', class_=re.compile(r'funding'))
            funding_info = {"amount": "", "currency": "", "raw": ""}
            if funding_element:
                funding_info = self._parse_funding_amount(funding_element.get_text())
            
            return {
                'company_name': company_name,
                'description': description[:300],  # Limit description length
                'industry': industry,
                'location': location,
                'funding_amount': funding_info['amount'],
                'funding_currency': funding_info['currency'],
                'funding_raw': funding_info['raw'],
                'company_url': company_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting company data: {e}")
            return None
    
    def get_company_details(self, company_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific company.
        
        Args:
            company_url: URL of the company page
        
        Returns:
            Dictionary with detailed company information
        """
        print(f"Fetching company details from: {company_url}")
        
        response = self._make_request(company_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            # Company name
            name_element = soup.find('h1') or soup.find('h2', class_=re.compile(r'company'))
            company_name = self._clean_text(name_element.get_text()) if name_element else ""
            
            # Description
            description_element = soup.find('div', class_=re.compile(r'description')) or \
                                soup.find('span', class_=re.compile(r'description'))
            description = ""
            if description_element:
                description = self._clean_text(description_element.get_text())
            
            # Founded date
            founded_element = soup.find('span', string=re.compile(r'Founded', re.I))
            founded_date = ""
            if founded_element:
                founded_parent = founded_element.find_parent()
                if founded_parent:
                    founded_date = self._clean_text(founded_parent.get_text()).replace('Founded', '').strip()
            
            # Headquarters
            hq_element = soup.find('span', string=re.compile(r'Headquarters', re.I))
            headquarters = ""
            if hq_element:
                hq_parent = hq_element.find_parent()
                if hq_parent:
                    headquarters = self._clean_text(hq_parent.get_text()).replace('Headquarters', '').strip()
            
            # Employee count
            employees_element = soup.find('span', string=re.compile(r'Employee', re.I))
            employee_count = ""
            if employees_element:
                emp_parent = employees_element.find_parent()
                if emp_parent:
                    employee_count = self._clean_text(emp_parent.get_text())
            
            # Website
            website_element = soup.find('a', href=re.compile(r'http'))
            website = ""
            if website_element and not 'crunchbase.com' in website_element.get('href', ''):
                website = website_element.get('href', '')
            
            # Industries/Categories
            industry_elements = soup.find_all('a', href=re.compile(r'/discover/.*categories'))
            industries = [self._clean_text(ind.get_text()) for ind in industry_elements[:5]]
            
            # Key people (executives, founders)
            people_elements = soup.find_all('a', href=re.compile(r'/person/'))
            key_people = []
            for person in people_elements[:10]:
                person_name = self._clean_text(person.get_text())
                if person_name and len(person_name) > 2:
                    key_people.append(person_name)
            
            # Recent news/updates
            news_elements = soup.find_all('a', class_=re.compile(r'news|press'))
            recent_news = []
            for news in news_elements[:5]:
                news_title = self._clean_text(news.get_text())
                if news_title and len(news_title) > 10:
                    recent_news.append(news_title)
            
            return {
                'company_name': company_name,
                'description': description[:500],
                'founded_date': founded_date,
                'headquarters': headquarters,
                'employee_count': employee_count,
                'website': website,
                'industries': industries,
                'key_people': key_people,
                'recent_news': recent_news,
                'company_url': company_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting company details: {e}")
            return None
    
    def get_funding_rounds(self, company_url: str) -> List[Dict]:
        """
        Get funding round information for a company.
        
        Args:
            company_url: URL of the company page
        
        Returns:
            List of funding round dictionaries
        """
        # Navigate to funding rounds tab
        funding_url = company_url.rstrip('/') + '/company_financials'
        print(f"Fetching funding rounds from: {funding_url}")
        
        response = self._make_request(funding_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        funding_rounds = []
        
        try:
            # Find funding round elements
            round_elements = soup.find_all('div', class_=re.compile(r'funding|round')) or \
                           soup.find_all('tr', class_=re.compile(r'funding|round'))
            
            for element in round_elements[:10]:  # Limit to 10 rounds
                try:
                    # Round type
                    round_type_element = element.find('span', class_=re.compile(r'round-type|series'))
                    round_type = ""
                    if round_type_element:
                        round_type = self._clean_text(round_type_element.get_text())
                    
                    # Amount
                    amount_element = element.find('span', class_=re.compile(r'money|amount'))
                    amount_info = {"amount": "", "currency": "", "raw": ""}
                    if amount_element:
                        amount_info = self._parse_funding_amount(amount_element.get_text())
                    
                    # Date
                    date_element = element.find('span', class_=re.compile(r'date'))
                    funding_date = ""
                    if date_element:
                        funding_date = self._clean_text(date_element.get_text())
                    
                    # Investors
                    investor_elements = element.find_all('a', href=re.compile(r'/organization/'))
                    investors = [self._clean_text(inv.get_text()) for inv in investor_elements[:5]]
                    
                    if round_type or amount_info['amount']:  # Only add if we have meaningful data
                        funding_rounds.append({
                            'round_type': round_type,
                            'amount': amount_info['amount'],
                            'currency': amount_info['currency'],
                            'amount_raw': amount_info['raw'],
                            'date': funding_date,
                            'investors': investors,
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                
                except Exception as e:
                    print(f"Error extracting funding round: {e}")
                    continue
        
        except Exception as e:
            print(f"Error extracting funding rounds: {e}")
        
        print(f"Found {len(funding_rounds)} funding rounds")
        return funding_rounds
    
    def search_investors(self, query: str, limit: int = 15) -> List[Dict]:
        """
        Search for investors on Crunchbase.
        
        Args:
            query: Search term (investor name, firm, etc.)
            limit: Number of investors to fetch
        
        Returns:
            List of investor dictionaries
        """
        investors = []
        
        print(f"Searching for investors: '{query}'")
        search_url = f"{self.base_url}/discover/principal.investors/f/text/{quote_plus(query)}"
        
        response = self._make_request(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find investor elements
        investor_elements = soup.find_all('div', class_=re.compile(r'grid-card|entity-card')) or \
                          soup.find_all('a', href=re.compile(r'/organization/|/person/'))
        
        for element in investor_elements[:limit]:
            try:
                investor_data = self._extract_investor_from_search(element)
                if investor_data:
                    investors.append(investor_data)
            except Exception as e:
                print(f"Error extracting investor: {e}")
                continue
        
        print(f"Found {len(investors)} investors")
        return investors
    
    def _extract_investor_from_search(self, element) -> Optional[Dict]:
        """Extract investor information from search result element."""
        try:
            # Investor name and URL
            name_element = element.find('a', href=re.compile(r'/organization/|/person/')) or \
                         element.find('h3') or element.find('h4')
            
            investor_name = ""
            investor_url = ""
            
            if name_element:
                investor_name = self._clean_text(name_element.get_text())
                if name_element.get('href'):
                    investor_url = urljoin(self.base_url, name_element['href'])
            
            # Type (VC, Angel, etc.)
            type_element = element.find('span', class_=re.compile(r'type|category'))
            investor_type = ""
            if type_element:
                investor_type = self._clean_text(type_element.get_text())
            
            # Location
            location_element = element.find('span', class_=re.compile(r'location'))
            location = ""
            if location_element:
                location = self._clean_text(location_element.get_text())
            
            # Number of investments
            investments_element = element.find('span', class_=re.compile(r'investment'))
            investment_count = ""
            if investments_element:
                count_match = re.search(r'(\d+)', investments_element.get_text())
                if count_match:
                    investment_count = count_match.group(1)
            
            return {
                'investor_name': investor_name,
                'investor_type': investor_type,
                'location': location,
                'investment_count': investment_count,
                'investor_url': investor_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting investor data: {e}")
            return None
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """Save data to a CSV file."""
        if not data:
            print("No data to save.")
            return
        
        # Flatten nested lists for CSV
        flattened_data = []
        for item in data:
            flat_item = item.copy()
            for key, value in item.items():
                if isinstance(value, list):
                    flat_item[key] = '; '.join(str(v) for v in value)
            flattened_data.append(flat_item)
        
        fieldnames = flattened_data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        
        print(f"Saved {len(data)} records to {filename}")
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save data to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(data)} records to {filename}")


def main():
    """Example usage of the Crunchbase scraper."""
    scraper = CrunchbaseScraper(delay_range=(3, 5))  # Conservative delays
    
    # Example 1: Search for companies
    print("=== Searching for 'AI startups' ===")
    ai_companies = scraper.search_companies("AI startups", limit=5)
    
    if ai_companies:
        scraper.save_to_csv(ai_companies, "crunchbase_ai_companies.csv")
        scraper.save_to_json(ai_companies, "crunchbase_ai_companies.json")
    
    # Example 2: Get detailed company information
    if ai_companies and ai_companies[0]['company_url']:
        print("\n=== Getting detailed company information ===")
        detailed_company = scraper.get_company_details(ai_companies[0]['company_url'])
        if detailed_company:
            print(f"Company: {detailed_company['company_name']}")
            print(f"Founded: {detailed_company['founded_date']}")
            print(f"Location: {detailed_company['headquarters']}")
            print(f"Website: {detailed_company['website']}")
    
    # Example 3: Get funding rounds
    if ai_companies and ai_companies[0]['company_url']:
        print("\n=== Getting funding rounds ===")
        funding_rounds = scraper.get_funding_rounds(ai_companies[0]['company_url'])
        if funding_rounds:
            scraper.save_to_csv(funding_rounds, "company_funding_rounds.csv")
    
    # Example 4: Search for investors
    print("\n=== Searching for 'venture capital' investors ===")
    investors = scraper.search_investors("venture capital", limit=5)
    
    if investors:
        scraper.save_to_csv(investors, "crunchbase_investors.csv")
    
    # Display sample results
    print("\n=== Sample Companies ===")
    for i, company in enumerate(ai_companies[:3]):
        print(f"\n{i+1}. {company['company_name']}")
        print(f"   Industry: {company['industry']}")
        print(f"   Location: {company['location']}")
        print(f"   Funding: {company['funding_currency']}{company['funding_amount']}")


if __name__ == "__main__":
    print("Required packages: requests beautifulsoup4")
    print("Install with: pip install requests beautifulsoup4")
    print("\nCRITICAL: This scraper is for educational purposes only.")
    print("For production use, please use Crunchbase's official API.")
    print("Business data is sensitive - use responsibly and ethically.")
    print("Always respect robots.txt and terms of service.")
    print("Use conservative rate limiting to avoid being blocked.\n")
    
    main()

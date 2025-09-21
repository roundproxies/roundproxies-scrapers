#!/usr/bin/env python3
"""
Reddit Scraper - Educational Purpose Only
=========================================

WARNING: This scraper is for educational purposes only.
For production use, please use Reddit's official API (PRAW).
Always respect robots.txt and terms of service.
"""

import requests
import json
import time
import csv
from datetime import datetime
from urllib.parse import urljoin
import random
from typing import List, Dict, Optional

class RedditScraper:
    def __init__(self, delay_range=(1, 3)):
        """
        Initialize the Reddit scraper with rate limiting.
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
        """
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.delay_range = delay_range
        
        # Set a proper user agent
        self.session.headers.update({
            'User-Agent': 'Educational Reddit Scraper 1.0 (Educational Purpose)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _rate_limit(self):
        """Add delay between requests to be respectful."""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make a request with error handling and rate limiting."""
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def get_subreddit_posts(self, subreddit: str, sort_by: str = "hot", limit: int = 25) -> List[Dict]:
        """
        Scrape posts from a subreddit using Reddit's JSON API.
        
        Args:
            subreddit: Name of the subreddit (without r/)
            sort_by: Sort method (hot, new, top, rising)
            limit: Number of posts to fetch (max 100)
        
        Returns:
            List of post dictionaries
        """
        # Use Reddit's JSON API endpoint
        url = f"{self.base_url}/r/{subreddit}/{sort_by}.json"
        params = {'limit': min(limit, 100)}
        
        print(f"Fetching posts from r/{subreddit} ({sort_by})...")
        
        response = self._make_request(url)
        if not response:
            return []
        
        try:
            data = response.json()
            posts = []
            
            for post_data in data['data']['children']:
                post = post_data['data']
                
                # Extract relevant information
                post_info = {
                    'id': post.get('id', ''),
                    'title': post.get('title', ''),
                    'author': post.get('author', '[deleted]'),
                    'subreddit': post.get('subreddit', ''),
                    'score': post.get('score', 0),
                    'upvote_ratio': post.get('upvote_ratio', 0),
                    'num_comments': post.get('num_comments', 0),
                    'created_utc': post.get('created_utc', 0),
                    'created_date': datetime.fromtimestamp(post.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'url': post.get('url', ''),
                    'permalink': f"{self.base_url}{post.get('permalink', '')}",
                    'selftext': post.get('selftext', ''),
                    'is_self': post.get('is_self', False),
                    'over_18': post.get('over_18', False),
                    'spoiler': post.get('spoiler', False),
                    'locked': post.get('locked', False),
                    'gilded': post.get('gilded', 0),
                    'domain': post.get('domain', ''),
                    'post_hint': post.get('post_hint', ''),
                }
                
                posts.append(post_info)
            
            print(f"Successfully scraped {len(posts)} posts from r/{subreddit}")
            return posts
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON response: {e}")
            return []
    
    def get_multiple_subreddits(self, subreddits: List[str], sort_by: str = "hot", limit: int = 25) -> Dict[str, List[Dict]]:
        """
        Scrape posts from multiple subreddits.
        
        Args:
            subreddits: List of subreddit names
            sort_by: Sort method
            limit: Number of posts per subreddit
        
        Returns:
            Dictionary mapping subreddit names to their posts
        """
        all_posts = {}
        
        for subreddit in subreddits:
            posts = self.get_subreddit_posts(subreddit, sort_by, limit)
            all_posts[subreddit] = posts
            
        return all_posts
    
    def save_to_csv(self, posts: List[Dict], filename: str):
        """Save posts to a CSV file."""
        if not posts:
            print("No posts to save.")
            return
        
        fieldnames = posts[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(posts)
        
        print(f"Saved {len(posts)} posts to {filename}")
    
    def save_to_json(self, posts: List[Dict], filename: str):
        """Save posts to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(posts, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(posts)} posts to {filename}")
    
    def filter_posts(self, posts: List[Dict], min_score: int = 0, max_age_hours: int = None) -> List[Dict]:
        """
        Filter posts based on criteria.
        
        Args:
            posts: List of post dictionaries
            min_score: Minimum score (upvotes - downvotes)
            max_age_hours: Maximum age in hours
        
        Returns:
            Filtered list of posts
        """
        filtered = []
        current_time = time.time()
        
        for post in posts:
            # Check score filter
            if post['score'] < min_score:
                continue
            
            # Check age filter
            if max_age_hours:
                post_age_hours = (current_time - post['created_utc']) / 3600
                if post_age_hours > max_age_hours:
                    continue
            
            filtered.append(post)
        
        return filtered


def main():
    """Example usage of the Reddit scraper."""
    scraper = RedditScraper(delay_range=(1, 2))
    
    # Example 1: Scrape posts from a single subreddit
    print("=== Scraping r/Python ===")
    python_posts = scraper.get_subreddit_posts("Python", "hot", 10)
    
    # Save to files
    if python_posts:
        scraper.save_to_csv(python_posts, "python_posts.csv")
        scraper.save_to_json(python_posts, "python_posts.json")
    
    # Example 2: Scrape multiple subreddits
    print("\n=== Scraping Multiple Subreddits ===")
    subreddits = ["Python", "programming", "MachineLearning"]
    all_posts = scraper.get_multiple_subreddits(subreddits, "hot", 5)
    
    # Combine all posts
    combined_posts = []
    for subreddit, posts in all_posts.items():
        combined_posts.extend(posts)
    
    # Filter posts (example: minimum 10 upvotes, max 24 hours old)
    filtered_posts = scraper.filter_posts(combined_posts, min_score=10, max_age_hours=24)
    
    print(f"\nFiltered to {len(filtered_posts)} high-quality recent posts")
    
    # Save filtered results
    if filtered_posts:
        scraper.save_to_csv(filtered_posts, "filtered_posts.csv")
    
    # Display sample results
    print("\n=== Sample Posts ===")
    for i, post in enumerate(python_posts[:3]):
        print(f"\n{i+1}. {post['title']}")
        print(f"   Author: u/{post['author']}")
        print(f"   Score: {post['score']}")
        print(f"   Comments: {post['num_comments']}")
        print(f"   Date: {post['created_date']}")
        print(f"   URL: {post['permalink']}")


if __name__ == "__main__":
    # Installation requirements reminder
    print("Required packages: requests")
    print("Install with: pip install requests")
    print("\nIMPORTANT: This scraper is for educational purposes only.")
    print("For production use, please use Reddit's official API (PRAW).")
    print("Always respect robots.txt and terms of service.\n")
    
    main()

# **Reddit.com Scraper**

This scraper is using Python and requests library to scrape data from reddit.com using Reddit's public JSON API endpoints.

Full tutorial: https://roundproxies.com/blog/reddit/

The scraping code is located in the `reddit_scraper.py` file. It's fully documented and simplified for educational purposes with built-in rate limiting and error handling.

This scraper scrapes:
* Reddit subreddit pages for post data and metadata
* Multiple subreddits simultaneously 
* Post information including scores, comments, timestamps, and content
* Filtered results based on score thresholds and post age
* Export capabilities to both CSV and JSON formats

For output examples, the scraper generates files like `python_posts.csv`, `python_posts.json`, and `filtered_posts.csv`.

## **Fair Use Disclaimer**

**Important**: This code is provided free of charge for **educational purposes only**. 

- This scraper is intended for learning web scraping concepts and techniques
- Always respect Reddit's robots.txt and terms of service
- Use appropriate rate limiting to avoid overloading Reddit's servers
- The code includes built-in delays and respectful scraping practices

For any issues, please use the issue tracker. This tool is not affiliated with or endorsed by Reddit.

## **Setup and Use**

This Reddit.com scraper uses **Python 3.7+** with the requests package for HTTP requests and built-in libraries for data processing.

### Prerequisites
- **Python 3.7** or higher
- Basic understanding of Python and web scraping concepts

### Installation

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd reddit-scraper
```

2. **Install required dependencies:**
```bash
pip install requests
```

3. **Run the scraper:**
```bash
python reddit_scraper.py
```

### **Basic Usage Examples**

**Scrape a single subreddit:**
```python
from reddit_scraper import RedditScraper

scraper = RedditScraper()
posts = scraper.get_subreddit_posts("Python", "hot", 25)
scraper.save_to_csv(posts, "python_posts.csv")
```

**Scrape multiple subreddits:**
```python
subreddits = ["Python", "programming", "MachineLearning"]
all_posts = scraper.get_multiple_subreddits(subreddits, "hot", 10)
```

**Filter posts by criteria:**
```python
# Get posts with minimum 50 upvotes from last 24 hours
filtered = scraper.filter_posts(posts, min_score=50, max_age_hours=24)
```

**Available sorting options:**
- `hot` - Currently trending posts
- `new` - Newest posts
- `top` - Highest scored posts
- `rising` - Posts gaining popularity

### **Configuration Options**

**Rate Limiting:**
```python
# Adjust delay between requests (min, max seconds)
scraper = RedditScraper(delay_range=(1, 3))
```

**Output Formats:**
- CSV: `scraper.save_to_csv(posts, "filename.csv")`
- JSON: `scraper.save_to_json(posts, "filename.json")`

### **Extracted Data Fields**

Each post contains the following information:
- `id` - Reddit post ID
- `title` - Post title
- `author` - Username of poster
- `subreddit` - Subreddit name
- `score` - Net upvotes (upvotes - downvotes)
- `upvote_ratio` - Ratio of upvotes to total votes
- `num_comments` - Number of comments
- `created_utc` - Unix timestamp
- `created_date` - Human-readable date
- `url` - External URL (if any)
- `permalink` - Reddit permalink
- `selftext` - Post content (for text posts)
- `is_self` - Boolean for text posts
- `over_18` - NSFW flag
- `spoiler` - Spoiler flag
- `locked` - Locked status
- `gilded` - Number of awards
- `domain` - Domain of external link

### **Contributing**

This is an educational project. Feel free to submit issues, suggestions, or improvements that enhance the learning experience while maintaining ethical scraping practices.

### **License**

This project is provided as-is for educational purposes. Please respect Reddit's terms of service and use responsibly.

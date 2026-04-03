#!/usr/bin/env python3
"""
RStudio Cheatsheets Web Scraper

This script scrapes the RStudio cheatsheets webpage to extract all cheatsheet names,
handling pagination automatically.

Usage:
    python3 scripts/scrape_cheatsheets.py
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
import argparse


class CheatsheetsScraper:
    """Scraper for RStudio cheatsheets webpage."""

    def __init__(self, base_url: str = "https://rstudio.github.io/cheatsheets/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a webpage."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_cheatsheet_names(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract cheatsheet names from the parsed HTML."""
        cheatsheets = []

        # Try multiple common selectors for cheatsheet items
        # Adjust these selectors based on actual page structure
        selectors = [
            '.cheatsheet-item',
            '.cheatsheet',
            'article.cheatsheet',
            '.card',
            '[data-cheatsheet]',
            'h2, h3, h4'  # Fallback to headings
        ]

        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    # Try to extract title from various possible elements
                    title = None

                    # Try to find title in heading tags
                    heading = item.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                    if heading:
                        title = heading.get_text(strip=True)

                    # Try to find title in data attribute
                    if not title and item.has_attr('data-title'):
                        title = item['data-title']

                    # Try to find title in direct text
                    if not title:
                        title = item.get_text(strip=True)

                    # Try to find associated link
                    link = None
                    a_tag = item.find('a')
                    if a_tag and a_tag.has_attr('href'):
                        link = a_tag['href']

                    if title and len(title) > 0 and len(title) < 200:
                        cheatsheets.append({
                            'name': title,
                            'link': link
                        })

                # If we found items with this selector, break
                if cheatsheets:
                    break

        return cheatsheets

    def find_next_page_url(self, soup: BeautifulSoup, current_url: str) -> str:
        """Find the URL for the next page if pagination exists."""
        # Common pagination patterns
        next_selectors = [
            'a.next',
            'a[rel="next"]',
            '.pagination .next a',
            '.pagination a[aria-label="Next"]',
            'a:contains("Next")',
            'a:contains("next")',
            'a:contains("下一页")',  # Chinese
        ]

        for selector in next_selectors:
            next_link = soup.select_one(selector)
            if next_link and next_link.has_attr('href'):
                next_url = next_link['href']
                # Handle relative URLs
                if not next_url.startswith('http'):
                    from urllib.parse import urljoin
                    next_url = urljoin(current_url, next_url)
                return next_url

        return None

    def scrape_all_pages(self, max_pages: int = 50) -> List[Dict[str, str]]:
        """Scrape all pages, handling pagination."""
        all_cheatsheets = []
        current_url = self.base_url
        visited_urls = set()
        page_count = 0

        print(f"Starting scrape from: {self.base_url}")

        while current_url and page_count < max_pages:
            if current_url in visited_urls:
                print("Detected circular pagination, stopping.")
                break

            visited_urls.add(current_url)
            page_count += 1

            print(f"\nPage {page_count}: {current_url}")

            soup = self.fetch_page(current_url)
            if not soup:
                break

            # Extract cheatsheets from current page
            cheatsheets = self.extract_cheatsheet_names(soup)
            print(f"Found {len(cheatsheets)} cheatsheets on this page")

            all_cheatsheets.extend(cheatsheets)

            # Look for next page
            next_url = self.find_next_page_url(soup, current_url)
            if next_url:
                print(f"Found next page: {next_url}")
                current_url = next_url
                time.sleep(1)  # Be polite, add delay between requests
            else:
                print("No more pages found")
                break

        # Remove duplicates while preserving order
        seen = set()
        unique_cheatsheets = []
        for item in all_cheatsheets:
            name = item['name']
            if name not in seen:
                seen.add(name)
                unique_cheatsheets.append(item)

        return unique_cheatsheets

    def save_results(self, cheatsheets: List[Dict[str, str]], output_file: str):
        """Save results to a JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cheatsheets, f, ensure_ascii=False, indent=2)
        print(f"\nSaved {len(cheatsheets)} cheatsheets to {output_file}")

    def print_results(self, cheatsheets: List[Dict[str, str]]):
        """Print results to console."""
        print("\n" + "="*60)
        print(f"Total cheatsheets found: {len(cheatsheets)}")
        print("="*60)
        for i, item in enumerate(cheatsheets, 1):
            print(f"{i}. {item['name']}")
            if item['link']:
                print(f"   Link: {item['link']}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Scrape RStudio cheatsheets webpage'
    )
    parser.add_argument(
        '--url',
        default='https://rstudio.github.io/cheatsheets/',
        help='Base URL to scrape (default: https://rstudio.github.io/cheatsheets/)'
    )
    parser.add_argument(
        '--output',
        default='cheatsheets.json',
        help='Output JSON file (default: cheatsheets.json)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help='Maximum number of pages to scrape (default: 50)'
    )

    args = parser.parse_args()

    scraper = CheatsheetsScraper(base_url=args.url)

    try:
        cheatsheets = scraper.scrape_all_pages(max_pages=args.max_pages)
        scraper.print_results(cheatsheets)
        scraper.save_results(cheatsheets, args.output)

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
    except Exception as e:
        print(f"\nError during scraping: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

# File: src/scraper.py
"""
Project Gutenberg scraper functionality
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import urljoin, urlparse
import time

class GutenbergScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Project Gutenberg Scraper App)'
        })
        self._books_cache = None
        self._last_fetch = None
    
    def get_books_paginated(self, page=1, per_page=25):
        """Get paginated list of books"""
        try:
            books = self._fetch_all_books()
            
            # Calculate pagination
            total_books = len(books)
            total_pages = (total_books + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            paginated_books = books[start_idx:end_idx]
            
            has_next = page < total_pages
            has_prev = page > 1
            
            return paginated_books, total_pages, has_next, has_prev
            
        except Exception as e:
            logging.error(f"Error fetching paginated books: {str(e)}")
            return [], 0, False, False
    
    def _fetch_all_books(self):
        """Fetch all books from the subject page"""
        # Cache for 5 minutes to avoid repeated requests
        if (self._books_cache is not None and 
            self._last_fetch is not None and 
            time.time() - self._last_fetch < 300):
            return self._books_cache
        
        try:
            books = []
            page = 1
            
            while True:
                url = f"{self.base_url}?start_index={(page-1)*25}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find book entries
                book_entries = soup.find_all('li', class_='booklink')
                
                if not book_entries:
                    break
                
                for entry in book_entries:
                    book = self._parse_book_entry(entry)
                    if book:
                        books.append(book)
                
                # Check if there's a next page
                next_link = soup.find('a', string='Next')
                if not next_link:
                    break
                
                page += 1
                time.sleep(0.5)  # Be respectful
            
            self._books_cache = books
            self._last_fetch = time.time()
            return books
            
        except Exception as e:
            logging.error(f"Error fetching books: {str(e)}")
            return []
    
    def _parse_book_entry(self, entry):
        """Parse individual book entry"""
        try:
            # Get title link
            title_link = entry.find('a', class_='link')
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            book_url = urljoin(self.base_url, title_link['href'])
            
            # Extract Gutenberg ID
            id_match = re.search(r'/ebooks/(\d+)', book_url)
            if not id_match:
                return None
            book_id = id_match.group(1)
            
            # Get author
            author = "Unknown Author"
            author_span = entry.find('span', class_='subtitle')
            if author_span:
                author = author_span.get_text(strip=True)
                # Clean up author text
                author = re.sub(r'^by\s+', '', author, flags=re.IGNORECASE)
            
            # Get download count (if available)
            download_count = "N/A"
            download_span = entry.find('span', class_='extra')
            if download_span and 'downloads' in download_span.get_text().lower():
                downloads_text = download_span.get_text()
                download_match = re.search(r'(\d+(?:,\d+)*)\s+downloads', downloads_text)
                if download_match:
                    download_count = download_match.group(1)
            
            return {
                'id': book_id,
                'title': title,
                'author': author,
                'download_count': download_count,
                'url': book_url,
                'estimated_words': self._estimate_words(book_id)
            }
            
        except Exception as e:
            logging.error(f"Error parsing book entry: {str(e)}")
            return None
    
    def _estimate_words(self, book_id):
        """Estimate word count for a book"""
        # Simple estimation based on typical book lengths
        # In a production app, you might cache actual word counts
        try:
            # Try to get file size as a rough estimate
            # Most Project Gutenberg books are 200-500 words per KB
            return 5000  # Default estimate
        except:
            return 5000
    
    def estimate_total_words(self, book_ids):
        """Estimate total words for selected books"""
        total = 0
        for book_id in book_ids:
            total += self._estimate_words(book_id)
        return total
    
    def get_book_content(self, book_id):
        """Get the full text content of a book"""
        try:
            # Try different text format URLs
            text_urls = [
                f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
                f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
                f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
            ]
            
            for url in text_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        content = response.text
                        # Remove Project Gutenberg header/footer
                        content = self._clean_gutenberg_text(content)
                        return content
                except:
                    continue
            
            return f"Error: Could not fetch content for book ID {book_id}"
            
        except Exception as e:
            logging.error(f"Error fetching book content for {book_id}: {str(e)}")
            return f"Error: Could not fetch content for book ID {book_id}"
    
    def _clean_gutenberg_text(self, text):
        """Clean Project Gutenberg text"""
        # Remove header
        start_markers = [
            "*** START OF THE PROJECT GUTENBERG",
            "*** START OF THIS PROJECT GUTENBERG",
            "***START OF THE PROJECT GUTENBERG"
        ]
        
        for marker in start_markers:
            if marker in text:
                parts = text.split(marker, 1)
                if len(parts) > 1:
                    # Find the end of the header line
                    header_end = parts[1].find('\n')
                    if header_end != -1:
                        text = parts[1][header_end+1:]
                    break
        
        # Remove footer
        end_markers = [
            "*** END OF THE PROJECT GUTENBERG",
            "*** END OF THIS PROJECT GUTENBERG",
            "End of the Project Gutenberg"
        ]
        
        for marker in end_markers:
            if marker in text:
                text = text.split(marker)[0]
                break
        
        return text.strip()

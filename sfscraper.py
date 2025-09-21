from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
import time
import requests
from urllib.parse import quote
from datetime import datetime
from article import Article


class SFScraper:
    """Handles searching and scraping reviews from Capterra.in."""

    def is_date_in_range(self, date_string, start_date, end_date):
        """
        Check if a review date falls within the specified range.
        """
        try:
            date_string = date_string.strip()

            date_formats = [
                "%Y-%m-%d"
            ]

            target_date = None
            for date_format in date_formats:
                try:
                    target_date = datetime.strptime(date_string, date_format)
                    break
                except ValueError:
                    continue

            if target_date is None:
                print(f"Could not parse date: '{date_string}'")
                return False, f"Could not parse date format: '{date_string}'"

            # Parse start and end dates (format: "DD-MM-YYYY")
            start_date_obj = datetime.strptime(start_date, "%d-%m-%Y")
            end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")

            # Check if target date is within range (inclusive)
            is_in_range = start_date_obj <= target_date <= end_date_obj
            print(f"Date check: '{date_string}' -> {target_date.strftime('%Y-%m-%d')} -> In range: {is_in_range}")

            return is_in_range, None

        except ValueError as e:
            print(f"Date parsing error for '{date_string}': {e}")
            return False, f"Date parsing error: {e}"

    def search_product(self, query):
        encoded_query = quote(query)
        url = f"https://sourceforge.net/software/?q={encoded_query}"
        try:
            with Camoufox(headless=False) as browser:
                page = browser.new_page()
                page.goto(url)
                time.sleep(10)
                if page.content():
                    soup = BeautifulSoup(page.content(), 'lxml')
                    a = soup.find('a',
                                  class_='result-heading-title')
                    if a:
                        href = a.get('href')
                        return "https://sourceforge.net" + href
                    else:
                        print("Link not found")
        except Exception as e:
            print(f"Camoufox failed: {e}")


    def get_reviews(self, url, start_date, end_date):
        print("\nTrying with Camoufox...")
        articles_list = list()
        number_of_reviews = ''
        name = ''
        try:
            with Camoufox(headless=False) as browser:
                page = browser.new_page()
                page.goto(url)
                time.sleep(10)
                soup = BeautifulSoup(page.content(), 'lxml')
                name_tag = soup.find('h1', class_ = 'title')
                if name_tag:
                    title_tag = name_tag.find('h1')
                    if title_tag.text:
                        name = title_tag.text
                number_of_reviews_tag = soup.find('a', class_ = 'reviews-link')
                if number_of_reviews_tag.text:
                    number_of_reviews = number_of_reviews_tag.text.strip()
                    number_of_reviews = number_of_reviews.replace(' User Reviews', '')
                sections = soup.find_all('div', class_='m-review extended')
                for section in sections:
                    full_description = section.find('div', class_ = 'ext-review-content').text.strip()
                    title = section.find('h3', class_ = 'review-title').text.strip()
                    date = section.find('span', class_ = 'created-date').text.strip()
                    date = date.replace('Edited ', '')
                    date = date.replace('Posted ', '')
                    name_div = section.find('div', class_='ext-review-meta').find('div', class_=False)
                    name = name_div.get_text(strip=True)

                    ##TODO: NEED TO WORK ON RATING
                    review_article = Article(
                        title=title,
                        description=full_description,
                        rating=0,
                        date=date,
                        reviewer=name
                    )
                    is_in_range, error = self.is_date_in_range(review_article.date, start_date, end_date)

                    if error:
                        print(f"Error checking date: {error}")
                    elif is_in_range:
                        print(f"✓ Review included (date in range)")
                        articles_list.append(review_article)
                    else:
                        print(f"✗ Review excluded (date out of range)")
                return name, number_of_reviews, articles_list
        except Exception as e:
            print(f"Camoufox failed: {e}")
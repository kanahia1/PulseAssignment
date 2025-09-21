from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
import time
import requests
from urllib.parse import quote
from datetime import datetime
from article import Article


class CapterraScraper:
    """Handles searching and scraping reviews from Capterra.in."""

    def is_date_in_range(self, date_string, start_date, end_date):
        """
        Check if a review date falls within the specified range.
        """
        try:
            date_string = date_string.strip()

            date_formats = [
                "%d %B %Y",
                "%B %d, %Y",
                "%d %b %Y",
                "%b %d, %Y",
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
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
        url = f"https://www.capterra.in/search/product?q={encoded_query}"
        try:
            with Camoufox(headless=False) as browser:
                page = browser.new_page()
                page.goto(url)
                time.sleep(10)
                if page.content():
                    soup = BeautifulSoup(page.content(), 'lxml')
                    a = soup.find('a',
                                  class_='entry d-flex my-4 text-decoration-none event')
                    if a:
                        href = a.get('href')
                        parts = href.split('/')
                        parts[1] = "reviews"
                        result = '/'.join(parts)
                        return "https://www.capterra.in" + result
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
                name_tag = soup.find('h1', class_ = 'h3 mb-1')
                number_of_reviews_tag = soup.find('h3', class_ = 'h4')
                if number_of_reviews_tag.text:
                    number_of_reviews = number_of_reviews_tag.text.strip()
                if name_tag.text:
                    name = name_tag.text
                sections = soup.find_all('div', class_='i18n-translation_container review-card border border-neutral-40 border-1 rounded-4 p-4 shadow-sm mb-4')
                for section in sections:
                    reviewer_name = section.find('div', class_='fw-600 mb-1').text.strip()
                    review_title = section.find('h3', class_='fs-3 fw-bold mt-0 mb-1 mb-lg-2').text.strip()
                    review_date = section.find('div', class_='fs-5 text-neutral-90 mb-2 pb-1 mb-lg-0 pb-lg-0').text.strip()
                    rating_value = section.find('span', class_ = 'ms-1').text.strip()
                    full_description = section.find_all('div', class_='fs-4 lh-2 text-neutral-99')
                    desc_text = ''
                    pros_text = ''
                    cons_text = ''

                    if len(full_description) >= 3:
                        desc = full_description[0].find('span')
                        if desc:
                            desc_text = desc.text
                        pros = full_description[1]
                        if pros:
                            pros_text = pros.text
                        cons = full_description[2]
                        if cons:
                            cons_text = cons.text
                    else:
                        if len(full_description) >= 1:
                            desc = full_description[0].find('span')
                            if desc:
                                desc_text = desc.text

                        if len(full_description) >= 2:
                            pros = full_description[1]
                            if pros:
                                pros_text = pros.text

                        if len(full_description) >= 3:
                            cons = full_description[2]
                            if cons:
                                cons_text = cons.text
                    final_description = 'Description: '+desc_text + ' Pros:' + pros_text + ' Cons:' + cons_text
                    review_article = Article(
                        title=review_title,
                        description=final_description,
                        rating=rating_value,
                        date=review_date,
                        reviewer=reviewer_name
                    )
                    is_in_range, error = self.is_date_in_range(review_article.date, start_date, end_date)

                    if error:
                        print(f"Error checking date: {error}")
                    elif is_in_range:
                        print(f"✓ Review included (date in range)")
                        articles_list.append(review_article)
                    else:
                        print(f"✗ Review excluded (date out of range)")
                number_of_reviews = number_of_reviews.replace('Filter reviews (', '').replace(')', '')
                return name, number_of_reviews, articles_list
        except Exception as e:
            print(f"Camoufox failed: {e}")
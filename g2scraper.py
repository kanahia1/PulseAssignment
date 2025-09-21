from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
import time
import requests
from urllib.parse import quote
from datetime import datetime
from article import Article


class G2Scraper:

    def __init__(self):
        self.session = self.create_session()

    def is_date_in_range(self, date_string, start_date, end_date):
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

            start_date_obj = datetime.strptime(start_date, "%d-%m-%Y")
            end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")

            is_in_range = start_date_obj <= target_date <= end_date_obj
            print(f"Date check: '{date_string}' -> {target_date.strftime('%Y-%m-%d')} -> In range: {is_in_range}")

            return is_in_range, None

        except ValueError as e:
            print(f"Date parsing error for '{date_string}': {e}")
            return False, f"Date parsing error: {e}"

    def create_session(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Cookie': 'events_distinct_id=48a95221-e62b-483e-8d1e-4bf06e98be58; _g2_session_id=c13e4a5d6b4033e84342c99c3566e73f; _gcl_au=1.1.1193217320.1758296938; _hjSessionUser_6509674=eyJpZCI6IjQ3OWVkYWIwLWE1YTEtNWQ5Zi05MmRkLTczZTI2ZWI5OWM1NyIsImNyZWF0ZWQiOjE3NTgyOTY5Mzg4MzQsImV4aXN0aW5nIjp0cnVlfQ==; _cs_c=0; sp=de490412-0e66-4a9d-bbaf-04ed8bac84e0; _gid=GA1.2.247281850.1758296939; osano_consentmanager_uuid=93613d94-0183-40dd-b1a9-acdec82c3d2d; osano_consentmanager=xyIQ183k1-eXhwyW78z996ACTq-qaRbDvUG3JcYBikHWsQfvuurPx28IAkdF_-7uMWbNrhCE4Jblqa01mbTrNWSJMXwyl_oSUIhO3phlDfVVTxJK06YVbM-ez-W35GAvkyOA7KQeFDqcyFrzPG_fJoSetBEiLflSvwQwyJfxqPwYSqjdnEhfs3pXnhNDdiHWa8pxakzsDIwBK26_-Sg4IqenAW1mu6HjZoefMGwXj-H2fkTxcuYoi2YgDEp9mR4_OtUCa22O8G54bPGJ6og9r9Kp3nwwu-n3yg8wjicZW3DKHmL6veGFmwMu1kpzGJFSB7xzprMMhwo=; zfm_cnt_ck_id=dy1b42snlue1758296939616; _fbp=fb.1.1758296941495.28393540876311210; zfm_app_l61sLB=hide; zfm_app_Zl2v7Z=hide; zfm_app_3SDj9c=hide; zfm_app_9f3XVc=show; __adroll_fpc=915e90c67bcfc4e6a57f008b8aaff0f1-1758296942017; _hjMinimizedPolls=1804245; _hjDonePolls=1804245; g_state={"i_p":1758416966687,"i_l":2}; amplitude_session=1758335938343; _sp_ses.6c8b=*; _hjSession_6509674=eyJpZCI6IjgzYmRjNzg2LTA4NjMtNDhhMy1hYWVjLTkyZDI3ZGNmYTc0ZCIsImMiOjE3NTgzMzU5NDA3ODYsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; zfm_usr_sess_ck_id=0ow29nnkkqa1758335941380; _hp2_ses_props.103086119=%7B%22r%22%3A%22https%3A%2F%2Fwww.g2.com%2Fproducts%2Fkk-digital-services%2Freviews%22%2C%22ts%22%3A1758335940511%2C%22d%22%3A%22www.g2.com%22%2C%22h%22%3A%22%2Fproducts%2Fkk-digital-services%2Freviews%22%7D; _hp2_id.103086119=%7B%22userId%22%3A%22117228606309905%22%2C%22pageviewId%22%3A%227461980827939544%22%2C%22sessionId%22%3A%224950551173239777%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _cs_id=a56b324d-2967-a61e-93d4-329c68423962.1758296939.4.1758337023.1758335941.1758127344.1792460939138.1.x; AMP_647844faf7=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI4NzQzNzZiYS0yZTY3LTQ2ZDQtYWNmMS00ZDkwYjMzN2U0NTIlMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjJmNTQwYjI0Mi1iMzY2LTQwZTAtOTdiZS1kMWJiMzc1ZDQ0ZjUlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzU4Mjk2OTQwOTUxJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJwYWdlQ291bnRlciUyMiUzQTAlN0Q=; _ga=GA1.1.1968157523.1758296938; __ar_v4=NBMTYK27EJFT3GYAV7FM56%3A20250919%3A12%7CEEPCTRZ5RNC6ZCBB2PJM4J%3A20250919%3A12%7CC6MKFN32KVBHZAS4DKYVVW%3A20250919%3A12; _ga_MFZ5NDXZ5F=GS2.1.s1758335940$o4$g1$t1758337028$j58$l0$h0; datadome=I8OoV5I5aF3tT~VmyWHdp8HyGAtje~uFepeCTUoDtWhgxwmwNC2NkED0PvJ6guCdWj~RY4mzh5q6HR8_zj92q5E4myP~CRmcUj4GbFtwUWzDfURLkge0Or2Q4XYEXWVg; _gali=product-header; _cs_s=4.5.U.9.1758339363846; __cf_bm=E15DHR6Z5n_j4zpPNYOg.AUk0Gpw94nzfY9yNu9TQCk-1758337565-1.0.1.1-gqBQkFmtZtyj4wHAjGZ8VqBCGj3d_9J.bCcNbPYv57i17d9JFNJGAeQCzq1RJbPm8B.UsgFv0TflEsIfvOrSb8uUa7rnlGGfvBgH3Bkl9LQ; _sp_id.6c8b=f540b242-b366-40e0-97be-d1bb375d44f5.1758296937.4.1758337569.1758332655.5fd740be-e6d0-48d5-a778-2e5c3b2c3808.38dfee14-2d58-4032-ba69-53526cf30571.ecf93663-0502-4090-bf78-9f81219e002d.1758335940365.24',
            'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "Windows",
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        })
        return session

    def search_product(self, query):
        encoded_query = quote(query)
        url = f"https://www.g2.com/search?utf8=%E2%9C%93&query={encoded_query}"
        session = self.create_session()
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            if response:
                soup = BeautifulSoup(response.content, 'lxml')
                a = soup.find('a',
                              class_='elv-w-fit elv-font-figtree elv-font-normal elv-tracking-normal focus-visible:elv-outline focus-visible:elv-outline-4 focus-visible:elv-outline-offset-0 focus-visible:elv-outline-purple-40 elv-text-base elv-leading-6 focus-visible:elv-rounded-sm elv-text-link active:elv-text-link-hover focus:elv-text-link-hover hover:elv-text-link-hover visited:elv-text-link-visited js-log-click')
                if a:
                    href = a.get('href')
                    img = a.find('img')
                    name = img.get('alt') if img else None
                    return name, href, url
                else:
                    print("Link not found")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during search: {e}")
            return None, None, None

    def get_reviews(self, url, start_date, end_date):
        print("\nTrying with Camoufox...")
        articles_list = list()
        try:
            with Camoufox(headless=False) as browser:
                page = browser.new_page()
                page.goto(url)
                time.sleep(20)
                number_of_reviews = BeautifulSoup(page.content(), 'lxml').find('label',
                                                                               'elv-tracking-normal elv-font-figtree elv-text-xs elv-leading-xs elv-font-light elv-text-subtle md:elv-text-base md:elv-leading-base')
                number_of_reviews.replace("(", "").replace(")", "")
                if number_of_reviews != '0':
                    soup = BeautifulSoup(page.content(), 'lxml')
                    ajax = soup.find('div', class_='nested-ajax-loading')
                    articles = ajax.find_all('article',
                                             class_='elv-bg-neutral-0 elv-border elv-rounded-md md:elv-shadow-1 elv-border-light elv-px-5 md:elv-px-6')
                    for article in articles:
                        title = article.find('div', itemprop='name').find('div').get_text(strip=True)

                        rating_value = article.find('meta', itemprop='ratingValue')['content']
                        rating = float(rating_value)  # Convert to a float

                        date = article.find('meta', itemprop='datePublished')['content']

                        reviewer = article.find('div', itemprop='author').find('meta', itemprop='name')['content']

                        like_question = article.find('div', string='What do you like best about Bitly?')
                        like_text = like_question.find_next_sibling('p').get_text(strip=True)

                        dislike_question = article.find('div', string='What do you dislike about Bitly?')
                        dislike_text = dislike_question.find_next_sibling('p').get_text(strip=True)

                        spam_text = "Review collected by and hosted on G2.com."
                        like_text = like_text.replace(spam_text, "").strip()
                        dislike_text = dislike_text.replace(spam_text, "").strip()

                        description = f"What I like: {like_text}\n\nWhat I dislike: {dislike_text}"

                        review_article = Article(
                            title=title,
                            description=description,
                            rating=rating,
                            date=date,
                            reviewer=reviewer
                        )
                        is_in_range, error = self.is_date_in_range(review_article.date, start_date, end_date)

                        if error:
                            print(f"Error checking date: {error}")
                        elif is_in_range:
                            print(f"✓ Review included (date in range)")
                            articles_list.append(review_article)
                        else:
                            print(f"✗ Review excluded (date out of range)")
                    return number_of_reviews, articles_list
                else:
                    print('No articles found!')
        except Exception as e:
            print(f"Camoufox failed: {e}")
from capterra import CapterraScraper
from data_converter import DataConverter
from g2scraper import G2Scraper
from datetime import datetime

class Application:
    """Main application class to run the scraper."""

    def runG2Scraper(self, user_query, start_date, end_date):
        try:
            scraper = G2Scraper()
            product_name, product_url = scraper.search_product(user_query)

            if product_url:
                print(f"Found product: '{product_name}'. Fetching reviews from: {product_url}")
                number_of_reviews, articles = scraper.get_reviews(product_url, start_date, end_date)
                if articles:
                    json_output = DataConverter.to_json(articles)
                    print("\n--- Scraped Reviews (JSON) ---")
                    print(json_output)
                else:
                    print("Finished with no reviews to display.")
            else:
                print(f"Could not find any products matching '{user_query}'.")

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def runCapterraScrapper(self, user_query, start_date, end_date):
        try:
            scraper = CapterraScraper()
            product_url = scraper.search_product(user_query)

            if product_url:
                name, number_of_reviews, articles = scraper.get_reviews(product_url, start_date, end_date)
                if articles:
                    json_output = DataConverter.to_json(articles)
                    print("\n--- Scraped Reviews (JSON) ---")
                    print(json_output)
                else:
                    print("Finished with no reviews to display.")
            else:
                print(f"Could not find any products matching '{user_query}'.")

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    app = Application()
    search_engine = input("Enter the website you want to search (1 = G2, 2 = Capterra): ").strip()
    user_query = input("Enter the product you want to search: ").strip()
    start_date = input("Enter the start date of your search (DD-MM-YYYY): ").strip()
    end_date = input("Enter the end date of your search (DD-MM-YYYY): ").strip()

    if not user_query:
        print("No query entered. Exiting.")
    else:
        try:
            search_engine = int(search_engine)
            if search_engine not in [1, 2]:
                print("No engine found")
            else:
                try:
                    start_date_obj = datetime.strptime(start_date, "%d-%m-%Y")
                    end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")

                    if start_date_obj >= end_date_obj:
                        print('Invalid start and end dates')
                    else:
                        if search_engine == 1:
                            app.runG2Scraper(user_query, start_date, end_date)
                        else:
                            app.runCapterraScrapper(user_query, start_date, end_date)
                except ValueError as e:
                    print(f"Invalid date format. Please use DD-MM-YYYY format. Error: {e}")

        except ValueError:
            print("Invalid search engine selection. Please enter 1 or 2.")

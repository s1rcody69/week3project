import requests 
from bs4 import BeautifulSoup
import json

bookstore_url = "https://books.toscrape.com/"

def fetch_bookstore_page(url):
    book_page_response = requests.get(url, timeout=10)

    # Check if the connection was successful using status code
    if book_page_response.status_code == 200:
        print(f"Successfully connected to: {url}")
        print(f"Status Code: {book_page_response.status_code}\n")
        return book_page_response

   

def scrape_book_listings(page_response):
    
    soup = BeautifulSoup(page_response.text, "lxml")
    all_book_pods = soup.find_all("article", class_="product_pod")

    if len(all_book_pods) == 0:
        print(" No books found on the page. The page structure may have changed.")
        return []
    else:
        print(f" Found {len(all_book_pods)} books on the page\n")

    scraped_books_list = []

    # Track seen titles to avoid duplicates
    seen_book_titles = []

    for single_book in all_book_pods:

        book_title_tag = single_book.find("h3").find("a")
        book_price_tag = single_book.find("p", class_="price_color")

        if book_title_tag is None or book_price_tag is None:
            print(" Skipping a book — missing title or price tag.")

        else:
            # --- Clean the title ---
            full_book_title = book_title_tag["title"].strip()

            # Shorten title if longer than 40 characters
            if len(full_book_title) > 40:
                display_book_title = full_book_title[:40] + "..."
            else:
                display_book_title = full_book_title

            # --- Clean the price ---
            raw_book_price = book_price_tag.text
            cleaned_book_price = float(
                raw_book_price.replace("£", "").replace("Â", "").strip()
            )
            # Format to always show 2 decimal places e.g. 50.1 → 50.10
            formatted_book_price = round(cleaned_book_price, 2)

            # --- Check for duplicates ---
            if full_book_title in seen_book_titles:
                print(f"Duplicate skipped: {display_book_title}")

            else:
                seen_book_titles.append(full_book_title)

                scraped_books_list.append({
                    "title": display_book_title,
                    "price_gbp": formatted_book_price
                })

    return scraped_books_list

def fetch_gbp_exchange_rate(target_currency_code):
    
    # Build the API URL using our key and base currency GBP
    exchange_api_url = f" https://v6.exchangerate-api.com/v6/6bfb72abbf9707f168f2d6f0/latest/GBP"

    currency_api_response = requests.get(exchange_api_url, timeout=10)

    if currency_api_response.status_code == 200:

        # Parse the JSON response into a Python dictionary
        exchange_rate_data = currency_api_response.json()

        # Check the API's own result field to confirm success
        if exchange_rate_data["result"] == "success":

            # Pull out all available rates
            all_available_rates = exchange_rate_data["conversion_rates"]

            # Check if our target currency exists in the rates
            if target_currency_code in all_available_rates:
                live_exchange_rate = all_available_rates[target_currency_code]
                print(f"Live Exchange Rate: 1 GBP = {live_exchange_rate} {target_currency_code}\n")
                return live_exchange_rate

            else:
                print(f"Currency code '{target_currency_code}' not found in exchange rates.")
                return None
            
def convert_book_prices(scraped_books_list, live_exchange_rate, target_currency_code):
    
    # Empty list to store books with converted prices
    books_with_converted_prices = []

    for single_book in scraped_books_list:

        original_gbp_price = single_book["price_gbp"]

        # The core conversion — multiply GBP price by exchange rate
        raw_converted_price = original_gbp_price * live_exchange_rate

        # Round to 2 decimal places for clean display
        final_converted_price = round(raw_converted_price, 2)

        # Add the converted price into the book dictionary as a new key
        single_book["converted_price"] = final_converted_price
        single_book["currency"] = target_currency_code

        books_with_converted_prices.append(single_book)

    print(f"Successfully converted {len(books_with_converted_prices)} book prices to {target_currency_code}\n")
    return books_with_converted_prices

# --- Run it ---
page = fetch_bookstore_page(bookstore_url)

if page is not None:
    book_listings = scrape_book_listings(page)

    if len(book_listings) > 0:
        exchange_rate = fetch_gbp_exchange_rate("KES")

        if exchange_rate is not None:
            converted_book_listings = convert_book_prices(book_listings, exchange_rate, "KES")

            # Preview first 5 converted books
            print("First 5 Books with Converted Prices:")
            for book in converted_book_listings[:5]:
                print(f"  {book['title']}")
                print(f"    GBP: £{book['price_gbp']:.2f}  →  {book['currency']}: {book['converted_price']:.2f}")


      

  

    






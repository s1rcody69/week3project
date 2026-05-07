import requests 
from bs4 import BeautifulSoup

bookstore_url = "https://books.toscrape.com/"

def fetch_bookstore_page(url):
    book_page_response = requests.get(url, timeout=10)

    # Check if the connection was successful using status code
    if book_page_response.status_code == 200:
        print(f"Successfully connected to: {url}")
        print(f"Status Code: {book_page_response.status_code}\n")
        return book_page_response

   

def scrape_book_listings(page_response):
    """
    Parses the HTML, extracts book titles and prices, and cleans the data.
    Returns a list of dictionaries e.g. [{"title": "...", "price_gbp": 12.99}, ...]
    """
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

# --- Run it ---
page = fetch_bookstore_page(bookstore_url)

if page is not None:
    book_listings = scrape_book_listings(page)

    # Print first 5 books to verify
    if len(book_listings) > 0:
        print("First 5 Scraped Books:")
        for book in book_listings[:5]:
            print(f"  {book['title']} — £{book['price_gbp']}")
    else:
        print("No books were scraped.")

    






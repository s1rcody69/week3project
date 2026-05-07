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
  
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(page_response.text, "lxml")

    # Find all book containers on the page
    all_book_pods = soup.find_all("article", class_="product_pod")

    # Check if we actually found any books
    if len(all_book_pods) == 0:
        print("No books found on the page. The page structure may have changed.")
        return []

    else:
        print(f" Found {len(all_book_pods)} books on the page\n")

    # Empty list to store our scraped books
    scraped_books_list = []

    for single_book in all_book_pods:

        # --- Extract the book title ---
        book_title_tag = single_book.find("h3").find("a")
        book_price_tag = single_book.find("p", class_="price_color")

        # Check that both title and price tags actually exist before reading them
        if book_title_tag is None or book_price_tag is None:
            print("Skipping a book — missing title or price tag.")

        else:
            book_title = book_title_tag["title"]

            # Clean the price — remove £ symbol and convert to a float number
            raw_book_price = book_price_tag.text
            cleaned_book_price = float(raw_book_price.replace("£", "").replace("Â", "").strip())

            # Store each book as a dictionary
            scraped_books_list.append({
                "title": book_title,
                "price_gbp": cleaned_book_price
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

    






"""
Example: call the Google Shopping API Apify Actor from Python.

Returns Google Shopping product listings for a query as clean, structured JSON:
title, merchant source, current and original price, rating, reviews, sale tag,
delivery terms, and product ID. One dataset item is returned per page (about 40
products), along with the available refinement filters.

This example fetches a single page so the first run is inexpensive; each page is
billed separately. Use min_price/max_price, sort_by, free_shipping, and on_sale
to narrow results.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3
Set it in a .env file (see .env.example) or export APIFY_API_TOKEN.
"""

import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    raise SystemExit(
        "APIFY_API_TOKEN is not set. Copy .env.example to .env and add your key, "
        "or run: export APIFY_API_TOKEN=your_api_key_here"
    )

client = ApifyClient(APIFY_API_TOKEN)

run_input = {
    "q": "wireless headphones",
    "max_pages": 1,
    # "min_price": 50, "max_price": 200,   # price band in local currency
    # "sort_by": 1,                        # 1 = price low to high, 2 = high to low
    # "on_sale": True,                     # only discounted items
}

print(f"Searching Google Shopping for: {run_input['q']}")
run = client.actor("johnvc/google-shopping-api-google-shopping-products-prices-deals").call(run_input=run_input)
if run is None:
    raise SystemExit("The Actor run did not start. Check your API token and inputs.")

# One dataset item is returned per page; each holds a shopping_results list.
for page in client.dataset(run.default_dataset_id).iterate_items():
    products = page.get("shopping_results", [])
    print(f"\nPage {page.get('page_number', '?')}: {len(products)} products\n")

    for product in products:
        price = product.get("price", "")
        old_price = product.get("old_price")
        tag = product.get("tag")
        deal = f"  (was {old_price}, {tag})" if old_price and tag else ""
        rating = product.get("rating")
        reviews = product.get("reviews")
        rating_str = f"{rating} ({reviews} reviews)" if rating is not None else ""

        print(f"  {product.get('position')}. {product.get('title')}")
        print(f"     {price}{deal}  -  {product.get('source', '')}")
        if rating_str:
            print(f"     {rating_str}")
        if product.get("delivery"):
            print(f"     {product.get('delivery')}")
        print()

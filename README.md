# shopify-scraper
Simple scraper to extract all products from shopify sites


Requirements:
Python 3

Usage:
python3 shopify.py [-h] [--list-collections] [--collections COLLECTIONS]
                  [--csv] [--tsv] [--google-manufacturer] [--base-feed] [site's url]

optional arguments:
  -h, --help            show this help message and exit
  --list-collections    List collections in the site
  --collections COLLECTIONS, -c COLLECTIONS
                        Download products only from the given collections
  --csv                 Output format CSV
  --tsv                 Output format TSV
  --google-manufacturer
                        Output google-manufacturer template
  --base-feed           Output original Shopify template

Listing collections:
python3 shopify.py --list-collections [site's url]

Scraping products only in given collections:
python3 shopify.py -c col1,col2,col3 [site's url]

Output to CSV with base-feed:
python3 shopify.py --csv --base-feed [site's url]
Output to TSV:
python3 shopify.py --tsv --base-feed [site's url]

Output to elliot-template format:
python3 shopify.py --tsv --elliot-template [site's url]

Example:
python3 shopify.py -c vip,babs-and-bab-lows https://www.greats.com

The products get saved into a file named products.csv in the current directory.

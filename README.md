# shopify-python-script
This python script allows you to scrape a Shopify stores product.json and output data to a specific file type.

**Requirements:**

Python 3

**Usage:**

python3 shopify.py [-h] [--list-collections] [--collections COLLECTIONS]
                  [--csv] [--tsv] [--google-manufacturer] [--base-feed] [site's url]

**Optional arguments:**

  * -h, --help: Shows help messages and allows exit
  * --list-collections: Returns a complete list of Shopify collections for the URL
  * --collections COLLECTIONS, -c COLLECTIONS: Scrape products from a specific Shopify URL's collection(s)
  * --csv: Formats the output file in .csv
  * --tsv: Formats the output file in .tsv

*Output Templates:*

  * --google-manufacturer: Outputs file to Google's Manufacturer Center Feed specification
  * --base-feed: Outputs basic product feed that includes Shopify's MetaField data
  * --elliot-template: Outputs Shopify product data into an importable Elliot catalog CSV

**Return a list of Shopify collections:**

python3 shopify.py --list-collections [site's url]

**Scrape products from a specific set of Shopify collections:**

python3 shopify.py -c col1,col2,col3 [site's url]

**Set output file format to .csv:**

python3 shopify.py --csv --base-feed [site's url]

**Set output file format to .tsv:**

python3 shopify.py --tsv --base-feed [site's url]

**Set output file format to Elliot's Product Import:**

python3 shopify.py --tsv --elliot-template [site's url]

**Example:**

python3 shopify.py -c vip,babs-and-bab-lows https://www.greats.com

The products get saved into a file named **products.csv** in the current directory.



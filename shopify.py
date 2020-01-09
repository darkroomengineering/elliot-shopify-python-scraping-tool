import sys
import csv
import json
import time
import urllib.request
from urllib.error import HTTPError
from optparse import OptionParser
import argparse

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'


def get_page(url, page, collection_handle=None):
    full_url = url
    if collection_handle:
        full_url += '/collections/{}'.format(collection_handle)
    full_url += '/products.json'
    req = urllib.request.Request(
        full_url + '?page={}'.format(page),
        data=None,
        headers={
            'User-Agent': USER_AGENT
        }
    )
    while True:
        try:
            data = urllib.request.urlopen(req).read()
            break
        except HTTPError:
            print('Blocked! Sleeping...')
            time.sleep(180)
            print('Retrying')

    products = json.loads(data.decode())['products']
    return products


def get_page_collections(url):
    full_url = url + '/collections.json'
    page = 1
    while True:
        req = urllib.request.Request(
            full_url + '?page={}'.format(page),
            data=None,
            headers={
                'User-Agent': USER_AGENT
            }
        )
        while True:
            try:
                data = urllib.request.urlopen(req).read()
                break
            except HTTPError:
                print('Blocked! Sleeping...')
                time.sleep(180)
                print('Retrying')

        cols = json.loads(data.decode())['collections']
        if not cols:
            break
        for col in cols:
            yield col
        page += 1


def check_shopify(url):
    try:
        get_page(url, 1)
        return True
    except Exception:
        return False


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
       not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url

    return fixed_url.rstrip('/')


def extract_products_collection(url, col):
    page = 1
    products = get_page(url, page, col)
    while products:
        for product in products:
            title = product['title']
            product_type = product['product_type']
            product_url = url + '/products/' + product['handle']
            product_handle = product['handle']

            def get_image(variant_id):
                images = product['images']
                for i in images:
                    k = [str(v) for v in i['variant_ids']]
                    if str(variant_id) in k:
                        return i['src']

                return ''

            for i, variant in enumerate(product['variants']):
                price = variant['price']
                option1_value = variant['option1'] or ''
                option2_value = variant['option2'] or ''
                option3_value = variant['option3'] or ''
                option_value = ' '.join([option1_value, option2_value,
                                         option3_value]).strip()
                sku = variant['sku']
                main_image_src = ''
                if product['images']:
                    main_image_src = product['images'][0]['src']

                image_src = get_image(variant['id']) or main_image_src
                stock = 'Yes'
                if not variant['available']:
                    stock = 'No'
                metafields = product['metafields'] if "metafields" in product else []
                row = {
                        'sku': sku, 'product_type': product_type,
                       'title': title, 'option_value': option_value,
                       'price': price, 'stock': stock, 'body': str(product['body_html']),
                       'variant_id': product_handle + str(variant['id']),
                       'product_url': product_url, 'image_src': image_src , "metafields" : metafields
                       }
                row.update(product)
                for k in row:
                    row[k] = str(str(row[k]).strip()) if row[k] else ''
                yield row

        page += 1
        products = get_page(url, page, col)


def extract_products(url, path, collections=None ,delimiter = "\t" , template = False):
    tsv_headers = get_headers(template)
    with open(path, 'w') as f:
        writer = csv.writer(f,delimiter=delimiter)
        # writer.writerow(tsv_headers)
        seen_variants = set()
        metafields_len = 0
        rows_data = []
        try:
            for col in get_page_collections(url):
                if collections and col['handle'] not in collections:
                    continue
                handle = col['handle']
                title = col['title']
                for product in extract_products_collection(url, handle):
                    variant_id = product['variant_id']
                    if variant_id in seen_variants:
                        continue

                    seen_variants.add(variant_id)
                    images = json.loads(product["images"].replace("'", '"'))
                    images = [x["src"] for x in images[1:]]
                    if template == BASE_TEMPLATE:
                        if( len(product['metafields']) > metafields_len ):
                            for index in range( len(product['metafields']) - metafields_len ):
                                tsv_headers.append("MetaField%i"%(metafields_len+index+1))
                            metafields_len = len(product['metafields'])
                    ret,b = format_row_data(template , product,images, title)
                    if b:
                        for i in ret:
                            rows_data.append(i)
                    else:
                        rows_data.append(ret)
        except Exception as e:

            writer.writerow(tsv_headers)
            for row in rows_data :
                writer.writerow(row)
            exit()
        writer.writerow(tsv_headers)
        for row in rows_data :
            writer.writerow(row)
def get_headers(TEMPLATE):
    if TEMPLATE == GOOGLE_TEMPLATE:
        tsv_headers = ['Code','Collection','Category','Name','Variant Name','Price','In Stock','URL','Image URL','Body','id','title','GTIN','brand','product_name','product_type','description','image_link','additional_image_link','product_page_url','release_date','disclosure_date','suggested_retial_price']
    elif TEMPLATE == ELLIOT_TEMPLATE:
        tsv_headers = ['Name', 'Description', 'SKU', 'Gender', ' Attribute 1', 'Attribute 1 Value', 'Attribute 2', 'Attribute Value 2', 'Attribute 3', 'Attribute Value 3', 'Base Image 1 ', 'Base Image 2', 'Base Image 3', 'Base Image 4', 'Base Image 5', 'Base Price(USD)', 'Sale Price(USD)', 'Quantity', 'Unit of Weight', 'Weight', 'Unit of Dimensions', 'Height', 'Width', 'Length', 'SEO Title', 'SEO Description']
    else:
        # TEMPLATE == BASE_TEMPLATE:
        tsv_headers = ['Code', 'Collection', 'Category','Name', 'Variant Name','Price', 'In Stock', 'URL', 'Image URL', 'Body']
    return tsv_headers

def format_row_data(TEMPLATE ,product,images,title):
    if TEMPLATE == GOOGLE_TEMPLATE:
        #       'Code',         'Collection','Category',             'Name',            'Variant Name',         'Price',          'In Stock',        'URL',                 'Image URL',           'Body',          'id',          'title',         'GTIN',         'brand',            'product_name',  'product_type',           'description',       'image_link','additional_image_link','product_page_url','release_date','disclosure_date','suggested_retial_price'
        return ([ product['sku'], str(title), product['product_type'], product['title'], product['option_value'], product['price'], product['stock'], product['product_url'], product['image_src'], product['body'], product['id'], product['title'], product['sku'], product['vendor'], product['title'], product['product_type'], product['body_html'], product['image_src'], ",".join(images), product['product_url'], product['created_at'][0:10], product['created_at'][0:10], product['price'] ],False)
    elif TEMPLATE == ELLIOT_TEMPLATE:
        attrs = json.loads(product['options'].replace("'",'"'))
        attributes = [] 
        variants = []
        metafields = []
        if 'variants' in product:
            variants = json.loads(product['variants'].replace("'",'"').replace("None",'""').replace("True",'""').replace("False",'""'))
        if 'metafields' in product:
            try:
                metafields = json.loads(product['metafields'].replace("'",'"').replace("None",'""').replace("True",'""').replace("False",'""'))
            except Exception as e:
                pass
        _images = []
        for i in range(3):
            if i in attrs:
                attributes.append(attrs[i]['name'])
                attributes.append(attrs[i]['values'])
            else:
                attributes.append("")
                attributes.append("")
        for i in range(5):
            if len(images)> i:
                _images.append(images[i])
            else:
                _images.append("")

        #  'Base Price(USD)', 'Sale Price(USD)', 'Quantity', 'Unit of Weight', 'Weight', 'Unit of Dimensions', 'Height', 'Width', 'Length', 'SEO Title', 'SEO Description']
        products = []
        for i in variants:
            quantity = i['inventory_quantity'] if 'inventory_quantity' in i  else ''
            weight = ''
            unit_of_weight = ''
            seo_title = ''
            seo_desc = ''
            if 'weight_unit' in i:
                 unit_of_weight = i['weight_unit']
                 weight = i['weight']
            if 'grams' in i : 
                unit_of_weight = 'grams'
                weight = i['grams']
            for meta in metafields:
                if meta == 'metafields_global_title_tag':
                    seo_title = metafields[meta]
                if meta == 'metafields_global_description_tag':
                    seo_desc = metafields[meta]
                if 'name' in meta and meta['name'] == 'metafields_global_title_tag':
                    if 'value' in meta:
                        seo_title = meta['value']
                    else:
                        seo_title = str(meta)
                if 'name' in meta and meta['name'] == 'metafields_global_description_tag':
                    if 'value' in meta:
                        seo_desc = meta['value']
                    else:
                        seo_desc = str(meta)
            products.append([ product['title'] , product['body_html'] , product['sku'] , ""  ,   ] + attributes + _images + [i['price'] , i['price'] , quantity , format_unit_weight(unit_of_weight) , weight , "" , "" , "" , "" ,seo_title,seo_desc])
        if len(products) == 0:
            products.append([ product['title'] , product['body_html'] , product['sku'] , ""  ,   ] + attributes + _images + ["" , "", "" , "" , "" , "" , "" , "" , "" ,"",""])
        return (products,True)
    else:
        return ([ product['sku'], str(title), product['product_type'], product['title'], product['option_value'], product['price'], product['stock'], product['product_url'], product['image_src'], product['body'] ] + [x for x in product['metafields']],False)
def format_unit_weight(w):
    if w.lower() == "ounces" or w.lower()=="oz":
        return "OZ"
    if w.lower() == "grams" or w.lower()=="g":
        return "G"
    if w.lower() == "pounds" or w.lower()=="lb":
        return "LB"
    if w.lower() == "kilograms" or w.lower()=="kg":
        return "KG"
    else:
        return ""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-collections' , dest="list_collections" , action="store_true" , help="List collections in the site")
    parser.add_argument("--collections" , "-c" , dest="collections" , default="" , help = "Download products only from the given collections")
    parser.add_argument("--csv", dest="csv" , action="store_true" , help="Output format CSV ")
    parser.add_argument("--tsv", dest="tsv" , action="store_true" , help="Output format TSV" )
    parser.add_argument("--google-manufacturer" , action="store_true" , help="Output google-manufacturer template")
    parser.add_argument("--elliot-template" , action="store_true", help="Output in Elliot's products template")
    parser.add_argument("--base-feed" , action="store_true" , help="Output original Shopify template")
    # constants to avoid string literal comparison 
    BASE_TEMPLATE = 0
    GOOGLE_TEMPLATE = 1
    ELLIOT_TEMPLATE = 2

    (options,args) = parser.parse_known_args()
    delimiter = "\t" if options.tsv else ','
    if len(args) > 0:
        url = fix_url(args[0])
        if options.list_collections:
            for col in get_page_collections(url):
                print(col['handle'])
        else:
            collections = []
            if options.collections:
                collections = options.collections.split(',')
            filename = 'products.tsv' if options.tsv else 'products.csv'
            if(options.elliot_template):
                extract_products(url,filename,collections,delimiter,ELLIOT_TEMPLATE)
            elif options.google_manufacturer:
                extract_products(url, filename, collections , delimiter , GOOGLE_TEMPLATE)
            elif not options.base_feed:
                extract_products(url, filename, collections , delimiter , GOOGLE_TEMPLATE)
            else:
                extract_products(url, filename, collections , delimiter , BASE_TEMPLATE)

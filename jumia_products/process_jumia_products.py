import pandas as pd
import os
import json 
import glob
import clickhouse_db_conn_cls as cls
import shutil

# Function to read JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def data_insert(table_name, db_name, df):
    try:
        conn = cls.clickhouse_connect()
        # conn.clickhouse_truncate(db_name, table_name)
        conn.clickhouse_insert(table_name, db_name, df)
        print(f'data has been successfully inserted into table : {db_name}.{table_name}')
        conn.close()
    except Exception as e:
        print("Exception raised for def data_insert method  - {}".format(str(e)))

def process_products_data(shop_id):
    json_folder_path = f'jumia_products/{shop_id}/'  # Replace with your JSON folder path
    done_folder_path = f'jumia_products/{shop_id}/done/'  # Folder to move processed files

    # Ensure the 'done' folder exists
    os.makedirs(done_folder_path, exist_ok=True)

    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder_path, '*.json'))

    for file_path in json_files:
        print(f'Processing file: {file_path}')
        try:
            data = read_json_file(file_path)
            products = data.get('products', [])

            # Extract required fields from each product
            extracted_data = []
            for product in products:
                product_id = product.get('id')
                name = product.get('name')
                parent_sku = product.get('parentSku')
                shop_id = product.get('shop', {}).get('id')
                brand_code = product.get('brand', {}).get('code')
                brand_name = product.get('brand', {}).get('name')
                category_code = product.get('category', {}).get('code')
                category_name = product.get('category', {}).get('name')
                attribute_set_id = product.get('attributeSetId')
                product_status = None
                product_model = None
                product_gender= None

                for attribute in product.get('attributes', []):
                    if attribute.get('name') == 'status':
                        product_status = attribute.get('value')
                    if attribute.get('name') == 'model':
                        product_model = attribute.get('value')
                    if attribute.get('name') == 'gender':
                        product_gender = attribute.get('value')

                variations = product.get('variations', [])
                #print(len(variations))

                for variation in variations:
                    seller_sku = variation.get('sellerSku')
                    barcodeEan = variation.get('barcodeEan')
                    variation_id = variation.get('id')
                    print(variation_id)
                    variation_name = variation.get('variation')
                    global_price_value = variation.get('globalPrice', {}).get('value')
                    global_price_currency = variation.get('globalPrice', {}).get('currency')
                    sale_price = variation.get('globalPrice', {}).get('salePrice', {})
                    sale_price_value = sale_price.get('value', None) if sale_price else None
                    sale_price_local_value = sale_price.get('localValue', None) if sale_price else None
                    sale_price_start_at = str(sale_price.get('startAt')) if sale_price else None
                    sale_price_end_at = str(sale_price.get('endAt')) if sale_price else None

                    for business_client in variation.get("businessClients",[]):
                        business_client_code = business_client.get("code")
                        business_client_name = business_client.get("name")
                        business_client_sku = business_client.get("sku")
                        business_client_countryName = business_client.get("countryName")
                        business_client_countryCode = business_client.get("countryCode")
                        business_client_visible = business_client.get("visible")
                        business_client_price= business_client.get("price", {}) 
                        business_client_price_local_value = None
                        business_client_price_local_currency = None
                        business_client_price_currency = None
                        business_client_price_value = None
                        business_client_price_saleprice_local_value = None
                        business_client_price_saleprice_value = None
                        business_client_price_saleprice_startAt = None
                        business_client_price_saleprice_endAt = None
                        business_client_price_saleprice_local_value = None
                        business_client_price_saleprice_value = None
                        business_client_price_saleprice_startAt = None
                        business_client_price_saleprice_endAt = None
                        if business_client_price:
                            business_client_price_local_value =business_client_price.get("localValue")
                            business_client_price_local_currency = business_client_price.get("localCurrency")
                            business_client_price_currency = business_client_price.get("currency")
                            business_client_price_value = business_client_price.get("value")
                            business_client_price_saleprice = business_client_price.get("salePrice", {})
                            if business_client_price_saleprice:                                        
                                business_client_price_saleprice_local_value = business_client.get("price", {}).get("salePrice",{}).get("localValue")
                                business_client_price_saleprice_value = business_client.get("price", {}).get("salePrice",{}).get("value")
                                business_client_price_saleprice_startAt = str(business_client.get("price", {}).get("salePrice",{}).get("startAt"))
                                business_client_price_saleprice_endAt = str(business_client.get("price", {}).get("salePrice",{}).get("endAt"))
                            
                        extracted_data.append({
                            'id': product_id,
                            'name': name,
                            'parentSku': parent_sku,
                            'shop_id': shop_id,
                            'brand_code': brand_code,
                            'brand_name': brand_name,
                            'category_code': category_code,
                            'category_name': category_name,
                            'attribute_set_id': attribute_set_id,
                            'seller_sku': seller_sku,
                            'source_file_name': os.path.basename(file_path),
                            'barcodeEan': barcodeEan,
                            'variation_id': variation_id,
                            'variation_name': variation_name,
                            'global_price_value': global_price_value,
                            'global_price_currency': global_price_currency,
                            'sale_price_value': sale_price_value,
                            'sale_price_local_value': sale_price_local_value,
                            'sale_price_start_at': sale_price_start_at,
                            'sale_price_end_at': sale_price_end_at,
                            'product_status': product_status,
                            'product_model': product_model,
                            'product_gender': product_gender,
                            'business_client_code': business_client_code,
                            'business_client_name': business_client_name,
                            'business_client_sku': business_client_sku,
                            'business_client_countryName': business_client_countryName,
                            'business_client_countryCode': business_client_countryCode,
                            'business_client_visible': business_client_visible,
                            'business_client_price_local_value': business_client_price_local_value,
                            'business_client_price_local_currency': business_client_price_local_currency,
                            'business_client_price_currency': business_client_price_currency,
                            'business_client_price_value': business_client_price_value,
                            'business_client_price_saleprice_local_value': business_client_price_saleprice_local_value,
                            'business_client_price_saleprice_value': business_client_price_saleprice_value,
                            'business_client_price_saleprice_startAt': business_client_price_saleprice_startAt,
                            'business_client_price_saleprice_endAt': business_client_price_saleprice_endAt,


                        })
                    #print(extracted_data[0])

            # Convert extracted data to DataFrame
            df = pd.DataFrame(extracted_data)
            df['created_at'] = pd.Timestamp.now().date()
            #df.to_csv('jumia_products.csv', index=False)

            # Insert data into ClickHouse
            data_insert('jumia_product_variants', 'cptdg_db', df)
            print(f'Processed and inserted data from file: {file_path}')

            # Move the processed file to the 'done' folder
            shutil.move(file_path, os.path.join(done_folder_path, os.path.basename(file_path)))
            print(f'Moved file to done folder: {file_path}')
            
        except Exception as e:
            print(f"Failed to process file {file_path}: {str(e)}")
            print(e)
        #break

process_products_data('bca4a0d7-8bcb-4e42-925c-380f83e225b0')
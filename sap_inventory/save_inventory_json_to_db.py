import json
import os
import clickhouse_db_conn_cls as cls
import pandas as pd
import glob
import shutil
from datetime import datetime


def data_insert(table_name, db_name, df):
    try:
        conn = cls.clickhouse_connect()
        # conn.clickhouse_truncate(db_name, table_name)
        conn.clickhouse_insert(table_name, db_name, df)
        print(f'data has been successfully inserted into table : {db_name}.{table_name}')
        conn.close()
    except Exception as e:
        print("Exception raised for def data_insert method  - {}".format(str(e)))


# Function to read JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

    # Function to insert data into ClickHouse
def insert_data_to_clickhouse(data, source):
        # Convert JSON data to DataFrame
        df = pd.DataFrame(data['value'])
        
        # List of required columns
        required_columns = [
            "U_TAG", "U_ColorFamily", "U_Images", "U_SyncFlag", "U_ParentId", "U_VariantId",
            "U_InventoryItemId", "U_StockFlag", "U_DataSource", "U_ProductType1", "U_MJTYPE",
            "U_MJSIZE", "U_MJCOLOR", "U_MJSKU", "U_MJGENDER", "U_MJSTAT", "U_MJVURL", "U_WMS_Sync",
            "U_SyncMsg", "U_EI", "U_MJHANDLE", "U_MJMTIT", "U_MJMDES"
        ]
        
        # Add missing columns with null values
        for column in required_columns:
            if column not in df.columns:
                df[column] = None

        # Add the source column
        df['source'] = source
        # Add the inventory_fetch_date column with the current date
        df['inventory_fetch_date'] = datetime.now().strftime('%Y-%m-%d')

        data_insert('sap_items_temp', 'cptdg_db', df)
        # Extract the contents of the 'ItemWarehouseInfoCollection' column which contains arrays of objects
        item_warehouse_info_list = df['ItemWarehouseInfoCollection'].tolist()

        # Flatten the list of lists into a single list of dictionaries
        flattened_item_warehouse_info = [item for sublist in item_warehouse_info_list for item in sublist]

        # Create a new DataFrame with the flattened list of dictionaries
        item_warehouse_df = pd.DataFrame(flattened_item_warehouse_info)
        
        # Add the source column
        item_warehouse_df['source'] = source
        item_warehouse_df['inventory_fetch_date'] = datetime.now().strftime('%Y-%m-%d')

        # Add the parent_item_code column from df
        item_warehouse_df['parent_item_code'] = df['ItemCode'].repeat(df['ItemWarehouseInfoCollection'].str.len()).values

        # Assuming the DataFrame columns match the ClickHouse table columns
        
        data_insert('sap_item_warehouse_info_temp', 'cptdg_db', item_warehouse_df)

def process_jumia_categories():
    json_folder_path = 'jumia_categories/'  # Replace with your JSON folder path
    done_folder_path = 'jumia_categories/done/'  # Folder to move processed files

    # Ensure the 'done' folder exists
    os.makedirs(done_folder_path, exist_ok=True)

    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder_path, '*.json'))

    for file_path in json_files:
        try:
            data = read_json_file(file_path)
            categories = data.get('categories', [])

            # Convert categories list to DataFrame
            df = pd.DataFrame(categories)

            # Ensure the DataFrame has the required columns
            required_columns = [
                'code', 'name', 'hasChildren', 'completePath', 'attributeSet.sid', 'attributeSet.name'
            ]
            for column in required_columns:
                if column not in df.columns:
                    df[column] = None

            # Convert boolean columns to string
            df['hasChildren'] = df['hasChildren'].astype(str)

            # Flatten the attributeSet column
            df['attributeSet.sid'] = df['attributeSet'].apply(lambda x: x.get('sid') if isinstance(x, dict) else None)
            df['attributeSet.name'] = df['attributeSet'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
            df.drop(columns=['attributeSet'], inplace=True)

            # Insert data into ClickHouse
            data_insert('jumia_categories', 'cptdg_db', df)
            print(f'Processed and inserted data from file: {file_path}')

            # Move the processed file to the 'done' folder
            shutil.move(file_path, os.path.join(done_folder_path, os.path.basename(file_path)))
            print(f'Moved file to done folder: {file_path}')
        except Exception as e:
            print(f"Failed to process file {file_path}: {str(e)}")


def process_jumia_brands():
    json_folder_path = 'jumia_brands/'  # Replace with your JSON folder path
    done_folder_path = 'jumia_brands/done/'  # Folder to move processed files

    # Ensure the 'done' folder exists
    os.makedirs(done_folder_path, exist_ok=True)

    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder_path, '*.json'))

    for file_path in json_files:
        try:
            data = read_json_file(file_path)
            brands = data.get('brands', [])
            
            # Convert brands list to DataFrame
            df = pd.DataFrame(brands)

            # Ensure the DataFrame has the required columns
            required_columns = ['code', 'name']
            for column in required_columns:
                if column not in df.columns:
                    df[column] = None

            # Insert data into ClickHouse
            data_insert('jumia_brands', 'cptdg_db', df)
            print(f'Processed and inserted data from file: {file_path}')

            # Move the processed file to the 'done' folder
            shutil.move(file_path, os.path.join(done_folder_path, os.path.basename(file_path)))
            print(f'Moved file to done folder: {file_path}')
        except Exception as e:
            print(f"Failed to process file {file_path}: {str(e)}")


def process_inventory_data():
    folder_names = ["MAR1","KEN1","UGA","NGA","SEN","CIV","EGY"]
    
    for folder_name in folder_names:
        json_folder_path = f'inventory_json/20241206/{folder_name}/'  # Replace with your JSON folder path
        done_folder_path = f'inventory_json/20241206/{folder_name}/done/'  # Folder to move processed files

        # Ensure the 'done' folder exists
        os.makedirs(done_folder_path, exist_ok=True)

        # Get all JSON files that start with 'items_data'
        json_files = glob.glob(os.path.join(json_folder_path, 'items_data*.json'))

        for file_path in json_files:
            try:
                data = read_json_file(file_path)
                insert_data_to_clickhouse(data, folder_name)
                # Move the processed file to the 'done' folder
                shutil.move(file_path, os.path.join(done_folder_path, os.path.basename(file_path)))
                print(f'Processed and moved file: {file_path}')
            except Exception as e:
                print(f"Failed to process file {file_path}: {str(e)}")


def process_products_data():
    json_folder_path = 'jumia_products/fa7afff6-4dab-467c-bd5d-d25625bbc689/'  # Replace with your JSON folder path
    done_folder_path = 'jumia_products/fa7afff6-4dab-467c-bd5d-d25625bbc689/done/'  # Folder to move processed files

    # Ensure the 'done' folder exists
    os.makedirs(done_folder_path, exist_ok=True)

    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder_path, '*.json'))

    for file_path in json_files:
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
                variations = product.get('variations', [])

                for variation in variations:
                    seller_sku = variation.get('sellerSku')
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
                        'source_file_name': os.path.basename(file_path)  # Add the file name to the extracted data
                    })

            # Convert extracted data to DataFrame
            df = pd.DataFrame(extracted_data)
            df.to_csv('jumia_products.csv', index=False)

            # Insert data into ClickHouse
            data_insert('jumia_products', 'cptdg_db', df)
            print(f'Processed and inserted data from file: {file_path}')

            # Move the processed file to the 'done' folder
            shutil.move(file_path, os.path.join(done_folder_path, os.path.basename(file_path)))
            print(f'Moved file to done folder: {file_path}')
            
        except Exception as e:
            print(f"Failed to process file {file_path}: {str(e)}")

# Example of how to call the function manually
if __name__ == "__main__":
    process_inventory_data()
    #process_jumia_categories()
    #process_jumia_brands()
    #process_products_data()



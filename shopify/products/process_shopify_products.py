import pandas as pd
import json
import uuid
from datetime import date

import clickhouse_db_conn_cls as cls
def data_insert(table_name, db_name, df):
    try:
        conn = cls.clickhouse_connect()
        # conn.clickhouse_truncate(db_name, table_name)
        conn.clickhouse_insert(table_name, db_name, df)
        print(f'data has been successfully inserted into table : {db_name}.{table_name}')
        conn.close()
    except Exception as e:
        print("Exception raised for def data_insert method  - {}".format(str(e)))

# Load the JSON file
with open('products_batch_2.json') as file:
    data = json.load(file)

# Normalize the data to flatten nested fields
df = pd.json_normalize(
    data['products'], 
    record_path=['variants'], 
    meta=['id', 'title', 'vendor', 'product_type', 'tags','created_at','status','updated_at'],
    meta_prefix='product_',  # Prefix to avoid conflicts
    record_prefix='variant_',  # Prefix for nested fields
    errors='ignore'
)

# Add a UUID column for each row
df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]

# Add a created_at column with today's date
df['created_at'] = date.today().isoformat()
# Cast all columns except 'created_at' to string
for col in df.columns:
    if col != 'created_at':
        df[col] = df[col].astype(str)

data_insert('shopify_product_variants', 'cptdg_db', df)
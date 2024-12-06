import pandas as pd
import os
import glob
from datetime import datetime
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

# Define the folder path
folder_path = r'sap_ledger'

# Get all JSON files in the folder and its subfolders
json_files = glob.glob(os.path.join(folder_path, '**', '*.json'), recursive=True)

# Ensure that json_files is not empty
if not json_files:
    print("No JSON files found.")
else:
    print(json_files)

# Read and concatenate all JSON files into a single DataFrame

# Flatten the 'value' array in each JSON file
flattened_df_list = []
for file in json_files:
    data = pd.read_json(file)
    if 'value' in data.columns:
        flattened_data = pd.json_normalize(data['value'])
    else:
        flattened_data = data
    
    # Extract ledger_date and warehouse_code from the file path
    parts = file.split(os.sep)
    ledger_date = parts[-3]
    source = parts[-2]
    
    # Add the extracted values as new columns
    flattened_data['ledger_date'] = pd.to_datetime(ledger_date).date()
    flattened_data['source'] = source
    flattened_data['ingested_at'] = datetime.today().strftime('%Y-%m-%d')


    flattened_df_list.append(flattened_data)


# Combine the flattened DataFrames
combined_df = pd.concat(flattened_df_list, ignore_index=True)

# Display the combined DataFrame
print(combined_df[:2])

# Display the combined DataFrame with new columns
print(combined_df.dtypes)
for column in combined_df.columns:
    print(f"Column: {column}, Type: {combined_df[column].dtype}")

data_insert('sap_ledger_entries', 'cptdg_db', combined_df)
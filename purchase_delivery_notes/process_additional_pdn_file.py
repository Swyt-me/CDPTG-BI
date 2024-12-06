import os
import pandas as pd
import json
from pandas import json_normalize
from datetime import datetime
import uuid
import clickhouse_db_conn_cls as cls


def read_json_files(base_folder):
    data = []
    for date_folder in os.listdir(base_folder):
        date_folder_path = os.path.join(base_folder, date_folder)
        if os.path.isdir(date_folder_path):
            for country_folder in os.listdir(date_folder_path):
                country_folder_path = os.path.join(date_folder_path, country_folder)
                if os.path.isdir(country_folder_path):
                    for json_file in os.listdir(country_folder_path):
                        if json_file.endswith('.json'):
                            json_file_path = os.path.join(country_folder_path, json_file)
                            with open(json_file_path, 'r') as file:
                                json_data = json.load(file)
                                if 'value' in json_data:
                                    flattened_data = json_normalize(json_data, record_path='value', errors='ignore', sep='_')
                                    flattened_data['source'] = country_folder
                                    flattened_data['foldername'] = date_folder
                                    flattened_data['filename'] = json_file
                                    data.append(flattened_data)
    return pd.concat(data, ignore_index=True)


def data_insert(table_name, db_name, df):
    try:
        conn = cls.clickhouse_connect()
        # conn.clickhouse_truncate(db_name, table_name)
        conn.clickhouse_insert(table_name, db_name, df)
        print(f'data has been successfully inserted into table : {db_name}.{table_name}')
        conn.close()
    except Exception as e:
        print("Exception raised for def data_insert method  - {}".format(str(e)))

base_folder = 'sap_pdn_additional'
df = read_json_files(base_folder)

df.columns = [col.split('_')[-1] for col in df.columns]
df['created_at'] = datetime.now().strftime('%Y-%m-%d')
df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]


data_insert('pdn_additional_data', 'cptdg_db', df)
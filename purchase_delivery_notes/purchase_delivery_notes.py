import pandas as pd
import uuid
import clickhouse_db_conn_cls as cls

def process_pdn(file_name):
    # Read the JSON file into a DataFrame
    df = pd.read_json(file_name)
    
    # Flatten the DataFrame up to 2 levels
    df = pd.json_normalize(df.to_dict(orient='records'), record_path=['value', 'DocumentLines']
                           , meta=[
                                ['value','odata.etag']
                                ,['value','DocNum']
                                ,['value','DocDate']
                                ,['value','CardCode']
                                ,['value','CardName']
                                ,['value','NumAtCard']
                                ,['value','DocCurrency']
                                ,['value','DocRate']
                                ,['value','Reference1']
                                ,['value','Comments']
                                ,['value','JournalMemo']
                                ,['value','CreationDate']
                                ,['value','UpdateDate']
                                ,['value','Address2']
                                ,['value','DocumentStatus']
                                ,['value','U_PQ2']
                               ])
    df = df.astype(str)

    # Replace dots in column names with underscores
    df.columns = df.columns.str.replace('.', '_')
    df.columns = df.columns.str.replace('value_', '')
    
    # Remove the 'LandedCost_CostLines' column
    # df = df.drop(columns=['LandedCost_CostLines'])

    # Add 'id' column with generated UUIDs
    df['id'] = [uuid.uuid4() for _ in range(len(df))]
    df['id'] = df['id'].astype(str)

    # Add 'source_file' column with the name of the file
    df['source_file'] = file_name.replace('.json', '')
    
    # Display the DataFrame
    with open('data_types.txt', 'w') as f:
        for col, dtype in df.dtypes.items():
            f.write(f'{col}: {dtype}\n')
    return df

def data_insert(table_name, db_name, df):
    try:
        conn = cls.clickhouse_connect()
        # conn.clickhouse_truncate(db_name, table_name)
        conn.clickhouse_insert(table_name, db_name, df)
        print(f'data has been successfully inserted into table : {db_name}.{table_name}')
        conn.close()
    except Exception as e:
        print("Exception raised for def data_insert method  - {}".format(str(e)))


#out_df = process_pdn('EGY.json')
#print(out_df.columns)
#print(out_df.dtypes)
#print(out_df.head())

data_insert('purchase_delivery_notes', 'cptdg_db', process_pdn('NGA.json'))

# Example usage

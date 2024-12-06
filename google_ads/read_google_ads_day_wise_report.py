import pandas as pd
import uuid
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

# Define the file path to your CSV file
file_path = 'Campaign performance.csv'

# Load the CSV file, skipping the first two lines to ignore metadata
data = pd.read_csv(file_path, skiprows=2)

# Rename the columns to follow snake_case conventions
data.columns = [
    "campaign",
    "campaign_state",
    "campaign_type",
    "report_date",
    "clicks",
    "impressions",
    "ctr",
    "currency_code",
    "avg_cpc",
    "cost",
    "impr_abs_top_pct",
    "impr_top_pct",
    "conversions",
    "view_through_conversions",
    "cost_per_conversion",
    "conversion_rate",
]

# Convert the 'day' column to proper datetime format (yyyy-mm-dd)
data['report_date'] = pd.to_datetime(data['report_date']).dt.strftime('%Y-%m-%d')

# Add a new column with unique UUIDs for each row
data['id'] = [str(uuid.uuid4()) for _ in range(len(data))]

# Display the first few rows of the updated DataFrame
#print(data.head())
# Convert all columns except 'report_date' and 'cost' to string
columns_to_convert = data.columns.difference(['report_date', 'cost'])
data[columns_to_convert] = data[columns_to_convert].astype(str)
print(data.dtypes)

data_insert('google_ads_day_wise', 'cptdg_db', data)
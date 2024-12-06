import pandas as pd
import sys
import os
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


def load_excel_data(file_path: str, sheet_name: str = 'MOJAA CP') -> pd.DataFrame:
    """
    Load data from the specified Excel file and sheet into a pandas DataFrame and rename columns.
    
    :param file_path: Path to the Excel file.
    :param sheet_name: Name of the sheet to read (default is 'MOJAA CP').
    :return: DataFrame containing the data.
    """
    try:
        # Load the data from the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
        
        # Define the column name mapping
        column_mapping = {
            'Tracking Number': 'tracking_number',
            'Parcel Number': 'parcel_number',
            'Destinataire': 'recipient_name',
            'Email': 'email',
            'GSM': 'gsm_number',
            'carrier_pickup_date_time': 'carrier_pickup_datetime',
            'carrier_first_attempt_date_time': 'carrier_first_attempt_datetime',
            'carrier_delivery_date_time': 'carrier_delivery_datetime',
            'carrier_Return_date_time': 'carrier_return_datetime',
            'carrier_status_code': 'carrier_status_code',
            'Carrier Macro Status': 'carrier_macro_status',
            'carrier_current_status_date_time': 'carrier_status_datetime',
            'carrier_chargable_weight': 'carrier_chargeable_weight',
            'Tier': 'tier',
            'Poids': 'weight',
            'Ville': 'city',
            'Zone': 'zone',
            'Mode paiement': 'payment_mode',
            'carrier_second_attempt_date': 'carrier_second_attempt_date',
            'carrier_third_attempt_date': 'carrier_third_attempt_date',
            'Montant Colis': 'parcel_value',
            'N°Virement': 'transfer_number',
            'Date Virement': 'transfer_date',
            'Montant Remboursé': 'amount_refunded',
            'Return/Order': 'return_or_order'
        }
        
        # Rename the columns
        df.rename(columns=column_mapping, inplace=True)

        # Transform 'carrier_pickup_datetime' to datetime, if error or null then make the value null
        date_columns = [
            'carrier_pickup_datetime',
            'carrier_first_attempt_datetime',
            'carrier_delivery_datetime',
            'carrier_return_datetime',
            'carrier_status_datetime',
            'carrier_second_attempt_date',
            'carrier_third_attempt_date',
            'transfer_date'
        ]
        
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Transform 'parcel_value', 'weight', and 'carrier_chargeable_weight' to decimal
        decimal_columns = ['parcel_value', 'weight', 'carrier_chargeable_weight']
        
        for col in decimal_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Add a column 'updated_at' with the current timestamp
        df['updated_at'] = pd.Timestamp.now()
        return df
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        return None

# Example usage
file_path = 'MOJAA_ColisPrive.xlsx'
data_df = load_excel_data(file_path)

# Display the first few rows of the data to verify
if data_df is not None:
    print(data_df.columns)
    print(data_df.shape)
    #print(data_df.dtypes)
    data_insert('colis_prive_file_data', 'cptdg_db', data_df)

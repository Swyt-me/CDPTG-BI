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


def read_colis_prive_file(file_path):
    try:
        df = pd.read_csv(file_path, delimiter=',',dtype=str)
        print("Column names:", df.columns.tolist())
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
            'Montant Remboursé': 'amount_refunded'
        }

        df.rename(columns=column_mapping, inplace=True)

        print("Renamed columns:", df.columns.tolist())

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

        decimal_columns = ['parcel_value', 'weight', 'carrier_chargeable_weight']
        
        for col in decimal_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Add a column 'updated_at' with the current timestamp
        df['updated_at'] = pd.Timestamp.now()
        df['return_or_order'] = 'Order'
        return df
    except Exception as e:
        print("Exception raised while reading the file - {}".format(str(e)))

file_path = 'CP_Mojaa_2024120510.txt'

data_df = read_colis_prive_file(file_path)

if data_df is not None:
    print(data_df.columns)
    print(data_df.shape)
    #print(data_df.dtypes)
    data_insert('colis_prive_file_data', 'cptdg_db', data_df)
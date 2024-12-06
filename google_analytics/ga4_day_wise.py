from google.analytics.data_v1beta import BetaAnalyticsDataClient

from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import os 
import pandas as pd
import uuid
from datetime import datetime
import clickhouse_db_conn_cls as cls
from datetime import timedelta
import time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "CPDTG-ce9f7d06fe2a.json"

def sample_run_report(start_date, end_date):
    """Runs a report on a Google Analytics 4 property including sessions, engaged sessions, purchases, purchase revenue, and currency."""
    property_id = "436438208"

    # Initialize Google Analytics Data client
    client = BetaAnalyticsDataClient()

    # Define the report request with necessary dimensions and metrics
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="date"),
            #Dimension(name="currencyCode"),
            #Dimension(name="sessionDefaultChannelGroup"),
            #Dimension(name="sessionCampaignName"),
            #Dimension(name="sessionGoogleAdsCampaignName"),
            #Dimension(name="sessionSourcePlatform"),
            #Dimension(name="sessionSourceMedium"),
            #Dimension(name="sessionSource"),
            #Dimension(name="eventName"), 
           

        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),        
            Metric(name="screenPageViews"),        
            Metric(name="addtoCarts"),
            Metric(name="keyEvents:add_to_cart"),
            Metric(name="checkouts"), 
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
            Metric(name="grossPurchaseRevenue"),
            Metric(name="averageSessionDuration"),

            ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
    )

    # Run the report
    response = client.run_report(request)

    # Prepare a DataFrame to store the results
    data = []
    for row in response.rows:
        dimensions = [dim_value.value for dim_value in row.dimension_values]
        metrics = [metric_value.value for metric_value in row.metric_values]
        data.append(dimensions + metrics)

    #print(data)
    # Convert RepeatedComposite objects to lists before concatenating
    dimension_headers = list(response.dimension_headers)
    metric_headers = list(response.metric_headers)
    # Create DataFrame with appropriate column names
    column_headers = [header.name for header in dimension_headers + metric_headers]
    df = pd.DataFrame(data, columns=column_headers)

    # Process the DataFrame
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df.rename(columns={'date': 'ga_date'}, inplace=True)
    df['ga_date'] = df['ga_date'].astype(str)

    numeric_columns = [
        'sessions', 'engagedSessions', 
        'screenPageViews', 'addtoCarts','keyEvents:add_to_cart','checkouts'
        ,'ecommercePurchases','purchaseRevenue','grossPurchaseRevenue'
    ]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    df.rename(columns={'keyEvents:add_to_cart': 'keyEvents_add_to_cart'}, inplace=True)

    df['id'] = [uuid.uuid4() for _ in range(len(df))]
    df['id'] = df['id'].astype(str)

    today = datetime.today().strftime('%Y-%m-%d')
    df['created_at'] = today
    df['updated_at'] = today

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


start_date = datetime.strptime("2024-12-05", "%Y-%m-%d")
end_date = datetime.strptime("2024-12-05", "%Y-%m-%d")

current_date = start_date

while current_date <= end_date:
    start_str = current_date.strftime("%Y-%m-%d")
    end_str = current_date.strftime("%Y-%m-%d")
    
    df = sample_run_report(start_str, end_str)
    print(df)
    print(df.dtypes)
    #df.to_csv('ga_ecom_purchases_daily_details.csv', index=False)   
    data_insert('ga_day_wise', 'cptdg_db', df)
    
    current_date += timedelta(days=1)
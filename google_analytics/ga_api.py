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

def sample_run_report(start_date,end_date):
    #print(start_date)
    #print(end_date)
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Uncomment this variable and replace with your
    #  Google Analytics 4 property ID before running the sample.
    property_id = "436438208"

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="date"),
            Dimension(name="defaultChannelGroup"),
            Dimension(name="campaignName"),
            Dimension(name="medium"),
            Dimension(name="source"),
            #Dimension(name="sourceMedium"),
            #Dimension(name="googleAdsCampaignName"),
            #Dimension(name="googleAdsCampaignType"),
            #Dimension(name="manualCampaignName"),
            #Dimension(name="primaryChannelGroup")
            
            #manualMedium
            #manualSource
            #manualSourceMedium
            #manualSourcePlatform
            #sourcePlatform
            #pageReferrer
            #primaryChannelGroup
            #sessionCampaignName
            #searchTerm
            #sessionManualCampaignName

            ],
        metrics=[
            #Metric(name="screenPageViews")
            Metric(name="sessions")
            ,Metric(name="engagedSessions")
            #,Metric(name="engagementRate")
            ,Metric(name="totalUsers")
            #,Metric(name="totalRevenue")
            ,Metric(name="cartToViewRate")
            ,Metric(name="activeUsers")
            #,Metric(name="purchaserRate")
            #,Metric(name="purchaseToViewRate")
            ,Metric(name="sessionsPerUser")
            
            ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
    )
    response = client.run_report(request)
    
    df = pd.DataFrame()
    #print(response.rows)

    print("Report result:")
    for row in response.rows:
        data = []
        #print("here")
        #print(row)
        #break
        # Extract the dimension headers and metric headers
        dimension_headers = [header.name for header in response.dimension_headers]
        metric_headers = [header.name for header in response.metric_headers]

        # Prepare the data for the DataFrame
        dimensions = [dimension_value.value for dimension_value in row.dimension_values]
        metrics = [metric_value.value for metric_value in row.metric_values]
        data.append(dimensions + metrics)
        temp_df = pd.DataFrame(data, columns=dimension_headers + metric_headers)
        df = pd.concat([df, temp_df], ignore_index=True)
        #print("df shape is ::")
        #print(df.shape)

        # Create the DataFrame
    #df = pd.DataFrame(data, columns=dimension_headers + metric_headers)
    print("columns are ::")
    print(df.columns)
    # Convert the 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    # Convert specified columns to integer
    # Rename 'date' to 'ga_date' and change to string type
    df.rename(columns={'date': 'ga_date'}, inplace=True)
    df['ga_date'] = df['ga_date'].astype(str)

    # Change specified columns to string type
    string_columns = [
        'defaultChannelGroup', 'campaignName', 'sourceMedium', 
        'googleAdsCampaignName', 'googleAdsCampaignType', 
        'manualCampaignName', 'primaryChannelGroup'
    ]
    #df[string_columns] = df[string_columns].astype(str)

    # Change specified columns to numeric type
    numeric_columns = [
        'sessions', 'engagedSessions', 
        'totalUsers', 'cartToViewRate', 
        'activeUsers',  
        'sessionsPerUser'
    ]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    # Add 'id' column with generated UUIDs
    df['id'] = [uuid.uuid4() for _ in range(len(df))]
    # Cast 'id' column to string
    df['id'] = df['id'].astype(str)

    # Add 'created_at' and 'updated_at' columns with today's date
    today = datetime.today().strftime('%Y-%m-%d')
    df['created_at'] = today
    df['updated_at'] = today
    #print(df.dtypes)
    return df

    #df.to_csv('data.csv', index=False)
        #print(row.dimension_values[0].value, row.metric_values[0].value)



def data_insert(table_name, db_name, df):
    try:
        conn = cls.clickhouse_connect()
        # conn.clickhouse_truncate(db_name, table_name)
        conn.clickhouse_insert(table_name, db_name, df)
        print(f'data has been successfully inserted into table : {db_name}.{table_name}')
        conn.close()
    except Exception as e:
        print("Exception raised for def data_insert method  - {}".format(str(e)))

start_date = datetime(2024, 6, 1)
end_date = datetime.today()
#start_date = datetime(2024, 11, 9)
#end_date = datetime(2024, 11, 1)

current_start_date = start_date

while current_start_date < end_date:
    current_end_date = current_start_date + timedelta(days=6)
    if current_end_date > end_date:
        current_end_date = end_date

    data_df = sample_run_report(current_start_date.strftime('%Y-%m-%d'), current_end_date.strftime('%Y-%m-%d'))
    data_insert('ga_sessions_data', 'cptdg_db', data_df)
    #print("Data Frame is ::")
    #print(data_df.dtypes)

    current_start_date = current_end_date + timedelta(days=1)
    time.sleep(5)
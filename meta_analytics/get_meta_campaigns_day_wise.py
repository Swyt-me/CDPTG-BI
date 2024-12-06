import requests
from datetime import datetime, timedelta
import pandas as pd
import clickhouse_db_conn_cls as cls

ACCESS_TOKEN = 'EAAMZBjl1pPl0BO3R1NZB0ICkyVllhv7Vw4Ihn13jyEfUYAiunzmVZCYChzGZBZAhbHomnnaZCiS7hA1qmYSZAXCp0sp3ByQ0AAZB8buUjcZCZBitHbqtrZCViZAVZCbzUTLa3QrX1iIGzIKfYGyCa4RM2wVoKdavBlYxXyklBV8fWeFGdsmDeKHdxxLRzSz00imsZD'
AD_ACCOUNT_ID = 'act_1454383668527984'
BASE_URL = 'https://graph.facebook.com/v21.0'

def data_insert(table_name, db_name, df):
    try:
        conn = cls.clickhouse_connect()
        # conn.clickhouse_truncate(db_name, table_name)
        conn.clickhouse_insert(table_name, db_name, df)
        print(f'data has been successfully inserted into table : {db_name}.{table_name}')
        conn.close()
    except Exception as e:
        print("Exception raised for def data_insert method  - {}".format(str(e)))



# Step 1: Get Campaigns
def get_campaigns(ad_account_id):
    url = f"{BASE_URL}/{ad_account_id}/campaigns"
    params = {
        'fields': 'id,name,objective,start_time,status,lifetime_budget,budget_remaining,spend_cap,created_time,updated_time,currency',
        'access_token': ACCESS_TOKEN
    }

    campaigns = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            #print(data)
            campaigns.extend(data['data'])
            if 'paging' in data and 'next' in data['paging']:
                url = data['paging']['next']
            else:
                break
        else:
            print("Error fetching campaigns:", response.json())
            break
    return campaigns

# Step 2: Get Insights for a Campaign
import requests

# Step 2: Get Insights for a Campaign
def get_campaign_insights(campaign_id, start_date, end_date):
    url = f"{BASE_URL}/{campaign_id}/insights"
    params = {
        'fields': 'account_currency,impressions,cpm,ctr,clicks,spend,cpc,date_start,date_stop,actions',
        'time_range[since]': start_date,
        'time_range[until]': end_date,
        'time_increment': 1,
        'breakdowns': 'publisher_platform',
        'access_token': ACCESS_TOKEN
    }
    insights = []
    parsed_insights = []
    
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            #print(data)
            insights.extend(data.get('data', []))
            
            # Parse insights to extract purchase actions
            for insight in data.get('data', []):
                action_values = {}

                if 'actions' in insight:
                    for action in insight['actions']:
                        action_type = action['action_type']
                        action_value = action['value']
                        action_values[action_type] = action_value

                
                # Add parsed insight to the result
                parsed_insights.append({
                    'impressions': insight.get('impressions'),
                    'cpm': insight.get('cpm'),
                    'ctr': insight.get('ctr'),
                    'clicks': insight.get('clicks'),
                    'spend': insight.get('spend'),
                    'cpc': insight.get('cpc'),
                    'date_start': insight.get('date_start'),
                    'date_stop': insight.get('date_stop'),
                    'publisher_platform': insight.get('publisher_platform'),
                    'account_currency': insight.get('account_currency'),
                    'omni_add_to_cart': action_values.get('omni_add_to_cart', 0),
                    'omni_initiated_checkout': action_values.get('omni_initiated_checkout', 0),
                    'landing_page_view': action_values.get('landing_page_view', 0),
                    'add_to_cart': action_values.get('add_to_cart', 0),
                    'onsite_web_app_add_to_cart': action_values.get('onsite_web_app_add_to_cart', 0),
                    'onsite_web_add_to_cart': action_values.get('onsite_web_add_to_cart', 0),
                    'onsite_web_initiate_checkout': action_values.get('onsite_web_initiate_checkout', 0),
                    'offsite_conversion.fb_pixel_add_to_cart': action_values.get('offsite_conversion.fb_pixel_add_to_cart', 0),
                    'offsite_conversion.fb_pixel_initiate_checkout': action_values.get('offsite_conversion.fb_pixel_initiate_checkout', 0),
                    'initiate_checkout': action_values.get('initiate_checkout', 0),
                    'web_in_store_purchase': action_values.get('web_in_store_purchase', 0),
                    'onsite_web_purchase': action_values.get('onsite_web_purchase', 0),
                    'onsite_web_app_purchase': action_values.get('onsite_web_app_purchase', 0),
                    'purchase': action_values.get('purchase', 0),
                    'offsite_conversion.fb_pixel_purchase': action_values.get('offsite_conversion.fb_pixel_purchase', 0),
                    'omni_purchase': action_values.get('omni_purchase', 0),
                })
            
            # Handle pagination
            if 'paging' in data and 'cursors' in data['paging'] and 'after' in data['paging']['cursors']:
                params['after'] = data['paging']['cursors']['after']
            else:
                break
        else:
            print(f"Error fetching insights for campaign {campaign_id}:", response.json())
            break
    
    return parsed_insights



# Step 3: Generate Report for the Last 30 Days
def generate_report(ad_account_id):
    # Define the date range for the last 30 days
    end_date = datetime(2024, 12, 5).date()
    start_date = datetime(2024, 6, 1).date()

    # Fetch all active campaigns
    campaigns = get_campaigns(ad_account_id)
    #print(campaigns)

    # Create a DataFrame of the campaigns
    df_campaigns = pd.DataFrame(campaigns)
    #print(df_campaigns)
    
    df_campaigns['channel'] = 'Meta'
    
    df_campaigns['start_time'] = pd.to_datetime(df_campaigns['start_time']).dt.tz_localize(None)
    df_campaigns['created_time'] = pd.to_datetime(df_campaigns['created_time']).dt.tz_localize(None)
    df_campaigns['updated_time'] = pd.to_datetime(df_campaigns['updated_time']).dt.tz_localize(None)
    
    df_campaigns = df_campaigns.astype({
        'id': 'string',
        'name': 'string',
        'objective': 'string',
        'start_time': 'datetime64[ns]',
        'status': 'string',
        'budget_remaining': 'float',
        'created_time': 'datetime64[ns]',
        'updated_time': 'datetime64[ns]',
        'lifetime_budget': 'float',
        'channel': 'string'
    })
    #print(df_campaigns.dtypes)

    #df_campaigns.to_csv('campaigns.csv', index=False)
    data_insert('meta_campaigns', 'cptdg_db', df_campaigns)

    report = []

    

    # Fetch daily insights for each campaign
    for campaign in campaigns:
        campaign_id = campaign['id']
        campaign_name = campaign['name']

        
        # Fetch insights data for the last 30 days
        insights = get_campaign_insights(campaign_id, start_date.isoformat(), end_date.isoformat())
        #break
        # Compile report rows
        for data in insights:
            report.append({
                'report_date': data['date_start'],
                'campaign_id': campaign_id,
                'campaign_name': campaign_name,
                'impressions': data.get('impressions', 0),
                'cpm': data.get('cpm', 0),
                'ctr_perc': data.get('ctr', 0),
                'clicks': data.get('clicks', 0),
                'total_marketing_costs': data.get('spend', 0),
                'cpc': data.get('cpc', 0),
                'publisher_platform': data.get('publisher_platform', 0),
                'account_currency': data.get('account_currency', 0),
                'omni_add_to_cart': data.get('omni_add_to_cart', 0),
                'omni_initiated_checkout': data.get('omni_initiated_checkout', 0),
                'landing_page_view': data.get('landing_page_view', 0),
                'add_to_cart': data.get('add_to_cart', 0),
                'onsite_web_app_add_to_cart': data.get('onsite_web_app_add_to_cart', 0),
                'onsite_web_add_to_cart': data.get('onsite_web_add_to_cart', 0),
                'onsite_web_initiate_checkout': data.get('onsite_web_initiate_checkout', 0),
                'offsite_conversion.fb_pixel_add_to_cart': data.get('offsite_conversion.fb_pixel_add_to_cart', 0),
                'offsite_conversion.fb_pixel_initiate_checkout': data.get('offsite_conversion.fb_pixel_initiate_checkout', 0),
                'initiate_checkout': data.get('initiate_checkout', 0),
                'web_in_store_purchase': data.get('web_in_store_purchase', 0),
                'onsite_web_purchase': data.get('onsite_web_purchase', 0),
                'onsite_web_app_purchase': data.get('onsite_web_app_purchase', 0),
                'offsite_conversion.fb_pixel_purchase': data.get('offsite_conversion.fb_pixel_purchase', 0),
                'omni_purchase': data.get('omni_purchase', 0),
                'purchases': data.get('purchase', 0)
            })

    
    #return report
    # Convert the report list to a DataFrame
    df_report = pd.DataFrame(report)
    df_report = df_report.astype({
        'report_date': 'datetime64[ns]',
        'campaign_id': 'string',
        'campaign_name': 'string',
        'impressions': 'float',
        'cpm': 'float',
        'ctr_perc': 'float',
        'clicks': 'int',
        'total_marketing_costs': 'float',
        'cpc': 'float',
        'purchases': 'float',
        'publisher_platform': 'string',
        'account_currency': 'string',
        'omni_add_to_cart': 'float',
        'omni_initiated_checkout': 'float',
        'landing_page_view': 'float',
        'add_to_cart': 'float',
        'onsite_web_app_add_to_cart': 'float',
        'onsite_web_add_to_cart': 'float',
        'onsite_web_initiate_checkout': 'float',
        'offsite_conversion.fb_pixel_add_to_cart': 'float',
        'offsite_conversion.fb_pixel_initiate_checkout': 'float',
        'initiate_checkout': 'float',
        'web_in_store_purchase': 'float',
        'onsite_web_purchase': 'float',
        'onsite_web_app_purchase': 'float',
        'offsite_conversion.fb_pixel_purchase': 'float',
        'omni_purchase': 'float'
    })
    #print(df_report.dtypes)
    data_insert('meta_campaign_insights', 'cptdg_db', df_report)
    return df_report


# Step 4: Run the Report for Last 30 Days and Print
job_status = 'success'
status_json = {'ingest_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                , 'status': job_status
                ,'methord' : 'meta ads'
                
                }
try:
    report_df = generate_report(AD_ACCOUNT_ID)
except Exception as e:
    print("Exception raised for def generate_report method  - {}".format(str(e)))
    job_status = 'failed'
finally:
    print('Process Completed')
    status_json = {'ingest_date': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                , 'status': job_status
                ,'methord' : 'meta ads'
                
                }
    
    #data_insert('health_table', 'cptdg_db', pd.DataFrame([status_json]))

#report_df.to_csv('meta_campaign_insights.csv', index=False)

#print(report_df)


#print(get_campaign_insights('120212982414660790', '2024-11-01', '2024-11-01'))
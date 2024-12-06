#----------------first run this command on terminal    python3 notebooks/clickhouse_db_conn_cls.py 

import logging
logging.basicConfig(filename="std.log", 
					format='%(asctime)s %(message)s', 
					filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# logger.info()

import pandas as pd
from clickhouse_driver import Client
import pandahouse as ph
import os
import warnings
import traceback
# warnings.filterwarnings('ignore')
import time

class clickhouse_connect:

    def __init__(self):
        df = pd.read_json('configuration.json', typ='dataframe')
        dict1 = df.to_dict()
        self.db_user = dict1.get('CH_USER_CD')
        self.db_passwd = dict1.get('CH_PWD_CD')
        self.db_name_ops = dict1.get('CH_DBNAME_OPS_CD')
        self.db_name = dict1.get('CH_DBNAME_CD')
        self.db_port = int(dict1.get('CH_PORT_CD'))
        self.db_host = dict1.get('CH_HOST_CD')
        self.url_db_host = f'''http://{dict1.get('CH_HOST_CD')}{int(dict1.get('CH_PORT_CD'))}'''
        self.client = None
        self.connect()


    def connect(self):
        maxTries=5
        trial=0
        while True:
            trial +=1
            try:
                logger.info("trying to connect to sql")
                # print("trying to connect to sql")
                self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
                break
            except Exception as e:
                # print("unable to connect-{}".format(str(e)))
                logger.error("unable to connect-{}".format(str(e)))
            if trial>maxTries:
                print("sql conn failed")
                logger.error("sql conn failed")
                raise Exception("sql conn failed")
                break

    def run(self,query):
        try:
            self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
            df = self.client.query_dataframe(query)            
            return df 
        except Exception as e:
            # print("unable to connect-{}".format(str(e)))
            logger.error("unable to connect-{}".format(str(e)))
            time.sleep(5)
            self.connect()
            try:
                time.sleep(5)
                self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
                df = self.client.query_dataframe(query) 
                return df
            except Exception as e:
                # print("exception raised on run methord unable to connect-{}".format(str(e)))
                logger.error("exception raised on run methord unable to connect-{}".format(str(e)))
                return None        

    def clickhouse_insert(self,table_name,db_name,mysql_table_data_df):  
            try :
                # insert the data into collegedekho_ops database in temp tables

                    # connection = dict(database=db_name,
                    #                 host=self.url_db_host,
                    #                 user=self.db_user,
                    #                 password=self.db_passwd)    
                    # ph.to_clickhouse(mysql_table_data_df, table_name, index=False, chunksize=100000, connection=connection)
                # col_list = list(mysql_table_data_df.columns)    
                self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd,database = db_name,settings={'use_numpy': True})    
                self.client.insert_dataframe(f'INSERT INTO {db_name}.{table_name} VALUES', mysql_table_data_df)    
                # print('Insert sussessfully to clickhouse')
                logger.info("Insert sussessfully to clickhouse")
            except Exception as e:
                    print(e)
                    # print("exception raised on clickhouse_insert methord unable to connect-{}".format(str(e)))
                    logger.error("exception raised on clickhouse_insert methord unable to connect-{}".format(str(e)))
                    return None         


    def clickhouse_custom_insert(self,table_name,mysql_table_data_df):  
            try :
                # insert the data into collegedekho_ops database in temp tables
                    table_name1 = table_name+'_str'
                    # connection = dict(database=self.db_name_ops,
                    #                 host=self.url_db_host,
                    #                 user=self.db_user,
                    #                 password=self.db_passwd)    
                    # ph.to_clickhouse(mysql_table_data_df, table_name1, index=False, chunksize=100000, connection=connection)
                    # col_list = list(mysql_table_data_df.columns)
                    query = ""
                    self.clickhouse_delete(self.db_name,table_name,query)    

                    db_name_ops = f'{self.db_name}_ops'
                    table_name_ops = f'{table_name}_str'
                    self.clickhouse_truncate(db_name_ops,table_name_ops)   

                    logger.info(f'from clickhouse_custom_insert methord Data has been sucessfully deleted from table {table_name}')

                    self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd,database = self.db_name,settings={'use_numpy': True})  
                    self.client.insert_dataframe(f'INSERT INTO {self.db_name_ops}.{table_name1} VALUES', mysql_table_data_df)   
                    logger.info(f'from clickhouse_custom_insert methord Insert sussessfully to clickhouse for table {table_name1} and count is : {mysql_table_data_df.count()}')

                    self.clickhouse_final_insert(table_name,self.db_name)
            except Exception as e:
                    # print("exception raised on clickhouse_custom_insert methord unable to connect-{}".format(str(e)))
                    logger.error("exception raised on clickhouse_custom_insert methord  unable to connect-{}".format(str(e)))
                    return None         


    def clickhouse_delete(self,db_name,table_name,query):  
        try:
            #-----------if query is blank then it deletes today's ingested data------------------
            self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd,database = self.db_name)
            if query == "" :
                # query = f"""
                #                 ALTER TABLE {db_name}.{table_name} DELETE where Date(ingested_at,'Asia/Calcutta') =  toDate(today(),'Asia/Calcutta')
                #         """
                query = f"""
                                ALTER TABLE {db_name}.{table_name} DELETE where id in 
                                (select id from {db_name}_ops.{table_name}_str );
                        """                
            self.client.execute(query)
            # time.sleep(6)
            logger.info(f'query of delete statement is {query}')
            logger.info(f'Data has been sucessfully deleted from table {table_name}')
        except Exception as e:
                    # print("exception raised on clickhouse_delete methord unable to connect-{}".format(str(e)))
                    logger.error("exception raised on clickhouse_delete methord unable to connect-{}".format(str(e)))
                    return None  

    def clickhouse_truncate(self,db_name,table_name):  
            #-----------excutes the truncate table command on given db and table_name------------------
        try:
            self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
                # truncate table {db_name}_ops.{table_name}_str
            query = f"""
                        truncate table {db_name}.{table_name}
                    """
            self.client.execute(query)
            logger.info(f'table {table_name} has been sucessfully truncated ')
        except Exception as e:
                    # print("exception raised on clickhouse_truncate methord unable to connect-{}".format(str(e)))
                    logger.error("exception raised on clickhouse_truncate methord uunable to connect-{}".format(str(e)))
                    self.clickhouse_DML_OPS(query)
                    return None  

#--------------------this function is currently not in use------------------------------------------------------
    def clickhouse_final_insert(self,table_name,db_name):  
            #-----------It inserts the data into collegedeko db's table and truncate the str table of collegedekho_ops db ---   
        try:
            # db_name_ops = f'{db_name}_ops'
            # table_name_ops = f'{table_name}_str'
            # self.clickhouse_truncate(db_name_ops,table_name_ops) 

            # query = ""
            # self.clickhouse_delete(db_name,table_name,query)            
            self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
            query = f"""
                        insert into {db_name}.{table_name}
                        select * from {db_name}_ops.{table_name}_str
                            """
            self.client.execute(query)
            logger.info(f'''Insert sussessfully to clickhouse in final_table {db_name}.{table_name}''')

            # db_name_ops = f'{db_name}_ops'
            # table_name_ops = f'{table_name}_str'
            # self.clickhouse_truncate(db_name_ops,table_name_ops)       
        except Exception as e:
                    print("exception raised on clickhouse_final_insert methord unable to connect-{}".format(str(e)))
                    # logger.error("unable to connect-{}".format(str(e)))
                    return None      
#------------------------------------------------------------------------------------------------------------

    def clickhouse_final_update(self,table_name,db_name,mysql_table_data_df):
    #-----------It replace the yesterday's changed data into collegedeko db's table and truncate the str table of collegedekho_ops db ---      
        try:  
            db_name_ops = f'{db_name}_ops'
            table_name_ops = f'{table_name}_str'
            
            self.clickhouse_truncate(db_name_ops,table_name_ops) 
            logger.info(f'executing clickhouse_final_update -- truncate table {table_name_ops}')

            self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd,database = db_name_ops,settings={'use_numpy': True})  
            self.client.insert_dataframe(f'INSERT INTO {db_name_ops}.{table_name_ops} VALUES', mysql_table_data_df)   
            logger.info(f'executing clickhouse_final_update Insert sussessfully to clickhouse  -- insert into table {table_name_ops}')

            del_query = f"""
                            ALTER TABLE {db_name}.{table_name} 
                            DELETE 
                            where Date(added_on) <=  today() 
                                    and id in (
                                                Select id 
                                                from {db_name}_ops.{table_name}_str 
                                            )
                        """
            self.clickhouse_delete(db_name,table_name,del_query)  
            logger.info(f'executing clickhouse_final_update -- delete from table {table_name}')

            self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
            query = f"""
                        insert into {db_name}.{table_name}
                        select * from {db_name}_ops.{table_name}_str
                            """
            self.client.execute(query)
            logger.info(f'executing clickhouse_final_update -- insert into table {table_name} from {table_name}_str')
            print('Updated sussessfully to clickhouse in final_table')
            # db_name_ops = f'{db_name}_ops'
            # table_name_ops = f'{table_name}_str'
            # self.clickhouse_truncate(db_name_ops,table_name_ops)       
        except Exception as e:
                    # print("exception raised on clickhouse_final_update methord unable to connect-{}".format(str(e)))
                    logger.error("exception raised on clickhouse_final_update methord unable to connect-{}".format(str(e)))
                    return None  
                    #         

    def max_record(self,db_name,table_name):
        try:
            # ------------populating maximum id coulm of the table from mysql
            query = ""
            self.clickhouse_delete(self.db_name,table_name,query)  

            query = f'select max(id) as max_id from {db_name}.{table_name} where Date(ingested_at) < toDate(today(),''Asia/Calcutta'')'
            clickhouse_df = self.run(query)
            max_id = int(clickhouse_df['max_id'].iloc[0])
            # print(clickhouse_df)
            return max_id
        except Exception as e:
                # print("exception raise in max_record methord ,unable to connect-{}".format(str(e)))
                logger.error("exception raise in max_record methord unable to connect-{}".format(str(e)))
                return None  
                

    def clickhouse_DML_OPS(self,dml_query):  
  
        try:
          
            self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
            self.client.execute(dml_query)
            logger.info(f'''DML query successfully executed on clickhouse ''')
       
        except Exception as e:
                    print("exception raised on clickhouse_DML_OPS methord unable to connect-{}".format(str(e)))
                    logger.error("unable to connect-{}".format(str(e)))
                    # return None   
                    time.sleep(5)
                    self.connect()
                    try:
                        time.sleep(5)
                        self.client = Client(host=self.db_host, user=self.db_user, password=self.db_passwd)
                        self.client.execute(dml_query)
                        logger.info(f'''DML query successfully executed on clickhouse on second attempt''')
                    except Exception as e:
                        # print("exception raised on run methord unable to connect-{}".format(str(e)))
                        logger.error("exception raised on run methord unable to connect-{}".format(str(e)))
                        return None                     


    # def ingest_data(self,dbname,table,dbtype,dbname2,dbname1):
    #     try:

    #         # conn = mysql_cls.mysql_connect()
    #         # col_df = conn.get_columns_df(table)
    #         # df = pd.DataFrame(['ingested_at'],columns = ['COLUMN_NAME'])
    #         # col_df.append(df)
    #         # tp1 = tuple(col_df['COLUMN_NAME'])
    #         # ch_conn = ch_cls.clickhouse_connect() 

    #         source_conn = self.source_conn_func(dbtype,dbname2,table,dbname1)

    #         query = f'''
    #                         SELECT *
    #                         ,today() as ingested_at 
    #                         FROM {source_conn}
    #                         where  id > 0 limit 10
    #                         '''
    #         col_df = self.run(query)
    #         tp1 = tuple(col_df.columns)
    #         query = f'''  
    #                         insert into {dbname}.{table}
    #                             {str(tp1).replace("'", "")} 
    #                         SELECT *
    #                         ,toDate(today(),'Asia/Calcutta') as ingested_at 
    #                         FROM {source_conn}
    #                         where id >  
    #                         ifNull(
    #                             (
    #                         select max(max_id) as dd
    #                         from collegedekho_ops.tab_max_id
    #                         where table_name = '{table}'
    #                             and dbname = '{dbname}'
    #                             and Date(ingested_at,'Asia/Calcutta') = toDate(today(),'Asia/Calcutta')
    #                             and remakrs = 'CLICKHOUSE'
    #                     )
    #                     ,0) 
    #                     and Date(added_on,'Asia/Calcutta') < toDate(today(),'Asia/Calcutta')  
    #                     '''

    #         # print('query to be executed : ' + query)              
    #         self.clickhouse_DML_OPS(query)             
    #         # print(query)         
    #     except Exception as e:
    #     # print("exception raise in tab_max_id_ops methord ,unable to connect-{}".format(str(e)))
    #         logger.error("exception raise in ingest_data methord unable to connect-{}".format(str(e)))       

 
    # def ingest_data_today(self,dbname,table,dbtype,dbname2,dbname1):
    #     try:

    #         # conn = mysql_cls.mysql_connect()
    #         # col_df = conn.get_columns_df(table)
    #         # df = pd.DataFrame(['ingested_at'],columns = ['COLUMN_NAME'])
    #         # col_df.append(df)
    #         # tp1 = tuple(col_df['COLUMN_NAME'])
    #         # ch_conn = ch_cls.clickhouse_connect() 
    #         source_conn = self.source_conn_func(dbtype,dbname2,table,dbname)
    #         query = f'''
    #                         SELECT *
    #                         ,today() as ingested_at 
    #                         FROM{source_conn}  
    #                         where  id > 0 limit 10
    #                         '''
    #         col_df = self.run(query)
    #         tp1 = tuple(col_df.columns)
    #         query = f'''  
    #                         insert into {dbname}.{table}
    #                             {str(tp1).replace("'", "")} 
    #                         SELECT *
    #                         ,toDate(today(),'Asia/Calcutta') as ingested_at 
    #                         FROM {source_conn}  
    #                         where id >  
    #                         ifNull(
    #                             (
    #                         select max(max_id) as dd
    #                         from collegedekho_ops.tab_max_id
    #                         where table_name = '{table}'
    #                             and dbname = '{dbname}'
    #                             and Date(ingested_at,'Asia/Calcutta') = toDate(today(),'Asia/Calcutta')
    #                             and remakrs = 'CLICKHOUSE_today'
    #                     )
    #                     ,0) 
    #                --     and Date(added_on,'Asia/Calcutta') < toDate(today(),'Asia/Calcutta')  
    #                     '''

    #         # print('query to be executed : ' + query)              
    #         self.clickhouse_DML_OPS(query)             
    #         # print(query)         
    #     except Exception as e:
    #     # print("exception raise in tab_max_id_ops methord ,unable to connect-{}".format(str(e)))
    #         logger.error("exception raise in ingest_data methord unable to connect-{}".format(str(e)))       

    # def temp_ingest(self,table,dbname,col_updated_on,col_added_on,dbtype,dbname2,dbname1):
    #     try:  
    #         # ch_conn = ch_cls.clickhouse_connect() 
    #         source_conn = self.source_conn_func(dbtype,dbname2,table,dbname1)
    #         # query = f'''
    #         #             SELECT *
    #         #             ,today() as ingested_at 
    #         #             FROM mysql('{self.sql_hostname}:{self.sql_port}', '{dbname}', '{table}', '{self.sql_username}', '{self.sql_password}') 
    #         #             where  id > 0 limit 10
    #         #             '''

    #         query = f'''
    #                     SELECT *
    #                     ,today() as ingested_at 
    #                     FROM {source_conn} 
    #                     where  id > 0 limit 10
    #                     '''


    #         col_df = self.run(query)
    #         tp1 = tuple(col_df.columns)
    #         # print('making tupple')
    #         query1 = f'''  
    #                         insert into {dbname}_ops.{table}_str
    #                             {str(tp1).replace("'", "")} 
    #                         SELECT *
    #                         ,toDate(today(),'Asia/Calcutta') as ingested_at 
    #                         FROM {source_conn} 
    #                         where id in  
    #                                         (
    #                                         select id 
    #                                         FROM {source_conn}  
    #                                         where id > 0 and  Date({col_updated_on},'Asia/Calcutta') >= toDate(yesterday(),'Asia/Calcutta')
    #                                     )
    #                         and Date({col_added_on},'Asia/Calcutta') < toDate(today(),'Asia/Calcutta')   
    #                     '''
    #         # print('making query1')            
    #         self.clickhouse_DML_OPS(query1) 
    #                                 # {str(tp1).replace("'", "")}

    #         query2_del = f'''
    #                     alter table {dbname}.{table}  delete where id in (select id from {dbname}_ops.{table}_str);
    #             '''
    #         # print('making query2')               
    #         self.clickhouse_DML_OPS(query2_del)     


    #         query2 = f'''
    #                     Insert into {dbname}.{table}
    #                     select * from {dbname}_ops.{table}_str;     
    #             '''
    #         # print('making query2')               
    #         self.clickhouse_DML_OPS(query2)     
    #         logger.info('table has been updated '+table)
    #     except Exception as e:
    #         # print("exception raised on clickhouse_final_update methord unable to connect-{}".format(str(e)))
    #         logger.error("exception raised on temp_ingest methord unable to connect-{}".format(str(e)))
    #         return None   

    # def temp_ingest_today(self,table,dbname,col_updated_on,col_added_on,dbtype,dbname2,dbname1):
    #     try:  
    #         # ch_conn = ch_cls.clickhouse_connect() 
    #         source_conn = self.source_conn_func(dbtype,dbname2,table,dbname1)
    #         query = f'''
    #                     SELECT *
    #                     ,today() as ingested_at 
    #                     FROM mysql('{self.sql_hostname}:{self.sql_port}', '{dbname}', '{table}', '{self.sql_username}', '{self.sql_password}') 
    #                     where  id > 0 limit 10
    #                     '''
    #         col_df = self.run(query)
    #         tp1 = tuple(col_df.columns)
    #         # print('making tupple')
    #         query1 = f'''  
    #                         insert into {dbname}_ops.{table}_str
    #                             {str(tp1).replace("'", "")} 
    #                         SELECT *
    #                         ,toDate(today(),'Asia/Calcutta') as ingested_at 
    #                         FROM {source_conn} 
    #                         where id in  
    #                                         (
    #                                         select id 
    #                                         FROM {source_conn} 
    #                                         where id > 0 and  Date({col_updated_on},'Asia/Calcutta') >= toDate(today(),'Asia/Calcutta')
    #                                     )
    #                         --and Date({col_added_on},'Asia/Calcutta') < toDate(today(),'Asia/Calcutta')   
    #                     '''
    #         # print('making query1')            
    #         self.clickhouse_DML_OPS(query1) 
    #                                 # {str(tp1).replace("'", "")}

    #         query2_del = f'''
    #                     alter table {dbname}.{table}  delete where id in (select id from {dbname}_ops.{table}_str);
    #             '''
    #         # print('making query2')               
    #         self.clickhouse_DML_OPS(query2_del)     


    #         query2 = f'''
    #                     Insert into {dbname}.{table}
    #                     select * from {dbname}_ops.{table}_str;     
    #             '''
    #         # print('making query2')               
    #         self.clickhouse_DML_OPS(query2)     
    #         logger.info('table has been updated '+table)
    #     except Exception as e:
    #         # print("exception raised on clickhouse_final_update methord unable to connect-{}".format(str(e)))
    #         logger.error("exception raised on temp_ingest_today methord unable to connect-{}".format(str(e)))
    #         return None   

    # def source_conn_func(self,dbtype,dbname2,table,dbname):
    #     try:  
    #         if dbtype == 'PGSQL':
    #             source_conn = f'''
    #             postgresql('{self.pgsql_hostname}:{self.pgsql_port}', '{dbname2}', '{table}', '{self.pgsql_username}', '{self.pgsql_password}','{dbname}')
    #             '''
    #         else :
    #              source_conn = f'''
    #              mysql('{self.sql_hostname}:{self.sql_port}', '{dbname}', '{table}', '{self.sql_username}', '{self.sql_password}')     
    #                           ''' 
    #         return source_conn             
    #     except Exception as e:
    #         # print("exception raised on source_conn_func methord unable to connect-{}".format(str(e)))
    #         logger.error("exception raised on source_conn_func methord unable to connect-{}".format(str(e)))
    #         return None      

    def close(self):
        try:
            """
            Close the connection to the ClickHouse database.
            """
            if self.client:
                self.client.disconnect()
                print("ClickHouse connection closed.")
        except Exception as e:
            print("exception raised on close methord unable to connect-{}".format(str(e)))
            logger.error("exception raised on close methord unable to connect-{}".format(str(e)))
                      
import mysql.connector                                                        
  from mysql.connector import Error                                             
  import pandas as pd                                                           
                                                                                
  # Function to connect to MySQL database                                       
  def connect_to_mysql():                                                       
      try:                                                                      
          connection = mysql.connector.connect(                                 
              host='your_host',                                                 
              user='your_username',                                             
              password='your_password',                                         
              database='your_database'                                          
          )                                                                     
          if connection.is_connected():                                         
              print('Connected to MySQL database')                              
          return connection                                                     
      except Error as e:                                                        
          print(f'Error: {e}')                                                  
          return None                                                           
                                                                                
  # Function to create a table                                                  
  def create_table(connection, create_table_sql):                               
      try:                                                                      
          cursor = connection.cursor()                                          
          cursor.execute(create_table_sql)                                      
          print('Table created successfully')                                   
      except Error as e:                                                        
          print(f'Error: {e}')                                                  
                                                                                
  # Function to insert data into a table                                        
  def insert_data(connection, df, table_name):                                  
      try:                                                                      
          cursor = connection.cursor()                                          
          for i, row in df.iterrows():                                          
              sql = f"INSERT INTO {table_name} VALUES {tuple(row)}"             
              cursor.execute(sql)                                               
          connection.commit()                                                   
          print(f'Data inserted successfully into {table_name}')                
      except Error as e:                                                        
          print(f'Error: {e}')                                                  
                                                                                
  # Main execution                                                              
  if __name__ == "__main__":                                                    
      connection = connect_to_mysql()                                           
                                                                                
      # Define table schemas (Adjust column types and names as needed)          
      user_log_table_sql = '''                                                  
      CREATE TABLE IF NOT EXISTS USER_LOG (                                     
          user_id INT,                                                          
          date DATE,                                                            
          time TIME                                                             
      )'''                                                                      
                                                                                
      activity_log_table_sql = '''                                              
      CREATE TABLE IF NOT EXISTS ACTIVITY_LOG (                                 
          component VARCHAR(255),                                               
          action VARCHAR(255)                                                   
      )'''                                                                      
                                                                                
      component_codes_table_sql = '''                                           
      CREATE TABLE IF NOT EXISTS COMPONENT_CODES (                              
          component VARCHAR(255),                                               
          code VARCHAR(255)                                                     
      )'''                                                                      
                                                                                
      # Create tables                                                           
      create_table(connection, user_log_table_sql)                              
      create_table(connection, activity_log_table_sql)                          
      create_table(connection, component_codes_table_sql)                       
                                                                                
      # Load cleaned CSV files                                                  
      user_log_df = pd.read_csv('USER_LOG_cleaned.csv')                         
      activity_log_df = pd.read_csv('ACTIVITY_LOG_cleaned.csv')                 
      component_codes_df = pd.read_csv('COMPONENT_CODES_cleaned.csv')           
                                                                                
      # Insert data into tables                                                 
      insert_data(connection, user_log_df, 'USER_LOG')                          
      insert_data(connection, activity_log_df, 'ACTIVITY_LOG')                  
      insert_data(connection, component_codes_df, 'COMPONENT_CODES')            
  '''                                                                           
                                                                                
  # Append the extended code to the script                                      
  with open('backup_to_mysql.py', 'a') as file:                                 
      file.write(extended_code)                                                 
                                 
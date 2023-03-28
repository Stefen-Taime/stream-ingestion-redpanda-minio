import random
import uuid
from faker import Faker
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Number of data points to generate
num_records = 1000

# Generate synthetic data
data = []

for _ in range(num_records):
    unique_id = str(uuid.uuid4())
    plate_number = f"{random.randint(1000, 9999)}-{fake.random_element(elements=('AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG', 'HHH', 'III', 'JJJ', 'KKK', 'LLL', 'MMM', 'NNN', 'OOO', 'PPP', 'QQQ', 'RRR', 'SSS', 'TTT', 'UUU', 'VVV', 'WWW', 'XXX', 'YYY', 'ZZZ'))}"
    
    car_info = {
        "make": fake.random_element(elements=("Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "Volkswagen", "BMW", "Mercedes-Benz")),
        "year": random.randint(2000, 2023)
    }
    
    owner_info = {
        "name": fake.name(),
        "address": fake.address(),
        "phone_number": fake.phone_number().replace("x", " ext. ")  # Modify phone number format
    }
    
    subscription_status = fake.random_element(elements=("active", "expired", "none"))
    
    if subscription_status != "none":
        subscription_start = fake.date_between(start_date='-3y', end_date='today')
        subscription_end = subscription_start + timedelta(days=365)
    else:
        subscription_start = None
        subscription_end = None

    balance = round(random.uniform(0, 500), 2)
    
    timestamp = fake.date_time_between(start_date='-30d', end_date='now').strftime('%Y-%m-%d %H:%M:%S')

    
    record = {
        "id": unique_id,
        "plate_number": plate_number,
        "car_make": car_info["make"],
        "car_year": car_info["year"],
        "owner_name": owner_info["name"],
        "owner_address": owner_info["address"],
        "owner_phone_number": owner_info["phone_number"],
        "subscription_status": subscription_status,
        "subscription_start": subscription_start,
        "subscription_end": subscription_end,
        "balance": balance,
        "timestamp": timestamp
    }
    
    data.append(record)

# Convert data to a pandas DataFrame
df = pd.DataFrame(data)

# Connect to the MySQL database
db_config = {
    "host": "mysql",
    "user": "root",
    "password": "debezium",
    "database": "inventory"
}
conn = mysql.connector.connect(**db_config)

# Create a cursor
cursor = conn.cursor()

# Create the 'customers' table if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(255) NOT NULL,
    plate_number VARCHAR(255) NOT NULL,
    car_make VARCHAR(255) NOT NULL,
    car_year INT NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    owner_address TEXT NOT NULL,
    owner_phone_number VARCHAR(255) NOT NULL,
    subscription_status ENUM('active', 'expired', 'none') NOT NULL,
    subscription_start DATE,
    subscription_end DATE,
    balance DECIMAL(10, 2) NOT NULL,
    timestamp TIMESTAMP NOT NULL
)
'''
cursor.execute(create_table_query)

# Store the synthetic data in the 'customers' table
for index, row in df.iterrows():
    insert_query = '''
    INSERT INTO customers (id, plate_number, car_make, car_year, owner_name, owner_address, owner_phone_number, subscription_status, subscription_start, subscription_end, balance, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query, (
        row['id'],
        row['plate_number'],
        row['car_make'],
        row['car_year'],
        row['owner_name'],
        row['owner_address'],
        row['owner_phone_number'],
        row['subscription_status'],
        row['subscription_start'],
        row['subscription_end'],
        row['balance'],
        row['timestamp']
    ))

# Commit the changes and close the cursor
conn.commit()
cursor.close()

# Close the database connection
conn.close()

print("Synthetic data stored in the 'customers' table in the MySQL database")

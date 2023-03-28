from flask import Flask, request, jsonify, render_template
import mysql.connector
import pandas as pd

app = Flask(__name__, template_folder='template')

db_config = {
        "host": "10.0.0.25",
        "user": "root",
        "password": "debezium",
        "database": "inventory"
    }

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.get_json()

    
    conn = mysql.connector.connect(**db_config)

    cursor = conn.cursor()

    insert_query = '''
    INSERT INTO customers (id, plate_number, car_make, car_year, owner_name, owner_address, owner_phone_number, subscription_status, subscription_start, subscription_end, balance, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query, (
        data['id'],
        data['plate_number'],
        data['car_make'],
        data['car_year'],
        data['owner_name'],
        data['owner_address'],
        data['owner_phone_number'],
        data['subscription_status'],
        data['subscription_start'],
        data['subscription_end'],
        data['balance'],
        data['timestamp']
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"status": "success"}), 200

@app.route('/customers', methods=['GET'])
def customers():
    plate_number = request.args.get('plate_number', '')
    page = int(request.args.get('page', 1))
    items_per_page = 10

    conn = mysql.connector.connect(**db_config)

    # Create a cursor
    cursor = conn.cursor()

    # Fetch customers filtered by plate_number and apply pagination
    select_query = '''
    SELECT * FROM customers
    WHERE plate_number LIKE %s
    LIMIT %s OFFSET %s
    '''
    cursor.execute(select_query, (f"%{plate_number}%", items_per_page, (page - 1) * items_per_page))
    customers = cursor.fetchall()

    # Get the total number of customers
    cursor.execute("SELECT COUNT(*) FROM customers WHERE plate_number LIKE %s", (f"%{plate_number}%",))
    total_customers = cursor.fetchone()[0]

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return render_template('customers.html', customers=customers, plate_number=plate_number, page=page, total_pages=(total_customers // items_per_page) + 1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
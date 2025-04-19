# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 17:25:49 2025
@author: star26
"""

import requests
import json
import pyodbc
from datetime import datetime

# Function to convert date string to datetime object
def convert_to_datetime(date_string):
    try:
        return datetime.strptime(date_string, "%d.%m.%Y")
    except ValueError:
        print(f"Invalid date format: {date_string}")
        return None

# Function to remove metadata and store data
def process_and_store_data_in_sql(json_data, server, database, username, password):
    conn = None  # Safeguard for finally block
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};DATABASE={database};UID={username};PWD={password};"
            "Timeout=60;" 
        )
        cursor = conn.cursor()

        results = json_data.get("d", {}).get("results", [])

        for record in results:
            srno = record.get("Srno", None)
            barcode = record.get("Barcode", None)
            lidcode = record.get("Lidcode", None)
            boxcode = record.get("Boxcode", None)
            invoice = record.get("Invoice", None)
            prefix = record.get("Prefix", None)
            points = float(record.get("Points", 0.0))
            cash = float(record.get("Cash", 0.0))
            synced = int(record.get("Synced", 0))
            invoice_date = record.get("InvoiceDate", None)

            invoice_date = convert_to_datetime(invoice_date) if invoice_date else None

            query = """
            INSERT INTO qrdata1 (Srno, Barcode, Lidcode, Boxcode, Invoice, Prefix, Points, Cash, Synced, InvoiceDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, srno, barcode, lidcode, boxcode, invoice, prefix, points, cash, synced, invoice_date)

        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"An error occurred while storing data in SQL: {e}")
    finally:
        if conn:
            conn.close()

# URL to send the GET request
url = "https://cpi-nonprod-u7xwl3ag.it-cpi026-rt.cfapps.eu10-002.hana.ondemand.com/http/sendqrdata"

# SAP Basic Auth credentials
username = "S0026376022"
password = "Hexa@1000#"

headers = {
    "INVOICEDATE": "16.04.2025"
}

try:
    response = requests.get(url, headers=headers, auth=(username, password))

    if response.status_code == 200:
        try:
            data_as_variable = response.json()
            print("Data successfully fetched:")
            print(json.dumps(data_as_variable, indent=4))

            # SQL credentials
            sql_server = "192.168.172.100"
            sql_db = "CILRTL"
            sql_user = "sa"
            sql_pass = "sq"

            process_and_store_data_in_sql(data_as_variable,sql_server, sql_db, sql_user, sql_pass)

        except json.JSONDecodeError:
            print("Failed to decode JSON.")
            print(response.text)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"An error occurred: {e}")

import csv
from datetime import datetime, date
from sms import notifications
from db import database
from model import Response
import json
from dotenv import load_dotenv

def read_file(filepath):
    try:
        with open(filepath, 'r')as file:
            csv_reader = csv.DictReader(file)

            data_list = []

            for row in csv_reader:
                data_list.append(row)
        return data_list
    except FileNotFoundError:
        print(f"Error: the file '{filepath}' was not found")
        return None
    except Exception as e:
        print(f"An error ocurred while reading the file: {e}")
        return None


def guest_populate_db(records):
    """
    Input a dictionary
    Returns a list of objects
    [
        {record 1: "Record insertado correctamente"}
        },
        {record 2: "Record existente"}
        ]
    """
    counter = 0
    records_response = []
    for row in records:
        action = row['Action']
        res = ""
        item = Response.Response(counter, res)
        counter = counter + 1
        if action == 'I':
            database.guest_insert_record(row, item)
        elif action == 'D':
            database.guest_delete_record(row, item)
        elif action == 'U':
            database.guest_insert_record(row, item)

        records_response.append(item)

    database.show_guests()
    return records_response;

def get_guests():
    return database.get_all_guests()

def property_populate_db(records):
    #Iterate over the dictionary and insert into correc tables.
    database.create_db()
    for row in records:
        action = row['Action']
        if action == 'I':
            database.insert_property_record(row)
        elif action == 'D':
            database.delete_property_record(row)
    database.show_properties()



def process_data(records):
    format = "%d/%m/%Y"
    print("Today ",datetime.today().date())
    today = datetime.today().date()
    for line in records:
        #print(line['FechaDePago'])
        payment_date = line.payment_due_date # line['payment_due_date']
        guest_name = line.name
        phone_number = line.phone_number
        payment_due_date = datetime.strptime(payment_date, format).date()
        print('Payment due date ', payment_due_date)

        if payment_due_date == today:
            notifications.send_notification(guest_name,phone_number, payment_due_date)
            print(f"Message sent to {guest_name} Whatsapp {phone_number} Payment due date {payment_due_date}")
        else:
            print('Skipped for ', guest_name, " payment due date ", payment_due_date)


def run_process():
    load_dotenv()
    #Read records from the database
    guests = database.get_all_guests()
    print(type(guests))
    for guest in guests:
        print(guest)
    #Send notification
    process_data(guests)


#run_process()


#filename = "../test data/property.csv"
#filename = "../test data/guest.csv"
"""filename = ""
file_content = read_file(filename)
if 'property.csv' in filename:
    property_populate_db(file_content)
elif 'guest.csv' in filename:
    out = guest_populate_db(file_content)
    print(json.dumps([rc.__dict__ for rc in out]))
else:
    run_process()
"""
#process_data(file_content)


#run_process()

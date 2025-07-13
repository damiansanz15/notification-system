import os
import sqlite3
import traceback
from dotenv import load_dotenv
from model.Guest import Guest

def create_db():
    load_dotenv()

    try:
        database_file = os.getenv('DATABASE_FILE')
        print(database_file)
        conn = sqlite3.connect(database_file)
        cursor_obj = conn.cursor()
        table_creation_query = """
        CREATE TABLE IF NOT EXISTS GUESTS (
            id INTEGER PRIMARY KEY autoincrement,
            guest_name VARCHAR(255) NOT NULL,
            property_identifier VARCHAR(255) NOT NULL,
            room_no VARCHAR(10) NOT NULL,
            start_date VARCHAR(25) NOT NULL,
            end_date VARCHAR(25),
            phone_number VARCHAR(20),
            payment_due_date VARCHAR(20),
            payment_final_due_date VARCHAR(20),
            is_active varchar(1)
        );
        """
        cursor_obj.execute(table_creation_query)
        # Commit changes and close connection
        conn.commit()

        table_creation_query = """
        CREATE TABLE IF NOT EXISTS PROPERTY_DETAILS (
            id INTEGER PRIMARY KEY autoincrement,
            property_identifier VARCHAR(255) NOT NULL,
            room_identifier VARCHAR(10) NOT NULL,
            price VARCHAR(25),
            is_active varchar(1)
        );
        """
        cursor_obj.execute(table_creation_query)
        # Commit changes and close connection
        conn.commit()

        table_creation_query = """
        CREATE TABLE IF NOT EXISTS PAYMENT_DETAILS (
            id INTEGER PRIMARY KEY autoincrement,
            guest_id integer,
            property_id integer,
            month_paid_for VARCHAR(25),
            year_paid_for varchar(4),
            payment_method varchar(10),
            amount_paid varchar(10),
            status varchar(10)            
        );
        """
        cursor_obj.execute(table_creation_query)
        # Commit changes and close connection
        conn.commit()
        print("Database created")
    except:
        traceback.print_exc()
        print("Database not created")
    finally:
        conn.close()
        print("Connexion closed")

def update_record(row):
    name = row['GuestName']
    room_no = row['RoomNo']
    property = row['Property']
    payment_due_date = row['PaymentDueDate']
    rate_price = row['Price']
    telephone = row['Telephone']
    print(f"name : {name} room_no :{room_no} property : {property} payment_due_date : {payment_due_date} rate_price : {rate_price} telephone {telephone}")

    try:
        database_file = os.getenv('DATABASE_FILE')
        conn = sqlite3.connect(database_file)
        cursor_obj = conn.cursor()
        #Insert guest
        cursor_obj.execute(f"INSERT INTO GUESTS (guest_name,property_identifier, room_no, start_date, end_date, phone_number, payment_due_date, payment_final_due_date) VALUES ('{name}','{room_no}','{payment_due_date}','{payment_due_date}','{telephone}','{payment_due_date}','{payment_due_date}')")
        conn.commit()
        #insert property
        cursor_obj.execute(f"INSERT INTO PROPERTY_DETAILS (property_identifier, room_identifier, price, is_active) VALUES ('{property}','{room_no}','{rate_price}','Y')")
        conn.commit()

    except:
        traceback.print_exc()
        print("Database not created")
    finally:
        conn.close()
        print("Connexion closed")


def guest_insert_record(row, response):
    name = row['GuestName']
    room_no = row['RoomNo']
    property = row['Property']
    payment_due_date = row['PaymentDueDate']
    rate_price = row['Price']
    telephone = row['Telephone']
    #print(f"name : {name} room_no :{room_no} property : {property} payment_due_date : {payment_due_date} rate_price : {rate_price} telephone {telephone}")

    try:
        database_file = os.getenv('DATABASE_FILE')
        conn = sqlite3.connect(database_file)
        cursor_obj = conn.cursor()
        if find_guest(row) is None:
            cursor_obj.execute(f"INSERT INTO GUESTS (guest_name,property_identifier,room_no, start_date, end_date, phone_number, payment_due_date, payment_final_due_date, is_active) VALUES ('{name}','{property}','{room_no}','{payment_due_date}','{payment_due_date}','{telephone}','{payment_due_date}','{payment_due_date}','Y')")
            conn.commit()
            response.message = f"Record created successfully for {name} - phone {telephone}"
        else:
            response.message = f"Record existing for {name} - phone {telephone}, delete old record and create a new one"

    except:
        traceback.print_exc()
        response.message = f"Error while creating the record for {name} - phone {telephone}. Contact system administrator"
        print("Record not created")
    finally:
        conn.close()
        print("Connexion closed")

def insert_property_record(row, response):
    action = row['Action']
    property_identifier = row['PropertyIdentifier']
    room_no = row['RoomIdentifier']
    rate_price = row['Price']

    #print(f"Action : {action} room_no :{room_no} property : {property_identifier} rate_price : {rate_price}")

    try:
        database_file = os.getenv('DATABASE_FILE')
        conn = sqlite3.connect(database_file)
        cursor_obj = conn.cursor()
        if find_property(row) is None:
            cursor_obj.execute(f"INSERT INTO PROPERTY_DETAILS (property_identifier, room_identifier, price, is_active) VALUES ('{property_identifier}','{room_no}','{rate_price}','Y')")
            conn.commit()
            response.message = f"Record created successfully for {property_identifier} - {room_no}"
        else:
            response.message = f"Record existing for {property_identifier} - {room_no}, delete old record and create a new one"

    except:
        traceback.print_exc()
        print("Record not created")
    finally:
        conn.close()
        print("Connexion closed")

def guest_delete_record(row, response):
    name = row['GuestName']
    room_no = row['RoomNo']
    property = row['Property']
    payment_due_date = row['PaymentDueDate']
    rate_price = row['Price']
    telephone = row['Telephone']
    #print(f"name : {name} room_no :{room_no} property : {property} payment_due_date : {payment_due_date} rate_price : {rate_price} telephone {telephone}")

    try:
        database_file = os.getenv('DATABASE_FILE')
        conn = sqlite3.connect(database_file)
        cursor_obj = conn.cursor()
        cursor_obj.execute(f"UPDATE GUESTS SET is_active='N' WHERE guest_name='{name}' and phone_number='{telephone}' and property_identifier='{property}' and is_active='Y'")
        if cursor_obj.rowcount != 0 :
            response.message = f"Record deleted succesfully for {name} - telephone {telephone}"
        else:
            response.message = f"Record not deleted for {name} - telephone {telephone}"

        conn.commit()

    except:
        traceback.print_exc()
        response.message = f"Record not deleted for {name} - telephone {telephone}"
    finally:
        conn.close()
        print("Connexion closed")

def delete_property_record(row, response):
    action = row['Action']
    property_identifier = row['PropertyIdentifier']
    room_no = row['RoomIdentifier']
    rate_price = row['Price']

    print(f"Action : {action} room_no :{room_no} property : {property_identifier} rate_price : {rate_price}")

    try:
        database_file = os.getenv('DATABASE_FILE')
        conn = sqlite3.connect(database_file)
        cursor_obj = conn.cursor()
        cursor_obj.execute(f"UPDATE PROPERTY_DETAILS SET IS_ACTIVE='N' where property_identifier='{property_identifier}' and room_identifier='{room_no}' and price='{rate_price}' and is_active='Y'")
        if cursor_obj.rowcount != 0 :
            response.message = f"Record deleted successfully for {property_identifier} - {room_no}"
        else:
            response.message = f"Record not deleted for {property_identifier} - {room_no}"

        conn.commit()

    except:
        traceback.print_exc()
        response.message = f"Error while deleting a record for {property_identifier} - {room_no}"
    finally:
        conn.close()
        print("Connexion closed")

def show_guests():
    database_file = os.getenv('DATABASE_FILE')
    con = sqlite3.connect(database_file)
    c = con.cursor()
    for row in c.execute("SELECT * FROM GUESTS where is_active='Y'"):
        print(row)
    #show_properties()


def show_properties():
    database_file = os.getenv('DATABASE_FILE')
    con = sqlite3.connect(database_file)
    c = con.cursor()
    print('Property')
    for row in c.execute("SELECT * FROM PROPERTY_DETAILS where is_active='Y'"):
        print(row)

def find_property(row):
    property_identifier = row['PropertyIdentifier']
    room_no = row['RoomIdentifier']
    rate_price = row['Price']

    database_file = os.getenv('DATABASE_FILE')
    con = sqlite3.connect(database_file)
    c = con.cursor()
    output = c.execute(f"SELECT * FROM PROPERTY_DETAILS where is_active='Y' and property_identifier='{property_identifier}' and room_identifier='{room_no}' and price='{rate_price}'").fetchone()
    return output;


def find_guest(row):
    name = row['GuestName']
    room_no = row['RoomNo']
    property = row['Property']
    payment_due_date = row['PaymentDueDate']
    rate_price = row['Price']
    telephone = row['Telephone']
    database_file = os.getenv('DATABASE_FILE')

    con = sqlite3.connect(database_file)
    c = con.cursor()
    output = c.execute(f"SELECT * FROM GUESTS where is_active='Y' and guest_name='{name}' and room_no='{room_no}' and property_identifier='{property}'").fetchone()
    return output;


def get_all_guests():
    load_dotenv()
    database_file = os.getenv('DATABASE_FILE')
    con = sqlite3.connect(database_file)
    con.row_factory = sqlite3.Row
    c = con.cursor()
    output = c.execute(f"SELECT * FROM GUESTS where is_active='Y'").fetchall()

    rowarray = []
    for row in output:
        d = dict(zip(row.keys(), row))
        guest = Guest(d['id'],d['guest_name'],d['phone_number'],d['payment_due_date'],d['property_identifier'],d['room_no'])
        rowarray.append(guest)

    return rowarray;

if __name__ == "__main__":
    create_db()

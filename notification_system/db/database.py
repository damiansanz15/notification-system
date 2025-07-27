import os
import sqlite3
import traceback
from dotenv import load_dotenv
from model.Guest import Guest
from util import utils
from util.custom_logger import getLogger

logger = getLogger()
#database operation only

def get_db_connection():
    database_file = os.getenv('DATABASE_FILE')
    conn = sqlite3.connect(database_file)
    return conn


def create_db():
    logger.info("Operation [create_db] started")

    try:
        conn = get_db_connection()
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
            room_rate int not null,
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
            insert_date varchar(25),
            is_deposit varchar(1),
            month_paid_for VARCHAR(25),
            year_paid_for varchar(4),
            payment_method varchar(10),
            amount_paid varchar(10),
            receipt_amount_paid varchar(10),
            status varchar(10), 
            notification_count integer,
            actual_payment_date varchar(20),
            receipt_payment_date varchar(20)              
        );
        """#Add a new column to handle the scenario where the notification was send
        cursor_obj.execute(table_creation_query)
        # Commit changes and close connection
        conn.commit()
        logger.info("Operation [create_db] Database created")
    except:
        traceback.print_exc()
        logger.error("Operation [create_db] Database not created")
    finally:
        conn.close()

    logger.info("Operation [create_db] finished")

def update_record(row):
    logger.info("Operation [update_record] started")

    name = row['GuestName']
    room_no = row['RoomNo']
    property = row['Property']
    payment_due_date = row['PaymentDueDate']
    rate_price = row['Price']
    telephone = row['Telephone']
    logger.info(f"name : {name} room_no :{room_no} property : {property} payment_due_date : {payment_due_date} rate_price : {rate_price} telephone {telephone}")

    try:
        conn = get_db_connection()
        cursor_obj = conn.cursor()
        #Insert guest
        statement = """INSERT INTO GUESTS (guest_name,property_identifier, room_no, start_date, end_date, phone_number, payment_due_date, payment_final_due_date) 
                    VALUES (?,?,?,?,?,?,?)"""
        data = (name,room_no,payment_due_date,payment_due_date,telephone,payment_due_date,payment_due_date)
        cursor_obj.execute(statement, data)
        conn.commit()
        #insert property
        cursor_obj.execute(f"INSERT INTO PROPERTY_DETAILS (property_identifier, room_identifier, price, is_active) VALUES ('{property}','{room_no}','{rate_price}','Y')")
        conn.commit()

    except:
        logger.exception("Exception raised: ")
        logger.error("Database not created")
    finally:
        conn.close()
        logger.debug("Connexion closed")
    logger.info("Operation [update_record] finished")

def get_final_payment_due_date(original_date, no_days):
    format = "%d/%m/%Y"
    final_payment_date = utils.add_days_to_date(no_days, original_date)
    final_payment_date = final_payment_date.strftime(format)
    return final_payment_date

def guest_insert_record(row, response):
    logger.info(f"Operation [guest_insert_record] started {row}")
    name = row['GuestName']
    room_no = row['RoomNo']
    property = row['Property']
    payment_due_date = row['PaymentDueDate']
    rate_price = row['Price']
    telephone = row['Telephone']
    final_payment_date = get_final_payment_due_date(payment_due_date, 1)
    contract_end_date = get_final_payment_due_date(payment_due_date,180)

    try:
        conn = get_db_connection()
        cursor_obj = conn.cursor()
        if find_guest(row) is None:
            statement = """INSERT INTO GUESTS (guest_name,property_identifier,room_no, start_date, end_date, phone_number, payment_due_date, payment_final_due_date, room_rate, is_active) 
                        VALUES (?,?,?,?,?,?,?,?,?,?)"""
            data = (name,property,room_no,payment_due_date,contract_end_date,telephone,payment_due_date,final_payment_date,rate_price,'Y')
            cursor_obj.execute(statement, data)
            conn.commit()
            response.message = f"Record created successfully for {name} - phone {telephone}"
        else:
            response.message = f"Record existing for {name} - phone {telephone}, delete old record and create a new one"

    except:
        logger.exception("Exception raised: ")
        response.message = f"Error while creating the record for {name} - phone {telephone}. Contact system administrator"
        logger.error("Record not created")
    finally:
        conn.close()
        logger.info("Connexion closed")
    logger.info("Operation [guest_insert_record] finished")

def insert_property_record(row, response):
    logger.info("Operation [insert_property_record] finished")
    action = row['Action']
    property_identifier = row['PropertyIdentifier']
    room_no = row['RoomIdentifier']
    rate_price = row['Price']

    #print(f"Action : {action} room_no :{room_no} property : {property_identifier} rate_price : {rate_price}")

    try:
        conn = get_db_connection()
        cursor_obj = conn.cursor()
        if find_property(row) is None:
            cursor_obj.execute(f"INSERT INTO PROPERTY_DETAILS (property_identifier, room_identifier, price, is_active) VALUES ('{property_identifier}','{room_no}','{rate_price}','Y')")
            conn.commit()
            response.message = f"Record created successfully for {property_identifier} - {room_no}"
        else:
            response.message = f"Record existing for {property_identifier} - {room_no}, delete old record and create a new one"

    except:
        logger.exception("Exception raised: ")
        logger.debug("Record not created")
    finally:
        conn.close()
        logger.debug("Connexion closed")

def guest_delete_record(row, response):
    logger.info("Operation [guest_delete_record] started")
    name = row['GuestName']
    property = row['Property']
    telephone = row['Telephone']
    logger.info(f"name : {name}  property : {property} telephone {telephone}")

    try:
        conn = get_db_connection()
        cursor_obj = conn.cursor()
        cursor_obj.execute(f"UPDATE GUESTS SET is_active='N' WHERE guest_name='{name}' and phone_number='{telephone}' and property_identifier='{property}' and is_active='Y'")
        if cursor_obj.rowcount != 0 :
            response.message = f"Record deleted succesfully for {name} - telephone {telephone}"
        else:
            response.message = f"Record not deleted for {name} - telephone {telephone}"

        conn.commit()

    except:
        logger.exception("Exception raised: ")
        response.message = f"Record not deleted for {name} - telephone {telephone}"
    finally:
        conn.close()
        logger.debug("Connexion closed")

    logger.info("Operation [guest_delete_record] finished")

def delete_property_record(row, response):
    logger.info("Operation [delete_property_record] finished")

    action = row['Action']
    property_identifier = row['PropertyIdentifier']
    room_no = row['RoomIdentifier']
    rate_price = row['Price']

    logger.debug(f"Action : {action} room_no :{room_no} property : {property_identifier} rate_price : {rate_price}")

    try:
        conn = get_db_connection()
        cursor_obj = conn.cursor()
        cursor_obj.execute(f"UPDATE PROPERTY_DETAILS SET IS_ACTIVE='N' where property_identifier='{property_identifier}' and room_identifier='{room_no}' and price='{rate_price}' and is_active='Y'")
        if cursor_obj.rowcount != 0 :
            response.message = f"Record deleted successfully for {property_identifier} - {room_no}"
        else:
            response.message = f"Record not deleted for {property_identifier} - {room_no}"

        conn.commit()

    except:
        logger.exception()
        response.message = f"Error while deleting a record for {property_identifier} - {room_no}"
    finally:
        conn.close()
        logger.debug("Connexion closed")

    logger.info("Operation [delete_property_record] finished")

def show_guests():
    logger.info("Operation [show_guests] started")

    try:
        con = get_db_connection()
        c = con.cursor()
        for row in c.execute("SELECT * FROM GUESTS where is_active='Y'"):
            print(row)
    #show_properties()
    except:
        logger.exception("Exception ocurred:")
    finally:
        con.close()
        logger.debug("Connexion closed")

    logger.info("Operation [show_guests] finished")


def show_properties():
    logger.info("Operation [show_properties] started")

    try:
        con = get_db_connection()
        c = con.cursor()
        print('Property')
        for row in c.execute("SELECT * FROM PROPERTY_DETAILS where is_active='Y'"):
            print(row)
    except:
        logger.exception("Exception ocurred:")
    finally:
        con.close()
        logger.debug("Connexion closed")

    logger.info("Operation [show_properties] finished")

def find_property(row):
    logger.info("Operation [find_property] started")

    property_identifier = row['PropertyIdentifier']
    room_no = row['RoomIdentifier']
    rate_price = row['Price']

    try:
        con = get_db_connection()
        c = con.cursor()
        output = c.execute(f"SELECT * FROM PROPERTY_DETAILS where is_active='Y' and property_identifier='{property_identifier}' and room_identifier='{room_no}' and price='{rate_price}'").fetchone()
    except:
        logger.exception("Exception ocurred:")
    finally:
        con.close()
        logger.debug("Connexion closed")

    logger.info("Operation [find_property] finished")
    return output;


def find_guest(row):
    logger.info("Operation [find_guest] started")

    name = row['GuestName']
    room_no = row['RoomNo']
    property = row['Property']

    try:
        con = get_db_connection()
        c = con.cursor()
        data = (name, room_no, property)
        output = c.execute(f"SELECT * FROM GUESTS where is_active='Y' and guest_name=? and room_no=? and property_identifier=?", data).fetchone()
    except:
        logger.exception("Exception ocurred:")
    finally:
        con.close()
        logger.debug("Connexion closed")

    logger.info("Operation [find_guest] finished")
    return output;


def find_guest_by_wa_no(wa_number : str):
    logger.info("Operation [find_guest_by_wa_no] started")
    logger.info(f"Operation [find_guest_by_wa_no] wa_number {wa_number}")
    dikt = {}

    try:
        con = get_db_connection()
        con.row_factory = sqlite3.Row
        c = con.cursor()
        data = (wa_number,)
        c.execute(f"SELECT * FROM GUESTS where is_active='Y' and phone_number=? ",data)
        output = c.fetchall()#TODO change to fetch one


        dikt = dict(output[0])
        logger.debug(f"Output {type(dikt)}")
    except:
        logger.exception("Exception ocurred:")
    finally:
        con.close()
        logger.debug("Connexion closed")

    logger.info("Operation [find_guest_by_wa_no] finished")
    return dikt;

def get_all_guests():
    logger.info("Operation [get_all_guests] started")

    try:
        con = get_db_connection()
        con.row_factory = sqlite3.Row
        c = con.cursor()
        output = c.execute(f"SELECT * FROM GUESTS where is_active='Y'").fetchall()

        rowarray = []
        for row in output:
            d = dict(zip(row.keys(), row))
            guest = Guest(d['id'],d['guest_name'],d['phone_number'],d['payment_due_date'],d['payment_final_due_date'],d['start_date'],d['end_date'],d['property_identifier'],d['room_no'],d['room_rate'])
            rowarray.append(guest)
    except:
        logger.exception("Exception raised:")
        logger.error("Record not created")
    finally:
        con.close()
        logger.debug("Connexion closed")


    logger.info("Operation [get_all_guests] finished")
    return rowarray;

def get_all_payment_records():
    logger.info("Operation [get_all_payment_records] started")

    try:
        con = get_db_connection()
        c = con.cursor()

        rowarray = []
        for row in c.execute("SELECT * FROM PAYMENT_DETAILS"):
            print(row)

    except:
        logger.exception("Exception raised:")
        logger.error("Record not created")
    finally:
        con.close()
        logger.debug("Connexion closed")

    logger.info("Operation [get_all_payment_records] finished")
    return rowarray;

def find_payment_rec(row):
    logger.info(f"Operation [find_payment_rec] started for guest_id {row.name} {row.property_identifier}")

    try:
        name = row.id
        property_id = row.property_identifier
        insert_date = utils.get_today_date()
        month_paid = utils.get_month()
        year = utils.get_year()

        con = get_db_connection()
        c = con.cursor()
        data = (name, property_id, month_paid, year)
        statement = """SELECT * FROM PAYMENT_DETAILS where guest_id=? and property_id=? and month_paid_for=? and year_paid_for=?"""
        output = c.execute(statement, data).fetchone()
    except:
        logger.exception("Exception raised:")
        logger.error("Record not created")
    finally:
        con.close()
        logger.debug("Connexion closed")


    logger.info("Operation [find_payment_rec] finished")
    return output;

def is_payment_completed(row):
    logger.info("Operation [is_payment_completed] started")

    try:

        name = row.id
        property_id = row.property_identifier
        insert_date = utils.get_today_date()
        month_paid = utils.get_month()
        year = utils.get_year()

        con = get_db_connection()
        c = con.cursor()
        data = (name, property_id, month_paid, year)
        statement = """SELECT * FROM PAYMENT_DETAILS where guest_id=? and property_id=? and month_paid_for=? and year_paid_for=? and status='COMPLETED'"""
        output = c.execute(statement, data).fetchone()
    except:
        logger.exception("Exception raised:")
        logger.error("Record not created")
    finally:
        con.close()
        logger.debug("Connexion closed")


    logger.info("Operation [is_payment_completed] finished")
    return output is not None;

def payment_insert_record(row, is_deposit ="N"):
    logger.info(f"Operation [payment_insert_record] started {row.name} {row.property_identifier} is_deposit={is_deposit}")

    name = row.id
    property_id = row.property_identifier
    insert_date = utils.get_today_date()
    month_paid = utils.get_month()
    year = utils.get_year()
    payment_method = ""

    try:
        conn = get_db_connection()
        cursor_obj = conn.cursor()
        if find_payment_rec(row) is None:
            statement = """INSERT INTO PAYMENT_DETAILS (guest_id,property_id,insert_date, is_deposit, month_paid_for, year_paid_for, payment_method, amount_paid, status, notification_count) 
                        VALUES (?,?,?,?,?,?,?,?,?,?)"""
            data = (name,property_id,insert_date,is_deposit,month_paid,year,payment_method,0,"PENDING",1)
            cursor_obj.execute(statement, data)
            conn.commit()
            logger.info('Record inserted for payment_details')


    except:
        logger.exception("Exception raised:")
        logger.error("Record not created")
    finally:
        get_all_payment_records()
        conn.close()
        logger.debug("Connexion closed")

    logger.info("Operation [payment_insert_record] finished")

def payment_update_notification_cnt(row):
    logger.info(f"Operation [payment_update_notification_cnt] started {row}")

    name = row.id
    property_id = row.property_identifier
    month_paid = utils.get_month()
    year = utils.get_year()
    try:

        conn = get_db_connection()
        cursor_obj = conn.cursor()

        if not find_payment_rec(row):#Record not found, insert it
            payment_insert_record(row)
            return

        #get current notification_count
        result = get_notification_count(row)
        rec_id = result[0]
        count = result[1] + 1

        statement = """UPDATE PAYMENT_DETAILS 
        SET notification_count = ? 
        where guest_id=? and property_id=? and month_paid_for=? and year_paid_for=? and id=?"""
        data = (count,name,property_id,month_paid,year, rec_id)
        cursor_obj.execute(statement, data)
        conn.commit()
        logger.info(f" Rows updated {cursor_obj.rowcount}")

    except:
        logger.exception("Exception raised:")
        logger.error("Record not created")
    finally:
        get_all_payment_records()
        conn.close()
        logger.info("Connexion closed")

    logger.info("Operation [payment_update_notification_cnt] finished")


def get_notification_count(row):
    logger.info(f"Operation [get_notification_count] started for {row.name} {row.property_identifier}")

    name = row.id
    property_id = row.property_identifier
    month_paid = utils.get_month()
    year = utils.get_year()
    try:

        conn = get_db_connection()
        cursor_obj = conn.cursor()

        #get current notification_count
        statement = """SELECT id, notification_count 
        from PAYMENT_DETAILS 
        where guest_id=? and property_id=? and month_paid_for=? and year_paid_for=?"""
        data = (name,property_id,month_paid,year)
        result = cursor_obj.execute(statement, data).fetchone()

    except:
        logger.exception("Exception raised:")
        logger.error("Record not created")
    finally:
        get_all_payment_records()
        conn.close()
        logger.info("Connexion closed")

    logger.info("Operation [get_notification_count] finished")
    return result


def payment_update_status(row : dict, amount : int, date : str, status='UNDER_VALIDATION', payment_method='', receipt_payment_date=''):
    logger.info(f"Operation [payment_update_status] started {row}")
    logger.info(f"Operation [payment_update_status] amount {amount} date {date}")

    name = row['id']
    property_id = row['property_identifier']
    month_paid = utils.get_month()
    year = utils.get_year()
    try:

        conn = get_db_connection()
        cursor_obj = conn.cursor()

        statement = """UPDATE PAYMENT_DETAILS 
        SET receipt_amount_paid=?, actual_payment_date=?, status=?, payment_method=?, receipt_payment_date=?
        where guest_id=? and property_id=? and month_paid_for=? and year_paid_for=? """
        data = (amount, date, status, payment_method,receipt_payment_date, name,property_id,month_paid,year)
        cursor_obj.execute(statement, data)
        conn.commit()
        logger.info(f" Rows updated {cursor_obj.rowcount}")

    except:
        logger.exception("Exception raised")
        logger.error("Record not created")
    finally:
        get_all_payment_records()
        conn.close()
        logger.info("Connexion closed")

    logger.info(f"Operation [payment_update_status] finished ")




if __name__ == "__main__":
    logger.info("Calling create_db \n Loading environment variables ...")
    load_dotenv()
    create_db()

import csv
from sms import notifications
from db import database
from model import Response
from jobs.job_util import remove_final_reminder_job
from util.custom_logger import getLogger
from util.utils import get_today_date, db_date_to_local_date, get_today_date_minus_one_day

logger = getLogger()
#This file talks to database

def read_file(filepath):
    logger.info("Operation [read_file] started")

    try:
        with open(filepath, 'r')as file:
            csv_reader = csv.DictReader(file)

            data_list = []

            for row in csv_reader:
                data_list.append(row)
        logger.info("Operation [read_file] finished")
        return data_list
    except FileNotFoundError:
        logger.error(f"Error: the file '{filepath}' was not found")
        return None
    except Exception as e:
        logger.error(f"An error ocurred while reading the file: {e}")
        return None


def guest_populate_db(records):
    logger.info("Operation [guest_populate_db] started")

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
    logger.info("Operation [guest_populate_db] finished")
    return records_response;

def get_guests():
    return database.get_all_guests()

def property_populate_db(records):
    logger.info(f"Operation [property_populate_db] started")

    #Iterate over the dictionary and insert into correc tables.
    database.create_db()
    for row in records:
        action = row['Action']
        if action == 'I':
            database.insert_property_record(row)
        elif action == 'D':
            database.delete_property_record(row)
    database.show_properties()
    logger.info(f"Operation [property_populate_db] finished")

def is_valid_guest_wa_no(wa_number : str):
    if database.find_guest_by_wa_no(wa_number):
        return True
    return False


def on_payment_due_date_handling(line):
    logger.info(f"Operation [on_payment_due_date_handling] started {line.name} {line.property_identifier} ")
    payment_date = line.payment_due_date
    guest_name = line.name
    phone_number = line.phone_number
    payment_due_date = db_date_to_local_date(payment_date)#datetime.strptime(payment_date, format).date()
    database.payment_insert_record(line)
    notifications.send_notification(guest_name,phone_number, payment_due_date, "Y", "N")
    logger.info(f"Operation [on_payment_due_date_handling] finished")

def on_final_payment_date_handling(line):
    logger.info(f"Operation [on_final_payment_date_handling] started")

    payment_date = line.payment_due_date
    guest_name = line.name
    phone_number = line.phone_number
    payment_due_date = db_date_to_local_date(payment_date)#datetime.strptime(payment_date, format).date()
    notifications.send_notification(guest_name,phone_number, payment_due_date, "Y", "Y")
    database.payment_update_notification_cnt(line)
    logger.info(f"Operation [on_final_payment_date_handling] finished")

def on_suplement_process_handling(guests):
    logger.info(f"Operation [on_suplement_process_handling] started")

    message = f"The following guest(s) did not covered the payment on final date {get_today_date_minus_one_day()} \n"
    guests_str = ""
    for guest in guests:
        guests_str += f"\u2022 {guest.name} {guest.phone_number} {guest.payment_final_due_date}\n"

    message = message + guests_str
    notifications.send_supplement_notification(message)
    remove_final_reminder_job()
    logger.info(f"Operation [on_suplement_process_handling] finished")

def on_payment_received(guest, same_amount=False, amount=0, payment_method='', response = None, receipt_payment_date = ''):
    logger.info(f"Operation [on_payment_received] started")

    logger.info(guest)
    if same_amount:
        database.payment_update_status(guest, amount, get_today_date(),'COMPLETED', 'CARD', receipt_payment_date)
        response.message = "Gracias por tu pago"
    else:
        database.payment_update_status(guest, amount, get_today_date(), status='UNDER_VALIDATION', payment_method='CARD', receipt_payment_date=receipt_payment_date)
        response.message = "El comprobante se encuentra en revision. \n Gracias por tu pago."

    logger.info(f"Operation [on_payment_received] finished")
    #Send notificatrion message to validate

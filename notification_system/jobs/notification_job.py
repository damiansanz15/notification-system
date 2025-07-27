
from datetime import datetime
import util.utils
from db import database
from dotenv import load_dotenv
from util.utils import get_today_date, db_date_to_local_date, get_today_date_str, get_today_date_minus_one_day
import load_data
import job_util
from util.custom_logger import getLogger

logger = getLogger()

def process_data(records):

    today = get_today_date()
    logger.info(f"Today {today}")
    is_final_remainder_send = False

    for line in records:
        payment_date = line.payment_due_date # line['payment_due_date']
        guest_name = line.name
        payment_due_date = db_date_to_local_date(payment_date)
        final_payment_date = db_date_to_local_date(line.payment_final_due_date)
        one_day_ahead = util.utils.add_days_to_date(1,get_today_date_str())
        #today#
        if payment_due_date == today and not database.find_payment_rec(line) and (database.get_notification_count(line) is None or database.get_notification_count(line)[1] == 0):
            load_data.on_payment_due_date_handling(line)
            #print(f"Regular Message sent to {guest_name} Whatsapp {phone_number} Payment due date {payment_due_date}")
        elif final_payment_date == one_day_ahead and not database.is_payment_completed(line) and database.get_notification_count(line) is not None and not database.get_notification_count(line)[1] > 1:
            load_data.on_final_payment_date_handling(line)
            is_final_remainder_send = True
            #Payment has not been completed in final date, schedule a job to run at 10:30
            #print(f"Final Message sent to {guest_name} Whatsapp {phone_number} Payment due date {payment_due_date}")
        else:
            logger.info(f"Skipped for  {guest_name} payment due date {payment_due_date}")

    if is_final_remainder_send:
        logger.info("Creating a midnight job")
        job_util.schedule_final_reminder_job()
        #Create a midnight job

def supplement_process_data(records):
    logger.info("Today {datetime.today().date()}")
    #Final day was 25 Julio 2025 -
    #This process runs on 26
    #Validate if today - 1 day == final_date and guest has not made the payment:
    #Collect all the names, phone numbers and send a notification to the primary contact
    yesterday = util.utils.add_days_to_date(1,get_today_date_str()) #get_today_date_minus_one_day()#datetime.today().date()
    guests = []
    for line in records:
        final_payment_date = db_date_to_local_date(line.payment_final_due_date)#datetime.strptime(line.payment_final_due_date, format).date()

        if final_payment_date == yesterday and not database.is_payment_completed(line):
            guests.append(line)

    load_data.on_suplement_process_handling(guests)



def run_regular_nofitication_process():
    logger.info("Operation [run_regular_nofitication_process] started")
    #Run every day at 10:30 am
    load_dotenv()
    #Read records from the database
    guests = database.get_all_guests()
    #Send notification
    process_data(guests)
    logger.info("Operation [run_regular_nofitication_process] finished")

def run_supplement_process():
    logger.info("Operation [run_supplement_process] started")

    #This process runs on demand at 10:30 pm (12) to validate if the payment has been made after the final notification sent.
    #Validate if the payment was covered, If so then update payment_details and inform the primary contact to validate.
    #If the payment was not covered, then inform the primary contact to reach out personally.

    #Read records from the database
    guests = database.get_all_guests()
    #Send notification
    supplement_process_data(guests)
    logger.info("Operation [run_supplement_process] finished")


if __name__ == "__main__":
    logger.info("Loading environment variables ...")
    #run_regular_nofitication_process()
    load_dotenv()
    run_supplement_process()

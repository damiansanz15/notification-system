import os
from twilio.rest import Client
from util import messages
from dotenv import load_dotenv
from util.custom_logger import getLogger

# Your Account SID and Auth Token from console.twilio.com
load_dotenv()
account_sid = os.getenv('ACCOUNT_SID')
auth_token  = os.getenv('AUTH_TOKEN')
source_phone_number  = os.getenv('SOURCE_PHONE_NUMBER')
client = Client(account_sid, auth_token)
logger = getLogger()


def send_notification(name, phone_number, due_date, monthly_payment, is_final = "N"):
    logger.info("Operation [send_notification] started ")
    logger.info(f" {name} {phone_number} {due_date} ")
    formatted_date = messages.transform_date(due_date)
    message = generate_message(name, formatted_date, monthly_payment, is_final)
    logger.info(message)
    send_to = f"whatsapp:{phone_number}"
    #message = client.messages.create(
    #    to=send_to,
    #    from_=f"whatsapp:{source_phone_number}",
    #    body=message)
    #print(message.sid)
    logger.info("Operation [send_notification] finished")

def send_supplement_notification(message: str):
    logger.info("Operation [send_supplement_notification] started")


    primary_contact_no = "+5213411298747"
    logger.info(message)
    send_to = f"whatsapp:{primary_contact_no}"
    #message = client.messages.create(
    #    to=send_to,
    #    from_=f"whatsapp:{source_phone_number}",
    #    body=message)
    #print(message.sid)
    logger.info("Operation [send_supplement_notification] finished")


def generate_message(name, date, monthly_payment, is_final = "N"):
    if monthly_payment == "Y" and is_final == "N" :
        return f"Hola {name}, te recordamos que tu fecha de pago es el {date}.\n Si ya realizaste el pago, favor de enviar comprobante."
    elif monthly_payment == "Y" and is_final == "Y" :
        return f"Hola {name}, Hoy es el ultimo dia para realizar el pago {date}.\n Si ya lo realizaste, favor de enviar comprobante."

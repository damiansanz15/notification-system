from ocr import text_analysis
from db.database import find_guest_by_wa_no, payment_update_status
from util.custom_logger import getLogger
from jobs.load_data import on_payment_received

logger = getLogger()

def process(filename : str, sender, message, response):
    logger.info("Operation [process] started")

    dict = text_analysis.run_image_analysis(filename)
    logger.info(f"Remarks from receipt {dict}")

    guest = find_guest_by_wa_no(sender)
    logger.info(f"Guest data {guest}")

    #get amounts
    rcpt_amounts = dict['amounts']
    same_amount = False
    for amnt in rcpt_amounts:
        logger.info(f" {amnt} == {int(guest['room_rate'])} ")
        if amnt == int(guest['room_rate']):
            same_amount = True
            break;

    #update payment details set amount = amount, fecha and status, where guest_id = and property_id and moth = and year_
    #Ask for confimration for from host
    if not same_amount:
        amnt = min(rcpt_amounts, key=lambda x: abs(x - guest['room_rate']))


    on_payment_received(guest, same_amount, amount = amnt, response=response, receipt_payment_date=dict['dates'][0] )

    logger.info(f"Operation [process] is same amount {same_amount}")
    logger.info("Operation [process] finished")

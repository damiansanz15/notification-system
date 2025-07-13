import os
from twilio.rest import Client
from util import messages

# Your Account SID and Auth Token from console.twilio.com
account_sid = os.getenv('ACCOUNT_SID')
auth_token  = os.getenv('AUTH_TOKEN')
source_phone_number  = os.getenv('SOURCE_PHONE_NUMBER')
client = Client(account_sid, auth_token)


def send_notification(name, phone_number, due_date):
    formatted_date = messages.transform_date(due_date)
    message = f"Hola {name}, te recordamos que tu fecha de pago es el {formatted_date}.\n Si ya realizaste el pago, favor de enviar comprobante."
    send_to = f"whatsapp:{phone_number}"
    message = client.messages.create(
        to=send_to,
        from_=f"whatsapp:{source_phone_number}",
        body=message)
    print(message.sid)

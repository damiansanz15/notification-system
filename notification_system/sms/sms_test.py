from twilio.rest import Client
import os

# Your Account SID and Auth Token from console.twilio.com
account_sid = os.getenv('ACCOUNT_SID')
auth_token  = os.getenv('AUTH_TOKEN')
target_phone_number = os.getenv('TARGET_PHONE_NUMBER')
source_phone_number  = os.getenv('SOURCE_PHONE_NUMBER')

client = Client(account_sid, auth_token)

message = client.messages.create(
    to=f"whatsapp:{target_phone_number}",
    from_=f"whatsapp:{source_phone_number}",
    body="Hello from Casa Damian")

print(message.sid)

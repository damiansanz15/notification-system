import time

from flask import Flask, request, jsonify, g
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse
from jobs import load_data
from dotenv import load_dotenv
import subprocess
from ocr.ocr_wos import process
from datetime import datetime
from util.custom_logger import getLogger
from model.Response import Response


load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = os.getenv('UPLOADS_FOLDER') # Define a folder to store uploaded files
app.config['CSV_FILES'] = UPLOAD_FOLDER
account_sid = os.getenv('ACCOUNT_SID')
auth_token  = os.getenv('AUTH_TOKEN')
logger = getLogger(log_level="INFO")

@app.before_request
def start_timer():
    g.start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url}")
    logger.debug(f"Headers: {request.headers}")

    if request.method in ['POST', 'PUT']:
        logger.debug(f"Body: {request.get_data(as_text=True)}")

@app.after_request
def log_request(response):
    if hasattr(g, 'start_time'):
        duration = round(time.time() - g.start_time, 4)
        logger.info(f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Duration: {duration}s")

    try:
        logger.debug(f"Response Data: {response.get_json()}")
    except Exception:
        logger.exception("Expection raised: ")
        logger.debug(f"Response Data (raw): {response.get_data(as_text=True)}")

    return response

@app.route('/guests', methods=['POST'])
def guests():
    logger.info(f"Operation [guests] started {request.remote_addr}")
    if 'file' not in request.files:
        logger.error("Not file found")
        return jsonify({"message" : "Not file found"}), 400

    file = request.files['file']

    if file and file.filename.endswith('.csv'):
        if not os.path.exists(UPLOAD_FOLDER):
            original_umask = os.umask(0)
            os.makedirs(UPLOAD_FOLDER, mode=0o777)
            subprocess.call(['chmod', '-R', '777', app.config['CSV_FILES']])
            os.umask(original_umask)


        #datetime to concatenate
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")

        filepath = os.path.join(UPLOAD_FOLDER, f"{formatted_datetime}_{file.filename}")
        file.save(filepath)
        logger.info(f"Saving file at {filepath}")
        #Call db
        file_content = load_data.read_file(filepath)
        out = load_data.guest_populate_db(file_content)
        dict_list = [rc.__dict__ for rc in out]
        logger.info("Operation [guests] finished ")
        return jsonify(dict_list)

    return jsonify({"message": "Please review the request"}), 400

@app.route('/guests', methods=['GET'])
def get_guests():
    """Return a json object with all the guests"""
    #Call the db to get the guests, then generate a csf
    out = load_data.get_guests()
    dict_list = [rc.__dict__ for rc in out]
    return jsonify(dict_list)



@app.route('/webhook', methods=['POST'])
def webhook():#TODO This should reply only to guests, validate this in the table
    #create a web service to update the payment_details if the payment was successful.
    response = Response("")
    sender = request.form.get('From')
    message = request.form.get('Body')
    media_url = request.form.get('MediaUrl0')
    count_file = request.form.get('NumMedia')
    #datetime to concatenate
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    real_number = sender[-10:]
    username = sender.split(':')[1]
    logger.info(f'{sender} -> {real_number} sent {message}')
    if not load_data.is_valid_guest_wa_no(username):
        return ''

    if media_url:
        r = requests.get(media_url, auth=(account_sid, auth_token))
        content_type = request.form.get("MediaContentType0")
          # remove the whatsapp: prefix from the number
        if content_type == 'image/jpeg':
            filename = f'/{formatted_datetime}.jpeg'
        elif content_type == 'image/png':
            filename = f'/{formatted_datetime}.png'
        elif content_type == 'image/gif':
            filename = f'/{formatted_datetime}.gif'
        else:
            filename = None


        if filename:
            user_folder = UPLOAD_FOLDER+f'/{username}'
            if not os.path.exists(user_folder):
                original_umask = os.umask(0)
                os.makedirs(user_folder, mode=0o777)
                subprocess.call(['chmod', '-R', '777',user_folder])
                os.umask(original_umask)


            with open(user_folder+filename, 'wb') as f:
                f.write(r.content)


            process(user_folder+filename, username, message, response)

            return respond(response.message)
        else:
            return respond('El archivo que enviaste no es valido, envia una imagen')
    else:
        return respond('Por favor envia una imagen')


def respond(message):
    response = MessagingResponse()
    response.message(message)
    return str(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
#ngrok http http://localhost:5000

from flask import Flask, request, jsonify
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse
from PIL import Image
#import pytesseract
from jobs import load_data
from dotenv import load_dotenv
from datetime import datetime
import subprocess

#pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_INSTALLATION_PATH')
load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = os.getenv('UPLOADS_FOLDER') # Define a folder to store uploaded files
app.config['CSV_FILES'] = UPLOAD_FOLDER
account_sid = os.getenv('ACCOUNT_SID')
auth_token  = os.getenv('AUTH_TOKEN')

@app.route('/guests', methods=['POST'])
def guests():

    if 'file' not in request.files:
        return jsonify({"message" : "Not file found"}), 400

    file = request.files['file']

    if file and file.filename.endswith('.csv'):
        if not os.path.exists(UPLOAD_FOLDER):
            original_umask = os.umask(0)
            os.makedirs(UPLOAD_FOLDER, mode=0o744)
            subprocess.call(['chmod', '-R', '+w', app.config['CSV_FILES']])
            os.umask(original_umask)


        #datetime to concatenate
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")

        filepath = os.path.join(UPLOAD_FOLDER, f"{formatted_datetime}_{file.filename}")
        file.save(filepath)
        #Call db
        file_content = load_data.read_file(filepath)
        out = load_data.guest_populate_db(file_content)
        dict_list = [rc.__dict__ for rc in out]
        return jsonify(dict_list)

    return jsonify({"message": "Please review the request"}), 400

@app.route('/guests', methods=['GET'])
def get_guests():
    """Return a json object with all the guests"""
    #Call the db to get the guests, then generate a csf
    out = load_data.get_guests()
    #dict_list = [rc.__dict__ for rc in out]
    print(out)
    #objects_dic = {}
    dict_list = [rc.__dict__ for rc in out]
    #for obj in out:
    #    objects_dic[obj.id] = obj.to_dict()

    return jsonify(dict_list)




"""@app.route('/webhook', methods=['POST'])
def webhook():
    print(request.form)
    sender = request.form.get('From')
    message = request.form.get('Body')
    media_url = request.form.get('MediaUrl0')
    count_file = request.form.get('NumMedia')
    print(count_file)
    print("media url ", media_url)
    print(f'{sender} sent {message}')
    if media_url:
        r = requests.get(media_url, auth=(account_sid, auth_token))
        print("r >> ",r)
        content_type = request.form.get("MediaContentType0") #r.headers['Content-Type']
        print(content_type)
        username = sender.split(':')[1]  # remove the whatsapp: prefix from the number
        if content_type == 'image/jpeg':
            filename = f'uploads/{username}/{message}.jpeg'
        elif content_type == 'image/png':
            filename = f'uploads/{username}/{message}.png'
        elif content_type == 'image/gif':
            filename = f'uploads/{username}/{message}.gif'
        else:
            filename = None

        print(r)

        #with open("received_image.jpg", "wb") as f:
        #    for chunk in r.iter_content(chunk_size=8192):
        #        f.write(chunk)
        #f.write(response.content)

        if filename:
            if not os.path.exists(f'uploads/{username}'):
                os.mkdir(f'uploads/{username}')
            with open(filename, 'wb') as f:
                f.write(r.content)


            #Read image
            image = Image.open(filename)
            text = pytesseract.image_to_string(image, lang='spa')
            print(text)
            return respond('Thank you! Your image was received.')
        else:
            return respond('The file that you submitted is not a supported image type.')
    else:
        return respond('Please send an image!')
"""

def respond(message):
    response = MessagingResponse()
    response.message(message)
    return str(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
#ngrok http http://localhost:5000

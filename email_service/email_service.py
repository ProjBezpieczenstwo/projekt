import logging
import sys

from flask import Flask, request, jsonify

from email_sender import EmailSender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
app = Flask(__name__)

email_sender = EmailSender()


@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json() or {}
    email_receiver = data.get('email_receiver')
    auth_key = data.get('auth_key')
    
    logging.info("test auth_keya itp")
    logging.info(f"email: {email_receiver}")
    logging.info(f"auth_key: {auth_key}")
    if not email_receiver or not auth_key:
        return jsonify({"message": "missing data to send email"}), 400
    logging.info("po test auth_keya itp")
    
    return email_sender.send_email(email_receiver, auth_key, False)


@app.route('/token-email', methods=['POST'])
def token_email():
    data = request.get_json() or {}
    email_receiver = data.get('email_receiver')
    token = data.get('token')
    
    logging.info("test token itp")
    logging.info(f"email: {email_receiver}")
    logging.info(f"token: {token}")
    if not email_receiver or not token:
        return jsonify({"message": "missing data to send email"}), 400
    logging.info("po test token itp")
    
    return email_sender.send_email(email_receiver, token, True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

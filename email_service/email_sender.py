# Email sender that sends emails based on the given parameters
import logging
import smtplib
import ssl
import sys
from email.message import EmailMessage

from flask import jsonify

from config import EMAIL_SENDER, EMAIL_PASSWORD, SMTP_PORT, SMTP_SERVER, FRONTEND_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


class EmailSender:
    def __init__(self):
        pass

    def send_email(self, email_receiver: str, auth_key: str, token: bool):
        em = EmailMessage()
        em['From'] = EMAIL_SENDER
        em['To'] = email_receiver
        em['Subject'] = "Twój kod weryfikacyjny"
        logging.info("tworzymy")
        if not token:
            text = f"""
            Aby potwierdzić swoje konto kliknij w poniższy link:
            {FRONTEND_URL}/auth/confirm?token={auth_key}
            Pozdro 600
            """
        else:
            text = f"""
            Jak chcesz sie zarejestrować dawaj mordo z tym tokenem:
            {auth_key}
            Pozdro 600
            """
        # em.set_content(MIMEText(text,'html'))
        em.set_content(text)
        logging.info("content ustawiony")
        context = ssl.create_default_context()
        logging.info("context utworzony")
        logging.info(SMTP_PORT)
        logging.info(SMTP_SERVER)
        logging.info(EMAIL_SENDER)
        logging.info(EMAIL_PASSWORD)
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                logging.info("login klasa")
                smtp.sendmail(EMAIL_SENDER, email_receiver, em.as_string())
                logging.info(em.as_string())
                logging.info("wysłane")
                return jsonify({"message": f"Email sent successfully to {email_receiver}"}), 200

        except smtplib.SMTPException as e:
            return jsonify({"message": f"Błąd SMTP: {e}"}), 400
        except Exception as e:
            return jsonify({"message": f"Nieoczekiwany bląd: {e}"}), 400

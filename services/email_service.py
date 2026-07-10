import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def _get_config():
    return {
        'host': os.getenv('MAIL_SERVER', 'localhost'),
        'port': int(os.getenv('MAIL_PORT', 587)),
        'username': os.getenv('MAIL_USERNAME', ''),
        'password': os.getenv('MAIL_PASSWORD', ''),
        'sender': os.getenv('MAIL_SENDER', 'noreply@exclusiveautodetail.com'),
        'use_tls': os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
    }


def send_email(to, subject, body_html, body_text=None, retries=2):
    config = _get_config()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['sender']
    msg['To'] = to
    if body_text:
        msg.attach(MIMEText(body_text, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))

    last_error = None
    for attempt in range(retries + 1):
        try:
            server = smtplib.SMTP(config['host'], config['port'], timeout=10)
            if config['use_tls']:
                server.starttls()
            if config['username'] and config['password']:
                server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            logger.info(f'Email sent to {to}: {subject}')
            return True
        except Exception as e:
            last_error = e
            logger.warning(f'Email attempt {attempt+1} failed for {to}: {e}')
    logger.error(f'Email failed permanently for {to}: {last_error}')
    return False


def send_password_reset(email, reset_url):
    subject = 'Recuperacion de contrasena - Exclusive Auto Detail'
    body = f'''<html><body>
    <h2>Recuperacion de contrasena</h2>
    <p>Hemos recibido una solicitud para restablecer tu contrasena.</p>
    <p><a href="{reset_url}">Haz clic aqui para restablecerla</a></p>
    <p>Este enlace expira en 15 minutos.</p>
    <p>Si no solicitaste este cambio, ignora este mensaje.</p>
    </body></html>'''
    return send_email(email, subject, body)

from passlib.context import CryptContext 
from api.config import settings
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
import random
import email, smtplib, ssl
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import string

def hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def rand_pass(size):
    generate_pass = ''.join([random.choice(string.ascii_uppercase +
                                           string.ascii_lowercase +
                                           string.digits)
                             for n in range(size)])

    return generate_pass


def generate_auth_email(passcode, receiver_email):
    subject = "Verification Code"
    body = f"\nHi,\n\n Your verification code is {passcode}"
    sender_email = settings.sender_email
    password = settings.password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def welcome_auth_email(name, passcode, receiver_email):
    subject = "Verification Code"
    body = f"\nHi,\n\n Welcome to fast-api-blog, \n\n {name} \n\n Your one time verification code:- {passcode}"
    sender_email = settings.sender_email
    password = settings.password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
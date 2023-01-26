from mailjet_rest import Client
from app.config import settings
from random import choices
import string
import socket

"""for this project i am using mailjet Free, wich hase 200 email in total"""
api_key = settings.MJ_APIKEY_PUBLIC  # api key of mailjet account
api_secret = settings.MJ_APIKEY_PRIVATE  # privet key of mailjet account
# using python lib to communicate with the API, we can still use just requests,
# if we want to not use this library
mailjet = Client(auth=(api_key, api_secret), version='v3')


def get_hostname():
    """here we get the ipaddress of the server
    in realife ill just use the domain name without port => defaut 443"""
    return socket.gethostbyname(socket.gethostname())
    
def send_email(server, email, pin_code, url, firstname="", lastname=""):
    """send email using a Mailjet REST API"""
    name = firstname or lastname
    hostname = get_hostname()
    data = {
      'FromEmail': "smtpmailver@gmail.com",
      'FromName': f"{server} team",
      'Recipients': [
        {
          "Email": email,
          "Name": name
        }
      ],
      'Subject': "activate your account",
      'Text-part': f"welcome to {server}, please use this pin : {pin_code} \
         to validate your registration",
      'Html-part': f"<h3>welcome to {server}</h3><br/>\
         please use this pin code : {pin_code} \
         to validate your registration<br/>\
         or follow up this link http://{hostname}:8000/users/validation/{url}\
         code will expire aften 1min"
    }
    result = mailjet.send.create(data=data)
    return result


def generate_key():
    "generate string of 4 random digits"
    return "".join(choices("0123456789", k=4))


def generate_url():
    "generation string of 10 characters as a short url pattern"
    return "".join(choices(string.ascii_letters, k=10))

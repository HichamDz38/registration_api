from mailjet_rest import Client
from config import settings
from random import choices

api_key = settings.MJ_APIKEY_PUBLIC
api_secret = settings.MJ_APIKEY_PRIVATE
mailjet = Client(auth=(api_key, api_secret), version='v3')


def send_email(server, email, pin_code, firstname="", lastname=""):
    """send email using a Mailjet REST API"""
    name = firstname or lastname
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
         code will expire aften 1min"
    }
    result = mailjet.send.create(data=data)
    return result


def generate_key():
    "generate string of 4 random digits"
    return "".join(choices("0123456789", k=4))

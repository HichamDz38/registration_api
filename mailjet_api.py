from mailjet_rest import Client
from config import settings
from random import choices


api_key = settings.MJ_APIKEY_PUBLIC
api_secret = settings.MJ_APIKEY_PRIVATE
mailjet = Client(auth=(api_key, api_secret), version='v3')


def generate_key():
    "generate string of 4 random digits"
    return "".join(choices("0123456789", k=4))


def send_email(server, email, firstname="", lastname=""):
    key = generate_key()
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
      'Text-part': "welcome to {}, please use this pin {} \
         to validate your registration".format(server, key),
      'Html-part': "<h3>welcome to {}</h3><br />please use this pin {}\
         to validate your registration".format(server, key)
    }
    result = mailjet.send.create(data=data)
    return result

from mailjet_rest import Client
from config import settings
api_key = settings.MJ_APIKEY_PUBLIC
api_secret = settings.MJ_APIKEY_PRIVATE
mailjet = Client(auth=(api_key, api_secret), version='v3')

def send_email():
    data = {
      'FromEmail': "smtpmailver@gmail.com",
      'FromName': "Your Mailjet Pilot",
      'Recipients': [
        {
          "Email": "dachirhicham@gmail.com",
          "Name": "Passenger 1"
        }
      ],
      'Subject': "Your email flight plan!",
      'Text-part': "Dear passenger, welcome to Mailjet! May the delivery force be with you!",
      'Html-part': "<h3>Dear passenger, welcome to Mailjet!</h3><br />May the delivery force be with you!"
    }
    result = mailjet.send.create(data=data)
    return result





# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
from config.settings import config

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config.TWILIO_ACCOUNT_SID
auth_token = config.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

# Phone numbers in E.164 format
twilio_number = config.TWILIO_PHONE_NUMBER     # Your Twilio phone number
destination_number = config.DESTINATION_NUMBER # The recipient's number

flask_url_outbound = config.FLASK_SERVER_URL_OUTBOUND

call = client.calls.create(
    to=destination_number,
    from_=twilio_number,
    url=flask_url_outbound  # your public Flask URL + '/outbound'

)

print(f"Call initiated. SID: {call.sid}")
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

# TwiML Bin URL (replace with your actual one)
twiml_bin_url = config.TWIML_TEST_URL

call = client.calls.create(
    to=destination_number,
    from_=twilio_number,
    url=twiml_bin_url

)

print(f"Call initiated. SID: {call.sid}")
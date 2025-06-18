# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = "AC4f2de8fb999f13ee1c63208bc71e19b5"
auth_token = "85bc684001260ed770af253f908b3a9b"
client = Client(account_sid, auth_token)

# Phone numbers in E.164 format
twilio_number = '+15393456978'     # Your Twilio phone number
destination_number = '+18582542803' # The recipient's number

# TwiML Bin URL (replace with your actual one)
twiml_bin_url = 'https://handler.twilio.com/twiml/EH9ab4b8344feafc1b52a1c0ad4aa1b56b'

call = client.calls.create(
    to=destination_number,
    from_=twilio_number,
    url=twiml_bin_url

)

print(f"Call initiated. SID: {call.sid}")
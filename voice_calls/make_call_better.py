from twilio.rest import Client
import os
import sys
from config.settings import config

# ==== TWILIO CONFIGURATION ====
# Replace these with your actual Twilio credentials
# You can find these in your Twilio Console: https://console.twilio.com/
account_sid = config.TWILIO_ACCOUNT_SID
auth_token = config.TWILIO_AUTH_TOKEN
twilio_number = config.TWILIO_PHONE_NUMBER   # Format: +1234567890

# Alternatively, use environment variables (more secure):
# account_sid = os.getenv('TWILIO_account_sid')
# auth_token = os.getenv('TWILIO_auth_token')
# twilio_number = os.getenv('twilio_number')

# ==== CALL CONFIGURATION ====
destination_number = config.DESTINATION_NUMBER  # Replace with the number you want to call
flask_url_outbound = config.FLASK_SERVER_URL_OUTBOUND

def validate_credentials():
    """Validate Twilio credentials before making the call"""
    print("🔍 Validating Twilio credentials...")
    
    if not account_sid or account_sid == 'YOUR_account_sid_HERE':
        print("❌ Error: account_sid not set or still has placeholder value")
        return False
    
    if not auth_token or auth_token == 'YOUR_auth_token_HERE':
        print("❌ Error: auth_token not set or still has placeholder value")
        return False
    
    if not twilio_number or twilio_number == 'YOUR_twilio_number':
        print("❌ Error: twilio_number not set or still has placeholder value")
        return False
    
    if not destination_number or destination_number == '+1234567890':
        print("❌ Error: destination_number not set or still has placeholder value")
        return False
    
    if not flask_url_outbound or 'your-ngrok-url' in flask_url_outbound:
        print("❌ Error: flask_url_outbound not set or still has placeholder value")
        return False
    
    # Check format
    if not account_sid.startswith('AC'):
        print(f"❌ Error: account_sid should start with 'AC', got: {account_sid[:5]}...")
        return False
    
    if len(auth_token) != 32:
        print(f"❌ Error: auth_token should be 32 characters, got: {len(auth_token)} characters")
        return False
    
    print("✅ Credentials format looks correct")
    return True

def test_twilio_connection():
    """Test Twilio connection before making a call"""
    try:
        print("🔗 Testing Twilio connection...")
        client = Client(account_sid, auth_token)
        
        # Test by fetching account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Successfully connected to Twilio account: {account.friendly_name}")
        
        # Test by listing phone numbers
        phone_numbers = client.incoming_phone_numbers.list(limit=5)
        print(f"📱 Found {len(phone_numbers)} phone number(s) in your account")
        
        for number in phone_numbers:
            print(f"   - {number.phone_number} ({number.friendly_name})")
            if number.phone_number == twilio_number:
                print("✅ Your configured phone number is valid")
                return True
        
        if not phone_numbers:
            print("❌ No phone numbers found in your account. You need to purchase a phone number first.")
            return False
        
        print(f"⚠️  Warning: Configured phone number {twilio_number} not found in your account")
        print("   Available numbers are listed above. Please update twilio_number")
        return False
        
    except Exception as e:
        print(f"❌ Twilio connection test failed: {str(e)}")
        return False

def make_call():
    """Make the outbound call"""
    try:
        print("📞 Initiating call...")
        client = Client(account_sid, auth_token)
        
        call = client.calls.create(
            to=destination_number,
            from_=twilio_number,
            url=flask_url_outbound,
            method='POST'
        )
        
        print(f"✅ Call initiated successfully!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        
        # Use the original values instead of trying to access from the call object
        print(f"   From: {twilio_number}")
        print(f"   To: {destination_number}")
        print(f"   Webhook URL: {flask_url_outbound}")
        print(f"\n🎯 Monitor your call at: https://console.twilio.com/us1/monitor/logs/calls/{call.sid}")
        
        return call
        
    except Exception as e:
        print(f"❌ Failed to make call: {str(e)}")
        return None

def main():
    print("🚀 Twilio Voice Call Initiator")
    print("=" * 50)
    
    # Step 1: Validate credentials
    if not validate_credentials():
        print("\n❌ Please fix the credential issues above and try again.")
        print("\n📋 To find your credentials:")
        print("   1. Go to https://console.twilio.com/")
        print("   2. Your Account SID and Auth Token are on the main dashboard")
        print("   3. Your phone number is under Phone Numbers > Manage > Active numbers")
        return
    
    # Step 2: Test connection
    if not test_twilio_connection():
        print("\n❌ Connection test failed. Please check your credentials and try again.")
        return
    
    # Step 3: Make the call
    print(f"\n📞 Ready to call {destination_number}")
    print(f"   Using webhook: {flask_url_outbound}")
    
    # Confirm before making call
    confirm = input("\nProceed with the call? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Call cancelled.")
        return
    
    call = make_call()
    
    if call:
        print(f"\n🎉 Success! Call is in progress.")
        print(f"🔍 You can monitor the call logs in your Twilio console.")
    else:
        print(f"\n❌ Call failed. Check the error message above.")

if __name__ == "__main__":
    main()
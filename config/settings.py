# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
    AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')
    DATABASE_URL = os.getenv('DATABASE_URL')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    DESTINATION_NUMBER = os.getenv('DESTINATION_NUMBER')
    TWIML_TEST_URL = os.getenv('TWIML_TEST_URL')
    FLASK_SERVER_URL_OUTBOUND = os.getenv('FLASK_SERVER_URL_OUTBOUND')

    @classmethod
    def validate_required_vars(cls):
        """
        Check if all important variables are set.
        This prevents your app from crashing later!
        """
        required_vars = {
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
            'TWILIO_ACCOUNT_SID': cls.TWILIO_ACCOUNT_SID,
            'TWILIO_AUTH_TOKEN': cls.TWILIO_AUTH_TOKEN,
        }
        
        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ All required environment variables are set!")

# Create a global config instance
config = Config()

# Validate when the module is imported
config.validate_required_vars()
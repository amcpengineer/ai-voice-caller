from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import logging
import os
from datetime import datetime
from config.settings import config

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='logs/voice_caller.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==== CONFIGURATION ====
# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY', config.OPENAI_API_KEY)
)

# Configuration constants
MAX_RETRIES = 3
SPEECH_TIMEOUT = 10
MAX_TOKENS = 150
TEMPERATURE = 0.3

def create_error_response(message="I'm sorry, I'm experiencing technical difficulties. Please try again later."):
    """Create a standardized error response"""
    resp = VoiceResponse()
    resp.say(message, language='en-US', voice='Polly.Joanna')
    resp.hangup()
    return Response(str(resp), mimetype='text/xml')

def log_request_info(route_name):
    """Log incoming request information"""
    logger.info(f"=== {route_name} REQUEST ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"Form data: {dict(request.form)}")
    logger.info(f"Args: {dict(request.args)}")
    logger.info(f"Remote addr: {request.remote_addr}")

# ===== OUTBOUND CALL HANDLER =====
@app.route("/outbound", methods=['GET', 'POST'])
def outbound():
    try:
        log_request_info("OUTBOUND")
        
        resp = VoiceResponse()
        gather = Gather(
            input='speech',
            timeout=SPEECH_TIMEOUT,
            language='en-US',
            action='/process_speech',
            partial_result_callback='/partial_result'  # Optional: for real-time feedback
        )
        
        welcome_message = (
            'Hi, I am the virtual assistant from Buildn 123. '
            'How can I help you with our real estate project today?'
        )
        
        gather.say(welcome_message, language='en-US', voice='Polly.Joanna')
        resp.append(gather)
        
        # If no speech detected, try again with a different message
        resp.say(
            'I didn\'t hear anything. Let me ask again.',
            language='en-US', 
            voice='Polly.Joanna'
        )
        resp.redirect('/outbound')
        
        logger.info("Outbound call initiated successfully")
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error in outbound handler: {str(e)}", exc_info=True)
        return create_error_response("I'm sorry, there was an issue starting our conversation.")

# ===== SPEECH PROCESSING AND GPT-4 INTEGRATION =====
@app.route("/process_speech", methods=['GET', 'POST'])
def process_speech():
    try:
        log_request_info("PROCESS_SPEECH")
        
        # Get speech result and confidence
        user_input = request.values.get('SpeechResult', '').strip()
        confidence = request.values.get('Confidence', 0)
        
        logger.info(f"Speech Result: '{user_input}' (Confidence: {confidence})")
        
        resp = VoiceResponse()
        
        # Check if we got valid speech input
        if not user_input:
            logger.warning("No speech input received")
            resp.say(
                'I didn\'t catch that. Could you please repeat your question more clearly?',
                language='en-US',
                voice='Polly.Joanna'
            )
            resp.redirect('/outbound')
            return Response(str(resp), mimetype='text/xml')
        
        # Check confidence level (if provided by Twilio)
        try:
            confidence_float = float(confidence)
            if confidence_float < 0.5:  # Low confidence threshold
                logger.warning(f"Low confidence speech recognition: {confidence_float}")
                resp.say(
                    'I\'m not sure I understood that correctly. Could you please repeat your question?',
                    language='en-US',
                    voice='Polly.Joanna'
                )
                resp.redirect('/outbound')
                return Response(str(resp), mimetype='text/xml')
        except (ValueError, TypeError):
            # Confidence not available or invalid, continue processing
            pass
        
        # Process with OpenAI
        answer = get_ai_response(user_input)
        
        if answer:
            logger.info(f"Successful AI response generated for input: '{user_input}'")
            resp.say(answer, language='en-US', voice='Polly.Joanna')
            
            # Optional: Ask if they need more help
            gather = Gather(
                input='speech',
                timeout=5,
                language='en-US',
                action='/process_followup'
            )
            gather.say('Is there anything else I can help you with?', language='en-US', voice='Polly.Joanna')
            resp.append(gather)
            
            # If no response, end call politely
            resp.say('Thank you for your interest in Buildn 123. Have a great day!', language='en-US', voice='Polly.Joanna')
            resp.hangup()
        else:
            logger.error("Failed to get AI response")
            return create_error_response(
                "I'm having trouble processing your request right now. "
                "Please call back in a few minutes or visit our website for immediate assistance."
            )
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error in process_speech: {str(e)}", exc_info=True)
        return create_error_response()

def get_ai_response(user_input, retry_count=0):
    """Get response from OpenAI with retry logic"""
    if retry_count >= MAX_RETRIES:
        logger.error(f"Max retries ({MAX_RETRIES}) reached for OpenAI API")
        return None
    
    system_prompt = (
        "You are a helpful AI assistant for Buildn 123, a residential real estate project in Dallas, "
        "offering modern 2- and 3-bedroom apartments starting at $180,000. "
        "Key details: Located in Dallas, modern amenities, competitive pricing, quality construction. "
        "Answer user questions clearly, briefly (under 100 words), and professionally. "
        "If asked about specific details you don't know, suggest they contact our sales team. "
        "Always maintain a friendly, helpful tone."
    )
    
    try:
        logger.info(f"Sending request to OpenAI (attempt {retry_count + 1}): '{user_input}'")
        
        # Updated API call for OpenAI v1.0+
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            timeout=30
        )
        
        answer = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response received: '{answer[:100]}...'")
        
        # Validate response
        if not answer or len(answer.strip()) == 0:
            logger.warning("Empty response from OpenAI")
            return None
            
        return answer
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Handle rate limiting
        if "rate_limit" in error_str or "rate limit" in error_str:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            return "I'm currently experiencing high demand. Please try again in a moment."
        
        # Handle authentication errors
        elif "authentication" in error_str or "unauthorized" in error_str or "api_key" in error_str:
            logger.error(f"OpenAI authentication error: {str(e)}")
            return None
        
        # Handle timeout errors
        elif "timeout" in error_str:
            logger.error(f"OpenAI timeout error: {str(e)}")
            if retry_count < MAX_RETRIES - 1:
                logger.info(f"Retrying OpenAI request after timeout (attempt {retry_count + 2})")
                return get_ai_response(user_input, retry_count + 1)
            return None
        
        # Handle other API errors with retry
        else:
            logger.error(f"OpenAI API error: {str(e)}")
            if retry_count < MAX_RETRIES - 1:
                logger.info(f"Retrying OpenAI request (attempt {retry_count + 2})")
                return get_ai_response(user_input, retry_count + 1)
            return None

# ===== FOLLOW-UP HANDLER =====
@app.route("/process_followup", methods=['GET', 'POST'])
def process_followup():
    try:
        log_request_info("PROCESS_FOLLOWUP")
        
        user_input = request.values.get('SpeechResult', '').strip().lower()
        resp = VoiceResponse()
        
        # Check for positive responses
        positive_responses = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok']
        if any(word in user_input for word in positive_responses):
            resp.redirect('/outbound')  # Start over
        else:
            resp.say('Thank you for your interest in Buildn 123. Have a great day!', language='en-US', voice='Polly.Joanna')
            resp.hangup()
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error in process_followup: {str(e)}", exc_info=True)
        return create_error_response("Thank you for calling Buildn 123. Goodbye!")

# ===== HEALTH CHECK ENDPOINT =====
@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test OpenAI API connectivity
        test_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        api_status = "healthy"
    except Exception as e:
        logger.error(f"Health check - OpenAI API issue: {str(e)}")
        api_status = "unhealthy"
    
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "openai_api": api_status
    }

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return create_error_response("I'm sorry, there was a routing error. Please try again.")

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return create_error_response()

# Remove the direct execution - let main.py handle this
if __name__ == "__main__":
    logger.info("Starting Voice Caller Application")
    logger.info(f"OpenAI API Key configured: {'Yes' if client.api_key else 'No'}")
    
    # For direct execution (fallback)
    app.run(debug=True, host='0.0.0.0', port=5000)
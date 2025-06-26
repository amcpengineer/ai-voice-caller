#!/usr/bin/env python3
"""
AI Voice Caller - Main Entry Point
This provides a unified interface to run different parts of the application.
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path to fix import issues
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_web_server(port=5000, debug=True):
    """Start the Flask web server for handling Twilio webhooks"""
    try:
        from app import app, logger
        logger.info("Starting Voice Caller Flask Application")
        logger.info(f"Server will be available at: http://localhost:{port}")
        logger.info("Webhook endpoints:")
        logger.info("  - /outbound (for outbound calls)")
        logger.info("  - /process_speech (for speech processing)")
        logger.info("  - /process_followup (for follow-up responses)")
        logger.info("  - /health (health check)")
        
        # Run server with specified parameters
        app.run(debug=debug, host='0.0.0.0', port=port)
        
    except ImportError as e:
        print(f"Error importing Flask app: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)

def make_voice_call(phone_number):
    """Make an outbound voice call"""
    try:
        from voice_calls.make_call_better import make_call
        print(f"Making call to: {phone_number}")
        
        # Check if make_call accepts parameters
        import inspect
        sig = inspect.signature(make_call)
        
        if len(sig.parameters) == 0:
            # Function takes no parameters - you may need to set phone number elsewhere
            print("Note: make_call() function doesn't accept phone number parameter.")
            print("You may need to configure the phone number in your settings or modify the function.")
            make_call()
        else:
            # Function accepts parameters
            make_call(phone_number)
        
    except ImportError as e:
        print(f"Error importing call module: {e}")
        print("Please ensure the voice_calls module is properly configured.")
        sys.exit(1)
    except TypeError as e:
        if "positional arguments" in str(e):
            print(f"Error: The make_call() function signature doesn't match expected parameters.")
            print(f"Error details: {e}")
            print("\nTo fix this, you need to either:")
            print("1. Modify make_call_better.py to accept a phone_number parameter, or")
            print("2. Set the phone number in your configuration/settings")
            sys.exit(1)
        else:
            print(f"Error making call: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Error making call: {e}")
        sys.exit(1)

def run_health_check(port=5000):
    """Check if the application is healthy"""
    try:
        import requests
        
        print(f"Checking health at http://localhost:{port}/health...")
        
        # Try to reach the health endpoint
        response = requests.get(f'http://localhost:{port}/health', timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Application is healthy!")
            print(f"Status: {health_data.get('status')}")
            print(f"OpenAI API: {health_data.get('openai_api')}")
            print(f"Timestamp: {health_data.get('timestamp')}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application. Is the server running?")
        print(f"Start the server with: python main.py --mode server --port {port}")
        return False
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install requests: pip install requests")
        return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_configuration():
    """Test that all required configurations are present"""
    try:
        from config.settings import config
        from app import client
        
        print("🔧 Configuration Test")
        print("-" * 30)
        
        # Check OpenAI API key
        api_key_present = bool(client.api_key)
        print(f"OpenAI API Key: {'✅ Present' if api_key_present else '❌ Missing'}")
        
        # Check if we can import required modules
        modules_to_check = ['flask', 'twilio', 'openai']
        for module in modules_to_check:
            try:
                __import__(module)
                print(f"{module}: ✅ Available")
            except ImportError:
                print(f"{module}: ❌ Missing")
        
        return api_key_present
        
    except Exception as e:
        print(f"Configuration test error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='AI Voice Caller - Unified Application Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode server          # Start the web server
  python main.py --mode call --phone +1234567890  # Make a call
  python main.py --mode health          # Check application health
  python main.py --mode test            # Test configuration
  
For development:
  python main.py                        # Defaults to server mode
  python main.py --port 8000            # Start server on port 8000
  python main.py --no-debug             # Start server without debug mode
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['server', 'call', 'health', 'test'], 
        default='server',
        help='Application mode (default: server)'
    )
    
    parser.add_argument(
        '--phone', 
        help='Phone number for call mode (required when mode=call)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port for web server (default: 5000)'
    )
    
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable debug mode for production'
    )
    
    args = parser.parse_args()
    
    print("🤖 AI Voice Caller")
    print("=" * 50)
    
    if args.mode == 'server':
        print(f"Mode: Web Server (Port: {args.port})")
        debug_mode = not args.no_debug
        if debug_mode:
            print("Debug mode: ON (use --no-debug for production)")
        else:
            print("Debug mode: OFF (production mode)")
        run_web_server(port=args.port, debug=debug_mode)
        
    elif args.mode == 'call':
        if not args.phone:
            print("❌ Error: Phone number is required for call mode")
            print("Usage: python main.py --mode call --phone +1234567890")
            sys.exit(1)
        
        print(f"Mode: Make Call to {args.phone}")
        make_voice_call(args.phone)
        
    elif args.mode == 'health':
        print(f"Mode: Health Check (Port: {args.port})")
        success = run_health_check(port=args.port)
        sys.exit(0 if success else 1)
        
    elif args.mode == 'test':
        print("Mode: Configuration Test")
        success = test_configuration()
        if success:
            print("\n✅ Configuration looks good!")
        else:
            print("\n❌ Configuration issues detected. Please check your setup.")
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
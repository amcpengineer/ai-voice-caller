import pytest
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check_ok(client):
    with patch('app.client') as mock_client:
        mock_chat = MagicMock()
        mock_chat.completions.create.return_value = MagicMock()
        mock_client.chat = mock_chat
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'running'
        assert data['openai_api'] == 'healthy'

def test_health_check_openai_error(client):
    with patch('app.client') as mock_client:
        mock_chat = MagicMock()
        mock_chat.completions.create.side_effect = Exception("API error")
        mock_client.chat = mock_chat
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['openai_api'] == 'unhealthy'

def test_outbound_route(client):
    response = client.post('/outbound')
    assert response.status_code == 200
    assert b'<Response>' in response.data
    assert b'How can I help you with our real estate project today?' in response.data

def test_process_speech_no_input(client):
    response = client.post('/process_speech', data={})
    assert response.status_code == 200
    assert b'I didn\'t catch that' in response.data

def test_process_speech_low_confidence(client):
    response = client.post('/process_speech', data={'SpeechResult': 'test', 'Confidence': '0.2'})
    assert response.status_code == 200
    assert b'I\'m not sure I understood that correctly' in response.data

def test_process_speech_with_ai_response(client):
    with patch('app.get_ai_response', return_value="This is an AI answer."):
        response = client.post('/process_speech', data={'SpeechResult': 'Tell me about Buildn 123', 'Confidence': '0.9'})
        assert response.status_code == 200
        assert b'This is an AI answer.' in response.data

def test_process_speech_ai_response_none(client):
    with patch('app.get_ai_response', return_value=None):
        response = client.post('/process_speech', data={'SpeechResult': 'Tell me about Buildn 123', 'Confidence': '0.9'})
        assert response.status_code == 200
        assert b'I\'m having trouble processing your request right now' in response.data

def test_process_followup_positive(client):
    response = client.post('/process_followup', data={'SpeechResult': 'yes'})
    assert response.status_code == 200
    assert b'<Redirect>' in response.data or b'<Response>' in response.data

def test_process_followup_negative(client):
    response = client.post('/process_followup', data={'SpeechResult': 'no'})
    assert response.status_code == 200
    assert b'Thank you for your interest in Buildn 123' in response.data

def test_404_handler(client):
    response = client.get('/not_a_real_route')
    assert response.status_code == 200
    assert b'routing error' in response.data

def test_500_handler(client):
    with patch('app.log_request_info', side_effect=Exception("fail")):
        response = client.post('/outbound')
        assert response.status_code == 200
        assert b'technical difficulties' in response.data
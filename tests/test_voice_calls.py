import pytest
from unittest.mock import patch, MagicMock
from voice_calls import make_call_better

def test_make_call_success():
    with patch('voice_calls.make_call_better.client') as mock_client:
        mock_calls = MagicMock()
        mock_calls.create.return_value.sid = "CA123456789"
        mock_client.calls = mock_calls
        sid = make_call_better.make_call(
            to="+1234567890",
            from_="+0987654321",
            url="http://example.com/twiml"
        )
        assert sid == "CA123456789"
        mock_calls.create.assert_called_once_with(
            to="+1234567890",
            from_="+0987654321",
            url="http://example.com/twiml"
        )

def test_make_call_raises_exception():
    with patch('voice_calls.make_call_better.client') as mock_client:
        mock_calls = MagicMock()
        mock_calls.create.side_effect = Exception("Twilio error")
        mock_client.calls = mock_calls
        with pytest.raises(Exception) as excinfo:
            make_call_better.make_call(
                to="+1234567890",
                from_="+0987654321",
                url="http://example.com/twiml"
            )
        assert "Twilio error" in str(excinfo.value)
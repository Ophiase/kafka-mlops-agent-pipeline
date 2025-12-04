from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase

from .services import ControlApiClient, ControlApiError


class ControlApiClientTests(SimpleTestCase):
	@patch("ui.services.requests.request")
	def test_state_success(self, mock_request: Mock) -> None:
		response = Mock()
		response.raise_for_status.return_value = None
		response.content = b"{}"
		response.json.return_value = {"phase": "running"}
		mock_request.return_value = response

		client = ControlApiClient("http://service")
		data = client.state()

		self.assertEqual(data["phase"], "running")
		mock_request.assert_called_once_with(
			"GET", "http://service/state", json=None, timeout=10.0
		)

	@patch("ui.services.requests.request")
	def test_request_exception_is_wrapped(self, mock_request: Mock) -> None:
		mock_request.side_effect = requests.RequestException("boom")
		client = ControlApiClient("http://service")

		with self.assertRaises(ControlApiError):
			client.start()

	@patch("ui.services.requests.request")
	def test_invalid_json_is_reported(self, mock_request: Mock) -> None:
		response = Mock()
		response.raise_for_status.return_value = None
		response.content = b"oops"
		response.json.side_effect = ValueError("bad json")
		mock_request.return_value = response

		client = ControlApiClient("http://service")

		with self.assertRaises(ControlApiError):
			client.state()

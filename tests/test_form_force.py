import unittest
from unittest.mock import patch, mock_open, MagicMock
from code.form_force import brute_force_form

class TestBruteForceForm(unittest.TestCase):

    @patch("form_force.requests.post")
    def test_brute_force_valid_credentials(self, mock_post):
        # Mock a valid response from the server
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "Valid login"
        
        with patch("builtins.open", mock_open()) as mock_file:
            brute_force_form("localhost", "/login", ["admin"], ["password123"], mock_file(), "user", "pass")
            # Ensure the post request was made correctly
            mock_post.assert_called_with("http://localhost/login", data={"user": "admin", "pass": "password123"})
            # Ensure valid credentials were written to the file
            mock_file().write.assert_called_once_with("admin:password123\n")

if __name__ == "__main__":
    unittest.main()

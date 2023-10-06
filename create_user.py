import requests

# URL for user registration
register_url = 'http://127.0.0.1:5000/register'

# User registration data (username and password)
user_data = {
    'username': 'new_username',
    'password': 'new_password'
}

# Send a POST request to register a new user
register_response = requests.post(register_url, json=user_data)

# Print the response from the registration endpoint
if register_response.status_code == 201:
    print("User registered successfully.")
else:
    print("User registration failed with status code:", register_response.status_code)

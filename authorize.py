import requests

# URL for user login
login_url = 'http://127.0.0.1:5000/login'

# User login data (username and password)
user_data = {
    'username': 'example_username',
    'password': 'example_password'
}

# Send a POST request to login
login_response = requests.post(login_url, auth=(user_data['username'], user_data['password']))

if login_response.status_code == 200:
    # Extract the token from the login response
    token = login_response.json()['token']
    print("Token:", token)

    # Use the token for the protected route request
    protected_url = 'http://127.0.0.1:5000/protected'
    headers = {
        'Authorization': 'Bearer ' + token
    }

    # Send a GET request to the protected endpoint
    protected_response = requests.get(protected_url, headers=headers)


    # Print the response from the protected endpoint
    if protected_response.status_code == 200:
        print("Protected endpoint response:", protected_response.json())
    else:
        print("Request to protected endpoint failed with status code:", protected_response.status_code)
else:
    print("Login request failed with status code:", login_response.status_code)

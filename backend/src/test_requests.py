import requests

# Base URL of your Flask application
BASE_URL = "http://127.0.0.1:5000"


def register_user(username, password):
    """Registers a new user on the Flask backend.

    Expects username to be alphanumeric and password to meet complexity rules:
    - Min 5 characters
    - 1 uppercase, 1 lowercase
    - 1 non-letter character
    """
    url = f"{BASE_URL}/api/auth/register"
    payload = {"username": username, "password": password}

    print(f"Attempting to register user: '{username}'...")
    try:
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            print(" -> Success: User registered successfully!")
            print(f" -> Response: {response.json()}\n")
            return True
        else:
            print(f" -> Failed (Status Code: {response.status_code})")
            print(f" -> Response: {response.json()}\n")
            return False
    except requests.exceptions.ConnectionError:
        print(" -> Error: Could not connect to the server. Is app.py running?\n")
        return False


s = requests.Session()
res = s.post(f"{BASE_URL}/api/auth/login", json={'username': 'emma', 'password': '123Pass'})
print(res.text)
res = s.get(f"{BASE_URL}/api/trade?ticker=mane")
print(res.text)
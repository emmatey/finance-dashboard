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


def get_scoreboard():
    """Retrieves the rankings for all users from the scoreboard route."""
    url = f"{BASE_URL}/api/scoreboard"

    print("Fetching global scoreboard rankings...")
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(" -> Success!")
            print(" --- CURRENT LEADERBOARD ---")

            # Iterate through and format the user scoreboard items nicely
            for user in data.get("data", []):
                print(
                    f"Rank #{user['rank']}: {user['username']} | "
                    f"Total Value: ${user['grand_total']:,.2f} "
                    f"(Cash: ${user['cash_balance']:,.2f}, Portfolio: ${user['portfolio_value']:,.2f})"
                )
            print(" ---------------------------")
        else:
            print(f" -> Failed (Status Code: {response.status_code})")
            print(f" -> Response: {response.json()}\n")
    except requests.exceptions.ConnectionError:
        print(" -> Error: Could not connect to the server. Is app.py running?\n")


if __name__ == "__main__":
    # 1. Try registering a brand new user (Make sure password meets your constraints!)
    # Change the username if running this multiple times to avoid a 409 conflict
    new_username = "TraderJoe42"
    secure_password = "Password1!"

    register_user(username=new_username, password=secure_password)

    # 2. Query the scoreboard route (This is a public GET route, no login required)
    get_scoreboard()
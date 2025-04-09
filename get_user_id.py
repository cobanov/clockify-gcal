import requests


def get_user_id(api_key):
    url = "https://api.clockify.me/api/v1/user"
    headers = {"X-Api-Key": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        user_data = response.json()
        return user_data.get("id")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user ID: {e}")
        return None


if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual Clockify API key
    api_key = input("Enter your Clockify API key: ")
    user_id = get_user_id(api_key)
    if user_id:
        print(f"Your Clockify User ID is: {user_id}")
    else:
        print("Failed to retrieve user ID")

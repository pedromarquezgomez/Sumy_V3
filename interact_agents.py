import requests
import json

BASE_URL = "http://localhost:8080"

def send_message_to_agent(app_name: str, user_id: str, session_id: str, message: str):
    """
    Sends a message to the specified agent and prints the response.
    """
    url = f"{BASE_URL}/run"
    headers = {"Content-Type": "application/json"}
    payload = {
        "appName": app_name,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {
            "parts": [
                {"text": message}
            ],
            "role": "user"
        },
        "streaming": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Response from agent:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the agent API at {BASE_URL}. Is the FastAPI application running?")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response content: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    # Replace with your desired app_name, user_id, session_id, and message
    # You can find app_name by calling the /list-apps endpoint if available,
    # or by checking your application's configuration.
    
    # Example for a culinary agent
    print("Sending message to culinary agent...")
    send_message_to_agent(
        app_name="culinary",  # Example app name
        user_id="test_user_123",
        session_id="test_session_456",
        message="What is a good recipe for pasta carbonara?"
    )

    print("\nSending another message to a nutrition agent...")
    send_message_to_agent(
        app_name="nutrition",  # Example app name
        user_id="test_user_123",
        session_id="test_session_789",
        message="How many calories are in an apple?"
    )

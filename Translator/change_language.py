import requests
import json

#===========================================================
# INITIALIATION
#===========================================================
user_settings_file = open("../../../../User-Settings.json", encoding="utf-8")
user_settings_data = json.load(user_settings_file)

port = user_settings_data["Translation_API_Server"]["Google"]["HTTP_port_number"]
host = '0.0.0.0'

def request_server(api_url, message, content):
    """
    Calls the 'translate sentences' API and returns the response.
    
    Parameters:
    - api_url (str): The full URL of the API endpoint (e.g., 'http://127.0.0.1:5000/').
    - content (str): The content to be translated.
    
    Returns:
    - dict: The JSON response from the API.
    """
    try:
        # Prepare the payload
        payload = {
            "message": message,
            "content": content
        }
        
        # Make the POST request
        response = requests.post(api_url, json=payload)
        
        # Check if the response is successful
        response.raise_for_status()
        
        # Return the parsed JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the API call
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # print(request_server(f"http://localhost:14175/", "change input language", "Korean"))
    print(request_server(f"http://localhost:{port}/", "change input language", "Korean"))

